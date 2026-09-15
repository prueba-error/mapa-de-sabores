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
    flavor_profile JSONB DEFAULT '{}'::jsonb, -- ej: {"sweet": 0.2, "umami": 0.8}
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
    confidence_score NUMERIC(3,2) DEFAULT 0.85 CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_ordered_pair CHECK (ingredient_a_id < ingredient_b_id),
    CONSTRAINT uq_ingredient_pair UNIQUE (ingredient_a_id, ingredient_b_id),
    CONSTRAINT chk_rationale_len CHECK (length(ai_rationale) <= 300)
);

CREATE INDEX idx_pairings_a ON flavor_pairings(ingredient_a_id);
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

CREATE TABLE user_favorite_pairings (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    pairing_id INT REFERENCES flavor_pairings(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, pairing_id)
);

-- 5. Cola de Revisión para Curación Manual de Pares Dudosos
CREATE TABLE pairing_review_queue (
    id SERIAL PRIMARY KEY,
    ingredient_a_id INT NOT NULL REFERENCES ingredients(id),
    ingredient_b_id INT NOT NULL REFERENCES ingredients(id),
    suggested_score NUMERIC(3,2) NOT NULL,
    ai_rationale VARCHAR(300),
    flag_reason VARCHAR(100) NOT NULL, -- ej: 'forbidden_antagonistic_pair', 'score_out_of_expected_range'
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

1. **Semilla de Ingredientes:** JSON/CSV con ~250 ingredientes clasificados por categoría.
2. **Generación Automatizada:** ejecución en lotes, con flag `--dry-run` para validar prompts sin escribir en la base ni gastar créditos de API.
3. **Validación Automática:** cada par generado se valida contra:
   * rango de score (0.00–1.00) y estructura JSON (Pydantic);
   * la matriz de pares antagónicos (Sección 2.1.2);
   * exclusión directa de pares con score < 0.40 (se descartan, no se guardan como relación débil).
4. **Enrutamiento:** si un par no dispara ninguna alerta, se inserta directamente en `flavor_pairings` con `source_type = 'llm_synthesis'`. Si dispara una alerta (por ejemplo, aparece en la matriz de antagónicos con score > 0.35), se inserta en `pairing_review_queue` con el `flag_reason` correspondiente y estado `pending_review`.
5. **Curación Manual:** el alumno revisa la cola con `scripts/curate.py --list` y decide cada caso:
   ```bash
   ./scripts/curate.py --approve 23   # copia el par a flavor_pairings, source_type = 'manual_review'
   ./scripts/curate.py --reject 24    # marca el par como rejected, nunca llega al grafo
   ```
6. **Snapshot Previo:** `pg_dump -U postgres -d mapa_sabores -f backups/pre_seed_snapshot.sql` antes de cada corrida masiva, para poder revertir.

### 2.3 Prompt Estructurado (JSON Mode)

> _"Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. Evalúa la afinidad organoléptica entre [Ingrediente A] y [Ingrediente B]. Responde estrictamente en JSON con la siguiente estructura: `{"affinity_score": float (0.00 a 1.00), "ai_rationale": string (máximo 250 caracteres en español explicativo)}`."_

### 2.4 Métricas de Aceptación

* Cobertura de al menos 80% de los ingredientes con 4 o más conexiones tras la curación.
* 100% de consistencia sintáctica (JSON válido) en los pares aceptados.
* Cola de revisión vaciada (sin pares en `pending_review`) antes de considerar el dataset "cerrado" para una demo.

---

## 3. Especificación de la API REST (FastAPI)

### 3.1 Autenticación (`/api/v1/auth`)
* `POST /api/v1/auth/register` — registro de nuevo usuario.
* `POST /api/v1/auth/login` — autenticación y retorno de JWT de sesión (Bearer).
* `GET /api/v1/auth/me` — perfil del usuario autenticado.

### 3.2 Red y Grafo (`/api/v1`)
* `GET /api/v1/graph` — subgrafo paginado para `react-force-graph` (`limit` default 50, max 100, `offset`, `min_affinity` default 0.50).
* `GET /api/v1/ingredients` — lista paginada con filtro de búsqueda por nombre.
* `GET /api/v1/ingredients/{id}/pairings` — vecinos directos (Top-N) y sus afinidades.
* `POST /api/v1/pairings/evaluate` — recibe una lista de 2 a 10 `ingredient_id`, devuelve:
  * `synergy_score` (0–100) e índice global de sinergia;
  * `pairwise_matrix`: afinidad cruzada NxN;
  * `clashing_ingredients`: lista de ingredientes discordantes (afinidad promedio con el resto del grupo < 45%).

### 3.3 Inteligencia Artificial (`/api/v1/ai`)
* `POST /api/v1/ai/explain-pairing` — genera (o recupera de fallback) una explicación en prosa para un par o grupo de ingredientes.
* `POST /api/v1/ai/suggest-replacement` — sugiere un reemplazo para el ingrediente discordante detectado por `/pairings/evaluate`.

### 3.4 Favoritos (`/api/v1/users/me/favorites`)
* `GET /api/v1/users/me/favorites` — combinaciones favoritas guardadas por el usuario autenticado.
* `POST /api/v1/users/me/favorites` — guarda una combinación (lista de `pairing_id`) como favorita.

### 3.5 Curación (uso interno, no expuesto al usuario final)
* Gestión de `pairing_review_queue` vía `scripts/curate.py` (CLI local), no vía endpoint HTTP, dado que el único rol de curación es ejercido por el propio alumno (ver `PROYECTO.md`, Sección 2.3).

---

## 4. Seguridad, Autenticación y Resiliencia Operativa

### 4.1 Hardening de Seguridad
1. **Hashing de Contraseñas:** Passlib con Argon2id (o `bcrypt` costo 12).
2. **Tokens JWT de Sesión:** `access_token` JWT de sesión única (expiración 7 días), enviado vía header `Authorization: Bearer <token>`. Validación criptográfica en FastAPI sin consultas de revocación a base de datos.
3. **Control de Tasa (`slowapi`):** rate limiting de 60 req/min por IP anónima y 120 req/min para llamadas autenticadas.

### 4.2 Resiliencia del Servicio de IA
1. **Timeout Estricto:** 3.0 segundos en llamadas HTTP a LLMs cloud.
2. **Reintentos:** máximo 1 reintento en errores 5xx.
3. **Jerarquía de Fallback:** Gemini 1.5 Flash → OpenAI GPT-4o-mini → fallback local al `ai_rationale` guardado en `flavor_pairings` (100% disponibilidad garantizada).

---

## 5. Diseño Frontend (React / Vite)

Ver el diagrama de layout y la lógica progresiva del grafo en **[PROYECTO.md, Sección 5](./PROYECTO.md#5-experiencia-de-usuario-y-diseño-frontend)**. Este documento no repite ese contenido.

Notas técnicas adicionales:
* Motor de grafo: `react-force-graph-2d` sobre HTML5 Canvas, target de 60 FPS / < 16ms por recálculo.
* Estado global de selección de ingredientes: Context API (sin librería externa de estado).
* Colores de arista: verde (`affinity_score > 0.75`), amarillo (`0.45–0.75`), rojo punteado (`< 0.45`).

---

## 6. Estrategia de Pruebas (TDD)

* **Backend:** `pytest` + `pytest-asyncio` + `httpx`, con cobertura concentrada en lógica de negocio crítica: cálculo de sinergia NxN, emisión/validación de JWT, y el flujo de aprobación/rechazo de `pairing_review_queue`.
* **Frontend:** `Vitest` + `React Testing Library` + `MSW` para componentes del grafo y del panel lateral.
* **Ejecución:** local, vía `pytest` y `npm run test:run` antes de cada entrega de sprint. La automatización en un pipeline de CI/CD queda planteada como trabajo futuro (ver `PROYECTO.md`, Sección 9).
