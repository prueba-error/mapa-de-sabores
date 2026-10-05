# Mapa de Sabores - Especificación Técnica Detallada (SPEC.md)

> Este documento es el anexo técnico de **[PROYECTO.md](./PROYECTO.md)**. Para el contexto académico, las decisiones de diseño y el alcance del proyecto, ver ese documento primero.

## 1. Modelo de Datos y Estrategia de Grafos (PostgreSQL)

### 1.1 Esquema Relacional de Base de Datos (DDL)

```sql
-- 1. Tabla de Categorías de Ingredientes
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- ej: Frutas, Verduras, Hierbas, Carnes, Lácteos
    color_code VARCHAR(7) NOT NULL   -- Hex color para el grafo (#FF5733)
);

-- 2. Tabla de Ingredientes
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    flavor_profile JSONB DEFAULT '{}'::jsonb, -- seis ejes fijos (0.00-1.00): sweet, sour, salty, bitter, umami, aromatic
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Afinidad de Maridaje (Grafo de Aristas con Provenance)
CREATE TABLE flavor_pairings (
    id SERIAL PRIMARY KEY,
    ingredient_a_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    ingredient_b_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    affinity_score NUMERIC(3,2) NOT NULL CHECK (affinity_score BETWEEN 0.00 AND 1.00),
    ai_rationale VARCHAR(300), -- Explicación prediseñada acotada a máx 300 caracteres
    source_type VARCHAR(30) DEFAULT 'llm_synthesis', -- 'llm_synthesis', 'manual_review'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_ordered_pair CHECK (ingredient_a_id < ingredient_b_id),
    CONSTRAINT uq_ingredient_pair UNIQUE (ingredient_a_id, ingredient_b_id),
    CONSTRAINT chk_rationale_len CHECK (length(ai_rationale) <= 300)
);

-- La búsqueda por ingredient_a_id la cubre el índice compuesto que crea uq_ingredient_pair (a, b).
CREATE INDEX idx_pairings_b ON flavor_pairings(ingredient_b_id);
CREATE INDEX idx_pairings_score ON flavor_pairings(affinity_score DESC);

-- 4. Usuarios y Favoritos
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Una combinación favorita es un conjunto de 2 a 10 ingredientes (no un conjunto de pares):
-- así se conserva la identidad del grupo aunque falten pares con dato.
CREATE TABLE favorite_combinations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    ingredient_key VARCHAR(100) NOT NULL, -- ids ordenados y unidos, ej: '12-45-88' (evita duplicados)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_combination UNIQUE (user_id, ingredient_key)
);

CREATE TABLE favorite_combination_items (
    combination_id INT NOT NULL REFERENCES favorite_combinations(id) ON DELETE CASCADE,
    ingredient_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    PRIMARY KEY (combination_id, ingredient_id)
);

-- 5. Cola de Revisión para Curación Manual de Pares Dudosos
CREATE TABLE pairing_review_queue (
    id SERIAL PRIMARY KEY,
    ingredient_a_id INT NOT NULL REFERENCES ingredients(id),
    ingredient_b_id INT NOT NULL REFERENCES ingredients(id),
    suggested_score NUMERIC(3,2) NOT NULL,
    ai_rationale VARCHAR(300),
    flag_reason VARCHAR(100) NOT NULL, -- 'forbidden_antagonistic_pair', 'random_audit'
    status VARCHAR(20) DEFAULT 'pending_review', -- 'pending_review', 'approved', 'rejected'
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_review_queue_status ON pairing_review_queue(status);
```

### 1.2 Lógica de Consulta Bidireccional

Dado que un par (ej. _Tomate_, _Albahaca_) es equivalente a (_Albahaca_, _Tomate_), la restricción `ingredient_a_id < ingredient_b_id` evita duplicados. Para obtener todas las afinidades de un ingrediente `:ingredient_id`:

```sql
SELECT
    CASE WHEN p.ingredient_a_id = :ingredient_id THEN i2.id ELSE i1.id END AS neighbor_id,
    CASE WHEN p.ingredient_a_id = :ingredient_id THEN i2.name ELSE i1.name END AS neighbor_name,
    p.affinity_score,
    p.ai_rationale
FROM flavor_pairings p
JOIN ingredients i1 ON p.ingredient_a_id = i1.id
JOIN ingredients i2 ON p.ingredient_b_id = i2.id
WHERE p.ingredient_a_id = :ingredient_id OR p.ingredient_b_id = :ingredient_id
```

### 1.3 Estrategia de Migraciones con Alembic

* **Control de Versiones:** cambios DDL registrados en `backend/alembic/versions/` con hashes secuenciales.
* **Ejecución:** en el arranque del backend se invoca `alembic upgrade head`.
* **Rollback:** métodos explícitos `upgrade()` y `downgrade()` por migración.

---

## 2. Pipeline Offline y Origen del Dataset de Sabores

### 2.1 Fuentes Prácticas de Información

1. **La IA como Sintetizador de Conocimiento (Método Principal):** el script `scripts/seed_flavor_network.py` consulta en lote a un LLM mediante solicitudes estructuradas (JSON Mode con Pydantic), evaluando pares de ingredientes y generando `affinity_score` + `ai_rationale`.
2. **Matriz de Incompatibilidad Conocida:** listado curado de ~50 pares antagónicos (ej. _Pescado Blanco + Dulce de Leche_), usado como regla de alerta durante la validación.

### 2.2 Fases del Pipeline

1. **Semilla de Ingredientes:** JSON/CSV con ~200-250 ingredientes clasificados por categoría.
2. **Perfiles Sensoriales:** el LLM genera el `flavor_profile` de cada ingrediente sobre seis ejes fijos (`sweet`, `sour`, `salty`, `bitter`, `umami`, `aromatic`), con valores de 0.00 a 1.00. Pydantic exige los seis ejes y el rango; el resultado se persiste en `ingredients.flavor_profile`. Sin este paso, la Ficha (Vista 2) y la tabla comparativa no tendrían datos.
3. **Selección de Pares Candidatos:** no se evalúan los ~31.000 pares posibles. Por cada ingrediente se arma una lista de ~10-12 candidatos: la mitad sugerida por el LLM como afines y la otra mitad muestreada al azar entre categorías distintas (esto garantiza la presencia de pares débiles y neutros), más los pares de la matriz de antagónicos (Sección 2.1.2). Los pares se deduplican con la forma ordenada `a < b`.
4. **Generación Automatizada:** ejecución en lotes (una llamada por ingrediente con su lista de candidatos), con flag `--dry-run` para validar prompts sin escribir en la base ni gastar créditos de API.
5. **Validación Automática:** cada par generado se valida contra:
   * rango de score (0.00–1.00) y estructura JSON (Pydantic);
   * descarte directo de pares con score < 0.15 (ruido sin valor informativo). Los pares débiles entre 0.15 y 0.45 **se conservan a propósito**: son los que alimentan las aristas rojas y el modo "Peores";
   * la matriz de pares antagónicos (Sección 2.1.2).
6. **Enrutamiento:** el descarte de la fase 5 se aplica primero; luego:
   * si el par está en la matriz de antagónicos y su score es > 0.35, se inserta en `pairing_review_queue` con `flag_reason = 'forbidden_antagonistic_pair'` y estado `pending_review`;
   * una muestra aleatoria del 5-10 % de los pares restantes se inserta en la misma cola con `flag_reason = 'random_audit'`, para estimar la tasa de error del LLM;
   * el resto se inserta directamente en `flavor_pairings` con `source_type = 'llm_synthesis'`.
7. **Curación Manual:** el alumno revisa la cola con `scripts/curate.py --list` y decide cada caso:
   ```bash
   ./scripts/curate.py --approve 23   # copia el par a flavor_pairings, source_type = 'manual_review'
   ./scripts/curate.py --reject 24    # marca el par como rejected, nunca llega al grafo
   ./scripts/curate.py --stats        # tasa de aprobados/rechazados, desglosada por flag_reason
   ```
   La tasa de rechazo de los pares `random_audit` se informa en la memoria como medida de calidad del dataset.
8. **Snapshot Previo:** `./scripts/backup.sh backup` (ver `PLAN.md`, Sección 5.3) antes de cada corrida masiva, para poder revertir.

### 2.3 Prompt Estructurado (JSON Mode)

> _"Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. Evalúa la afinidad organoléptica entre [Ingrediente A] y [Ingrediente B]. Responde estrictamente en JSON con la siguiente estructura: `{"affinity_score": float (0.00 a 1.00), "ai_rationale": string (máximo 250 caracteres en español explicativo)}`."_

> Para la evaluación en lote (fase 4) la misma consigna se aplica a una lista de candidatos y la respuesta es un arreglo JSON de objetos `{"ingredient_b": ..., "affinity_score": ..., "ai_rationale": ...}`, validado con Pydantic. El prompt de perfiles (fase 2) es análogo y devuelve `{"sweet": float, "sour": float, "salty": float, "bitter": float, "umami": float, "aromatic": float}`.

### 2.4 Métricas de Aceptación

* Cobertura de al menos 80% de los ingredientes con 4 o más conexiones tras la curación.
* 100% de consistencia sintáctica (JSON válido) en los pares aceptados.
* 100% de los ingredientes con los seis ejes de `flavor_profile` completos.
* Al menos 15 % de los pares aceptados con `affinity_score < 0.45`, para que el modo "Peores" y las aristas rojas tengan contenido real.
* Informe de auditoría: tasa de rechazo/corrección sobre la muestra aleatoria (`random_audit`).
* Cola de revisión vaciada (sin pares en `pending_review`) antes de considerar el dataset "cerrado" para una demo.

---

## 3. Especificación de la API REST (FastAPI)

### 3.1 Autenticación (`/api/v1/auth`)
* `POST /api/v1/auth/register` — registro de nuevo usuario.
* `POST /api/v1/auth/login` — autenticación y retorno de JWT de sesión (Bearer).
* `GET /api/v1/auth/me` — perfil del usuario autenticado.

### 3.2 Red y Grafo (`/api/v1`)
* `GET /api/v1/graph` — subgrafo paginado para `react-force-graph` (`limit` = número máximo de **aristas**, default 50, max 100; los nodos son los extremos de esas aristas; `offset`; `sort=best|worst|all` para priorizar mayor o menor afinidad; `min_affinity` tiene default 0.50 con `sort=best` y 0.00 con `sort=worst|all`, para que las aristas débiles sean visibles).
* `GET /api/v1/ingredients` — lista paginada con filtro de búsqueda por nombre.
* `GET /api/v1/ingredients/{id}` — detalle del ingrediente, incluyendo `flavor_profile` (JSONB con ejes dulce/ácido/salado/amargo/umami/aromático, etc.).
* `GET /api/v1/ingredients/{id}/pairings` — vecinos directos y sus afinidades; acepta `sort=best|worst` (por defecto `best`) y `limit` para separar el ranking de mejores y peores combinaciones sin lógica adicional en el backend, solo ordenamiento sobre `flavor_pairings.affinity_score`.
* `POST /api/v1/pairings/evaluate` — recibe una lista de 2 a 10 `ingredient_id`, devuelve:
  * `synergy_score` (0–100): promedio simple de `affinity_score` sobre los pares del grupo **que tienen dato** (de los `N*(N-1)/2` pares posibles), escalado a porcentaje; `null` si ningún par tiene dato;
  * `coverage`: `{"pairs_with_data": 4, "pairs_total": 6}`; la UI lo muestra como "4 de 6 pares con dato", porque el dataset es disperso (~4 % de los pares posibles) y el score no debe presentarse como más firme de lo que es;
  * `pairwise_matrix`: afinidad cruzada NxN, con `null` en las celdas sin dato;
  * `clashing_ingredients`: solo para N ≥ 3; ingredientes cuya afinidad promedio contra el resto del grupo (calculada únicamente sobre sus pares con dato) es menor a 45%. Un ingrediente sin ningún par con dato no participa. El mínimo de esos promedios define el "ingrediente discordante" principal. Para N = 2 la lista es vacía (ambos tendrían el mismo promedio).

#### 3.2.1 (Opcional / Stretch Goal) Sugerencias para Expandir una Combinación

> Ver `PROYECTO.md`, Sección 9, ítem 4. No forma parte del *Definition of Done* del Sprint 4 — se implementa solo si sobra tiempo, y estas dos decisiones ya quedan resueltas de antemano para no tener que definirlas sobre la marcha.

* `GET /api/v1/pairings/suggest-additions?ingredient_ids=12,45,88&mode=synergy|contrast` — dado el grupo de ingredientes ya seleccionado en el Laboratorio, devuelve candidatos para sumar, ordenados según `mode`.

**Decisión 1 — Regla de cobertura mínima (el dataset es disperso):** con ~200-250 ingredientes y ~1.000-1.500 pares cargados, la mayoría de los candidatos no van a tener afinidad conocida contra *todos* los ingredientes del grupo. Un candidato solo entra al ranking si tiene `affinity_score` conocido contra al menos el 50% de los ingredientes seleccionados (redondeando hacia arriba, ej. 2 de 3), promediando únicamente sobre los pares que sí existen. Los candidatos que no alcanzan ese mínimo de cobertura se excluyen del todo, en vez de mostrarse con una afinidad parcial engañosa.

**Decisión 2 — Definición de cada modo:**
* `mode=synergy` ("Para aumentar sinergia"): candidatos ordenados por promedio de afinidad descendente, mostrando el Top 5 con promedio > 0.75.
* `mode=contrast` ("Para experimentar"): candidatos con promedio de afinidad en la banda 0.35–0.55 (ligera afinidad, ni claramente compatible ni antagónico), ordenados de mayor a menor dentro de esa banda.

Ambas reglas reutilizan `flavor_pairings.affinity_score` sin necesidad de una tabla o campo nuevo.

### 3.3 Inteligencia Artificial (`/api/v1/ai`)
* `POST /api/v1/ai/explain-pairing` — genera (o recupera de fallback) una explicación en prosa para un par o grupo de ingredientes. La respuesta incluye `source: "llm" | "stored" | "generic"`. Fallbacks: para un par con dato, su `ai_rationale` guardado (`stored`); para un grupo de más de 2, los `ai_rationale` de los pares mejor y peor puntuados (`stored`); si no hay ningún par con dato, un mensaje genérico (`generic`).
* `POST /api/v1/ai/suggest-replacement` — sugiere un reemplazo para el ingrediente discordante detectado por `/pairings/evaluate`. No existe texto guardado equivalente, por lo que su fallback es un mensaje genérico (`source: "generic"`).

### 3.4 Favoritos (`/api/v1/users/me/favorites`)
* `GET /api/v1/users/me/favorites` — combinaciones favoritas del usuario autenticado; cada una con `id`, `name`, `ingredient_ids` y `created_at`.
* `POST /api/v1/users/me/favorites` — guarda una combinación. Body: `{"name": "opcional", "ingredient_ids": [12, 45, 88]}` (2 a 10 ids). Si el mismo conjunto de ingredientes ya existe para ese usuario, responde `409`.
* `DELETE /api/v1/users/me/favorites/{id}` — elimina una combinación favorita propia.

### 3.5 Curación (uso interno, no expuesto al usuario final)
* Gestión de `pairing_review_queue` vía `scripts/curate.py` (CLI local), no vía endpoint HTTP, dado que el único rol de curación es ejercido por el propio alumno (ver `PROYECTO.md`, Sección 4).

### 3.6 Ejemplos de Contrato (Request/Response)

Para los tres endpoints con lógica no trivial, de forma que no haya que inferir nombres de campos ni el formato de los casos sin dato:

**`POST /api/v1/pairings/evaluate`** — grupo de 3 ingredientes donde Albahaca-Chocolate no tiene dato:

```json
// Request
{ "ingredient_ids": [12, 45, 88] }

// Response (12 = Tomate, 45 = Albahaca, 88 = Chocolate)
{
  "synergy_score": 53,
  "coverage": { "pairs_with_data": 2, "pairs_total": 3 },
  "pairwise_matrix": [
    [null, 0.94, 0.12],
    [0.94, null, null],
    [0.12, null, null]
  ],
  "clashing_ingredients": [
    { "ingredient_id": 88, "avg_affinity": 0.12 }
  ]
}
```

**`GET /api/v1/graph?sort=best&limit=2`**:

```json
{
  "nodes": [
    { "id": 12, "name": "Tomate", "category": "Verduras" },
    { "id": 45, "name": "Albahaca", "category": "Hierbas" }
  ],
  "edges": [
    { "ingredient_a_id": 12, "ingredient_b_id": 45, "affinity_score": 0.94 }
  ]
}
```

**`POST /api/v1/ai/explain-pairing`**:

```json
// Request
{ "ingredient_ids": [12, 45] }

// Response
{
  "explanation": "El tomate y la albahaca comparten notas frescas y aromáticas que se potencian mutuamente, un maridaje clásico de la cocina mediterránea.",
  "source": "llm"
}
```

---

## 4. Seguridad, Autenticación y Resiliencia Operativa

### 4.1 Hardening de Seguridad
1. **Hashing de Contraseñas:** `argon2-cffi` con Argon2id (o `bcrypt` costo 12). Se evita `passlib` por su falta de mantenimiento reciente.
2. **Tokens JWT de Sesión:** `access_token` JWT de sesión única (expiración 7 días), enviado vía header `Authorization: Bearer <token>`. Validación criptográfica en FastAPI sin consultas de revocación a base de datos.
3. **Control de Tasa (`slowapi`):** rate limiting de 60 req/min por IP anónima y 120 req/min para llamadas autenticadas.
4. **Token en el Cliente (riesgo XSS):** el JWT se guarda en `localStorage` por simplicidad, lo que lo expone a XSS. Mitigaciones: CSP estricta, sin `dangerouslySetInnerHTML` y salida del LLM tratada siempre como texto plano, nunca como HTML.
5. **CORS:** `CORSMiddleware` de FastAPI habilitado solo para los orígenes listados en `CORS_ORIGINS` (`.env`, por defecto `http://localhost:5173`), con `allow_credentials=True` para que el header `Authorization` llegue en las requests del frontend. En producción, `CORS_ORIGINS` se actualiza para incluir el dominio real; nunca se usa `allow_origins=["*"]` junto con `allow_credentials=True` (lo rechaza el propio navegador).

### 4.2 Resiliencia del Servicio de IA
1. **Presupuesto Total de Tiempo:** 8.0 segundos por solicitud (`LLM_TIMEOUT_SECONDS`), compartido entre el reintento y el cambio de proveedor. Cada intento usa el tiempo restante y no se inicia uno nuevo si no queda presupuesto.
2. **Reintentos:** máximo 1 reintento en errores 5xx, solo si queda presupuesto.
3. **Jerarquía de Fallback:** Gemini (modelo Flash vigente, `GEMINI_MODEL`) → OpenAI (modelo mini vigente, `OPENAI_MODEL`) → fallback local: `ai_rationale` guardado o mensaje genérico. Los IDs de modelo se configuran por entorno para no depender de versiones retiradas; se verifican contra la documentación del proveedor.
4. **Contrato Honesto:** el endpoint siempre responde (una caída del proveedor nunca produce un 5xx), pero no garantiza texto generado: el campo `source` le indica a la UI si el texto es en vivo, guardado o genérico, y el frontend muestra estado de carga y el origen.

---

## 5. Diseño Frontend (React / Vite)

Ver la arquitectura de 3 Vistas Principales (Explorar / Ficha / Laboratorio) y el diagrama en **[PROYECTO.md, Sección 5](./PROYECTO.md#5-experiencia-de-usuario-y-diseño-frontend)**.

Notas técnicas adicionales de implementación:
* **Arquitectura de 3 Vistas:** Enrutamiento modular por pestañas/rutas en React (`/explore`, `/ingredient/:id`, `/lab`).
* **Estado Global Compartido (Context API):** `LabContext` gestiona los ingredientes seleccionados (mesa de chips del Laboratorio) permitiendo la acción *"Agregar al Laboratorio"* de forma transparente desde los nodos del Grafo en la Vista 1 y desde la Ficha en la Vista 2.
* **Motor de Grafo:** `react-force-graph-2d` sobre HTML5 Canvas, target de 60 FPS / < 16ms por recálculo.
* **Colores de Arista:** verde (`affinity_score > 0.75`), amarillo (`0.45–0.75`), rojo punteado (`< 0.45`).
* **Mapeo de Filtros:** El selector **Mejores / Todas / Peores** mapea a `sort` de `GET /api/v1/graph` (carga inicial global, `limit=50` aristas) y de `GET /api/v1/ingredients/{id}/pairings` (nodo activo). El slider de cantidad (5–20) mapea a `limit` de este segundo endpoint, es decir, cuántos vecinos del nodo activo se muestran.
* **Botón "Explorar Extremos":** Consume `GET /api/v1/ingredients/{id}/pairings` con `sort=best&limit=1` y `sort=worst&limit=1`.
* **Tabla Comparativa de Perfiles (Vista 2):** Se construye al seleccionar una arista específica enfrentando los JSONB de `flavor_profile` de ambos ingredientes. Los valores numéricos se muestran como etiquetas (Bajo < 0.34, Medio 0.34–0.66, Alto > 0.66).
* **Mesa del Laboratorio (Vista 3):** Renderizado de chips reactivos. Al modificar los chips se invoca en tiempo real `POST /api/v1/pairings/evaluate`, mostrando el indicador `coverage` y las celdas sin dato como "sin dato".

---

## 6. Estrategia de Pruebas (TDD)

* **Backend:** `pytest` + `pytest-asyncio` + `httpx`, con cobertura concentrada en lógica de negocio crítica: cálculo de sinergia NxN (incluidos pares sin dato, cobertura y el caso N=2), emisión/validación de JWT, favoritos por conjunto de ingredientes y el flujo de aprobación/rechazo de `pairing_review_queue`.
* **Frontend:** `Vitest` + `React Testing Library` + `MSW` para componentes del grafo, la ficha de ingrediente y el laboratorio de combinaciones.
* **Ejecución:** local, vía `pytest` y `npm run test:run` antes de cada entrega de sprint. La automatización en un pipeline de CI/CD queda planteada como trabajo futuro (ver `PROYECTO.md`, Sección 9).
