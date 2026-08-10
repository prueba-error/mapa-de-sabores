# Mapa de Sabores - Propuesta de Proyecto y Especificación Técnica

## Proyecto Final Desarrollo de Sistemas Web

**Alumno:** Diego Rafael Guaraz

---

## 1. Resumen

**Mapa de Sabores con IA** es un sistema web interactivo de descubrimiento gastronómico basado en una arquitectura híbrida de **Base de Datos Relacional + Inteligencia Artificial (IA)**.

El proyecto resuelve el problema del maridaje e innovación culinaria mediante una representación en forma de **Grafo de Sabores** interactivo y dinámico. Permite a profesionales de la cocina y aficionados explorar combinaciones de ingredientes basados en afinidad química y culinaria, consultar recetas reales integradas y recibir justificaciones organolépticas generadas por modelos de lenguaje (LLM).

### Principales pilares de ingeniería:
1. **Certeza en el Core (Base Relacional Estable):** La red de sabores reside en una base de datos PostgreSQL optimizada con índices compuestos bidireccionales. La estructura del grafo se define por datos curados y validados, no por generación en tiempo real de un modelo de lenguaje.
2. **Pipeline de Datos Sintéticos Offline:** Un pipeline de ingeniería de prompts sobre LLMs compila y cura un dataset inicial de 200–300 ingredientes y miles de pares de afinidad.
3. **Capa de IA Desacoplada e Intercambiable:** Un servicio backend agnóstico en FastAPI permite alternar entre proveedores cloud (Google Gemini, OpenAI) y ejecución 100% local (Ollama / Llama 3.2 3B).
4. **Visualización React en 2D:** Renderizado dinámico de nodos y aristas mediante `react-force-graph-2d` con experiencia de usuario fluida y paneles laterales descriptivos.

---

## 2. Marco Académico y Planteamiento del Problema

### 2.1 Problema Identificado

El descubrimiento de combinaciones de ingredientes (maridaje o *flavor pairing*) tradicionalmente ha dependido de la intuición empírica o de enciclopedias culinarias estáticas. Aunque existen teorías científicas de maridaje de sabores (compartir compuestos aromáticos clave), no existen herramientas web abiertas e interactivas en español que combinen:

* Exploración visual intuitiva en forma de grafo dinámico.
* Explicaciones organolépticas personalizadas en lenguaje natural.
* Búsqueda en tiempo real de recetas aplicadas.

### 2.2 Objetivos del Proyecto

* **Objetivo General:** Desarrollar una aplicación web full-stack funcional y escalable que permita explorar redes de sabores e interacciones de ingredientes asistida por Inteligencia Artificial.
* **Objetivos Específicos:**
  1. Diseñar un esquema relacional optimizado en PostgreSQL para modelar grafos bidireccionales de afinidad, con consultas de vecinos resueltas mediante índices compuestos.
  2. Implementar un pipeline offline en Python para la generación, validación y sanitización de un dataset sintético de afinidades culinarias.
  3. Crear una API REST en FastAPI con arquitectura limpia y abstracción del proveedor de LLM.
  4. Desarrollar una interfaz de usuario interactiva en React utilizando la librería `react-force-graph-2d`.
  5. Integrar autenticación JWT para áreas personalizadas de usuarios (guardar combinaciones favoritas y recetas).

### 2.3 Defensa

Las decisiones de diseño se fundamentan en criterios estratégicos de ingeniería de software:

* **PostgreSQL vs. Neo4j:** Se optó por PostgreSQL debido a que en una red de 300 a 1,000 ingredientes las consultas de 1 o 2 saltos (*hops*) no justifican la sobrecarga operativa y de consumo de memoria de un motor de grafos nativo como Neo4j. Mediante índices compuestos y ordenamiento de IDs, Postgres resuelve estas consultas de forma directa (sin recorridos recursivos), con un costo operativo y de despliegue significativamente menor.

* **Arquitectura Híbrida de IA:** La IA no actúa como la base de datos (evitando alucinaciones o respuestas lentas en navegación UI), sino como un potenciador en dos fases: compilación de dataset en pipeline offline y generación de prosa culinaria en línea.

---

## 3. Arquitectura General del Sistema

El sistema utiliza un patrón de **Arquitectura Multicapa Desacoplada** (Frontend Client, Backend API, Relational Storage & External Services).

```
+-----------------------------------------------------------------------------------+
|                                  CAPA FRONTEND                                    |
|         React (Vite) + Tailwind CSS + Context API + react-force-graph-2d          |
+-----------------------------------------------------------------------------------+
                                         │
                                  HTTP / REST (JWT)
                                         ▼
+-----------------------------------------------------------------------------------+
|                                  CAPA BACKEND                                     |
|                                FastAPI (Python)                                   |
|   ├─ Auth Controller & Security (JWT / Passlib)                                   |
|   ├─ Ingredients & Pairings Service (SQLAlchemy Core)                             |
|   ├─ LLM Provider Service Interface (Gemini / OpenAI / Ollama Adapter)            |
|   └─ Recipe Integration Service (Spoonacular Client + DB Cache)                   |
+-----------------------------------------------------------------------------------+
               │                                 │                         │
     SQL (SQLAlchemy/asyncpg)               HTTP API                  HTTP API
               ▼                                 ▼                         ▼
+-----------------------------+   +--------------------+    +----------------------+
|     PostgreSQL Database     |   |  External LLM API  |    |   Spoonacular API    |
| (Ingredients, Pairings, DB) |   | (Gemini / OpenAI)  |    | (Recetas Culinarias) |
+-----------------------------+   +--------------------+    +----------------------+
```

### 3.1 Flujo de Datos Principal
1. **Carga Inicial del Grafo:** El cliente React solicita `GET /api/v1/graph`. FastAPI consulta PostgreSQL y retorna los nodos y enlaces activos.
2. **Exploración y Filtrado:** El usuario selecciona un nodo (ej: *Tomate*). El frontend resalta vecinos y solicita `GET /api/v1/ingredients/{id}/pairings`.
3. **Explicación con IA (Online):** Al presionar "¿Por qué combinan?", el frontend invoca `POST /api/v1/ai/explain-pairing`. FastAPI utiliza la interfaz `LLMProvider` para generar un párrafo descriptivo con tono gastronómico.
4. **Recetas Relacionadas:** Al solicitar recetas para una combinación (ej: *Tomate + Albahaca + Ajo*), FastAPI consulta la caché local. Si no existe en caché, llama a la API de Spoonacular y guarda el resultado.

### 3.2 Configuración de Entorno (.env.example) y Orquestación Local (Docker Compose)
Para asegurar que cualquier desarrollador o evaluador pueda clonar e iniciar el entorno en local de manera reproducible:

1. **Estructura del archivo `.env.example`:**
```ini
# Base de Datos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secret
POSTGRES_DB=mapa_sabores
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres_secret@db:5432/mapa_sabores

# Seguridad & Autenticación
JWT_SECRET_KEY=super_secret_jwt_key_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Servicios de IA Externa
GEMINI_API_KEY=tu_google_gemini_api_key
OPENAI_API_KEY=tu_openai_api_key
LLM_PRIMARY_PROVIDER=gemini # "gemini" | "openai" | "ollama"
LLM_TIMEOUT_SECONDS=3.0

# API de Recetas
SPOONACULAR_API_KEY=tu_spoonacular_api_key
```

2. **Orquestación con Docker Compose (`docker-compose.yml`):**
   * Servicio `db`: Contenedor `postgres:16-alpine` con volumen persistente.
   * Servicio `backend`: Contenedor Python FastAPI ejecutando `alembic upgrade head` seguido de `uvicorn main:app`.
   * Servicio `frontend`: Contenedor Node.js Vite en desarrollo o servidor Nginx en producción.

---

## 4. Especificaciones del Modelo de Datos y Estrategia de Grafos

### 4.1 Esquema Relacional de PostgreSQL (DDL)

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

-- 3. Tabla de Afinidad de Maridaje (Grafo de Aristas)
CREATE TABLE flavor_pairings (
    id SERIAL PRIMARY KEY,
    ingredient_a_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    ingredient_b_id INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    affinity_score NUMERIC(3,2) NOT NULL CHECK (affinity_score BETWEEN 0.00 AND 1.00),
    ai_rationale VARCHAR(300), -- Explicación prediseñada acotada a máx 300 caracteres

    -- Restricción para garantizar que ingredient_a_id siempre sea menor que ingredient_b_id
    CONSTRAINT chk_ordered_pair CHECK (ingredient_a_id < ingredient_b_id),
    CONSTRAINT uq_ingredient_pair UNIQUE (ingredient_a_id, ingredient_b_id),
    CONSTRAINT chk_rationale_len CHECK (length(ai_rationale) <= 300)
);

-- Índices optimizados para búsquedas bidireccionales inmediatas
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

-- 5. Caché e Indexación Permanente de Recetas en el Servidor
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE, -- ID devuelto por Spoonacular (opcional)
    title VARCHAR(255) NOT NULL,
    image_url TEXT,
    source_url TEXT,
    ready_in_minutes INT,
    servings INT,
    raw_json JSONB NOT NULL, -- Datos completos de la receta (ingredientes, pasos, nutrición)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipe_search_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(64) UNIQUE NOT NULL, -- Hash SHA-256 de los ingredient_ids ordenados (ej: hash("12,45,88"))
    ingredient_ids INT[] NOT NULL,
    recipe_ids INT[] NOT NULL, -- Arreglo de IDs de la tabla 'recipes'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recipe_search_hash ON recipe_search_cache(cache_key);
```

### 4.2 Lógica de Consulta Bidireccional
Dado que un par (ej: *Tomate*, *Albahaca*) es equivalente a (*Albahaca*, *Tomate*), la restricción `ingredient_a_id < ingredient_b_id` evita duplicados.

Para obtener todas las afinidades de un ingrediente `:ingredient_id`:
```sql
SELECT
    CASE 
        WHEN p.ingredient_a_id = :ingredient_id THEN i2.id 
        ELSE i1.id 
    END AS neighbor_id,
    CASE 
        WHEN p.ingredient_a_id = :ingredient_id THEN i2.name 
        ELSE i1.name 
    END AS neighbor_name,
    p.affinity_score,
    p.ai_rationale
FROM flavor_pairings p
JOIN ingredients i1 ON p.ingredient_a_id = i1.id
JOIN ingredients i2 ON p.ingredient_b_id = i2.id
WHERE p.ingredient_a_id = :ingredient_id OR p.ingredient_b_id = :ingredient_id
```

### 4.3 Estrategia de Migraciones y Versionado de Base de Datos (Alembic)
Para garantizar la evolución controlada del esquema sin pérdida de datos ni discrepancias entre entornos (desarrollo, testing, producción), el proyecto utiliza **Alembic** integrado con **SQLAlchemy Core**:

1. **Control de Versiones del Esquema:** Cada cambio en la estructura DDL se registra como un script de migración versionado en `backend/alembic/versions/` etiquetado con hashes secuenciales y mensajes descriptivos.
2. **Ejecución Automatizada:** En el arranque del contenedor/servidor FastAPI, se ejecuta automáticamente `alembic upgrade head` para garantizar que la base de datos se encuentre sincronizada con la versión más reciente del código.
3. **Rollback Seguro:** Todos los scripts de migración incluyen métodos explícitos `upgrade()` y `downgrade()` para permitir la reversión limpia de cambios en caso de contingencia.

---

## 5. Pipeline Offline y Origen del Dataset de Sabores (Mes 1)

### 5.1 Origen y Fuentes Prácticas de la Información

El dataset no se construye por relevamiento manual, sino combinando tres fuentes complementarias:

1. **La IA como "Sintetizador y Destilador de Conocimiento" (Pipeline Offline - Método Principal):**
   * Los modelos de lenguaje modernos (OpenAI GPT-4o, Google Gemini) fueron entrenados con millones de textos científicos, recetas globales y literatura gastronómica de referencia (incluyendo *The Flavor Bible*, *The Flavor Thesaurus* y artículos científicos de maridaje molecular).
   * En lugar de descargar o transcribir libros, nuestro script en Python (`scripts/seed_flavor_network.py`) consulta en lote al LLM mediante solicitudes estructuradas (JSON Mode con Pydantic). La IA actúa como un "chef experto", evaluando cada par de ingredientes y generando la puntuación de afinidad (0.0 a 1.0) y la explicación culinaria.
2. **Datasets Abiertos Académicos en GitHub y Kaggle (Fuentes Públicas Abiertas):**
   * **FlavorDB / Flavornet:** Proyecto científico abierto de IIIT Delhi que mapea ~1,000 ingredientes a sus moléculas aromáticas volátiles (eugenol, linalool, etc.). Sus datasets son descargables públicamente en formato CSV/JSON.
   * **Nature Scientific Reports - Dataset de "Flavor Network":** Dataset público del famoso estudio científico de Yong-Yeol Ahn (*"Flavor network and the principles of food pairing"*), disponible libremente en repositorios de GitHub.
3. **Co-ocurrencia Estadística en Recetas (Spoonacular / RecipeDB):**
   * Mapeo estadístico automático: Si dos ingredientes (ej: *Tomate* y *Albahaca*) aparecen juntos frecuentemente en miles de recetas procesadas, se refuerza la puntuación de afinidad.

**Nota metodológica sobre la normalización del score:** las fuentes anteriores no son directamente comparables entre sí. FlavorDB/Flavornet expresan afinidad como cantidad de compuestos aromáticos volátiles compartidos (un número entero, no un score de 0 a 1), mientras que el LLM devuelve directamente un puntaje 0.0–1.0 y la co-ocurrencia en recetas es una frecuencia relativa. El pipeline define una fórmula explícita de normalización (por ejemplo, escalar la cantidad de compuestos compartidos contra el máximo observado en el dataset) para llevar todas las fuentes a la misma escala antes de promediarlas o combinarlas. Esta fórmula y su justificación deben documentarse como una decisión metodológica propia del proyecto.

### 5.2 Fases del Pipeline Offline (`scripts/seed_flavor_network.py`)
1. **Semilla de Ingredientes:** Listado inicial normalizado en JSON/CSV con ~250 ingredientes comunes clasificados por categorías (Frutas, Verduras, Carnes, Lácteos, Hierbas/Especias, Granos).
2. **Generación Automatizada de Pares:** El script genera pares lógicos de ingredientes y consulta al LLM en lotes para extraer puntajes de afinidad y explicaciones en español. Soporta el flag `--dry-run` para validar prompts y esquemas JSON sin escribir en la base de datos ni gastar créditos de API.
3. **Control de Calidad y Sanitización:**
   * Filtrado de pares con puntuación menor a 0.40 para evitar saturación visual en el grafo.
   * Validación de tipos con Pydantic.
   * Inserción ordenada en PostgreSQL (`ingredient_a_id < ingredient_b_id`).

### 5.3 Diseño de Prompts, Criterios de Curado y Respaldos
1. **Ejemplo de Prompt Estructurado (JSON Mode):**
   > *"Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. Evalúa la afinidad organoléptica entre [Ingrediente A] y [Ingrediente B]. Responde estrictamente en JSON con la siguiente estructura: `{"affinity_score": float (0.00 a 1.00), "ai_rationale": string (máximo 250 caracteres en español explicativo)}`."*
2. **Criterios de Curado Manual y Mapeo Culinario:**
   * Revisión por muestreo aleatorio (mínimo el 10% del dataset o 150 pares) verificando coherencia gastronómica.
   * Eliminación manual de alucinaciones o justificaciones redundantes antes de la inserción final.
3. **Estrategia de Snapshot y Backup de Base de Datos:**
   * Previo a ejecutar la carga masiva del dataset en PostgreSQL, el pipeline invoca automáticamente una salva de respaldo mediante `pg_dump`:
     `pg_dump -U postgres -d mapa_sabores -f backups/pre_seed_snapshot.sql`
4. **Métricas de Calidad del Dataset (Acceptance Metrics):**
   * **Cobertura:** Al menos el 80% de los 250 ingredientes deben contar con un mínimo de 4 conexiones activas ($>0.40$).
   * **Consistencia Sintáctica:** 100% de cumplimiento del esquema Pydantic y límite de 300 caracteres en `ai_rationale`.

---

## 6. ESPECIFICACIÓN DE LA API REST (FastAPI)

### 6.1 Autenticación (`/api/v1/auth`)
* `POST /api/v1/auth/register`: Registro de nuevo usuario.
* `POST /api/v1/auth/login`: Autenticación y retorno de Access Token JWT.
* `GET /api/v1/auth/me`: Perfil del usuario autenticado.

### 6.2 Red y Grafo (`/api/v1/graph`)
* `GET /api/v1/graph`: Retorna una estructura paginada o acotada de subgrafo para `react-force-graph` evitando saturar el navegador.
  * **QueryParams:** `limit` (default: 50, max: 100), `offset` (default: 0), `min_affinity` (default: 0.50), `category_id` (opcional).
* `GET /api/v1/ingredients`: Lista paginada con filtro de búsqueda de ingredientes.
* `GET /api/v1/ingredients/{id}/pairings`: Obtiene los ingredientes vecinos directos (Top-N) y sus afinidades.

### 6.3 Servicio de Evaluación Multi-Ingrediente e IA (`/api/v1/pairings`, `/api/v1/ai`)

Este servicio separa explícitamente dos responsabilidades: el cálculo de sinergia es **determinístico** (se resuelve enteramente contra los datos de `flavor_pairings`, sin invocar un LLM), mientras que la sugerencia de reemplazo es **generativa** (requiere una llamada a IA, ya que implica razonar sobre qué ingrediente alternativo mejoraría la combinación, algo que no se desprende directamente de la matriz de puntajes).

* `POST /api/v1/pairings/evaluate`: Recibe un arreglo de 2 o más `ingredient_ids`. Calcula, únicamente a partir de la base de datos, la matriz de afinidades cruzadas, el **Índice de Sinergia Global (0-100%)** y el o los ingredientes discordantes (*clashing elements*, definidos como el ingrediente con menor afinidad promedio respecto al resto del grupo).
* `POST /api/v1/ai/suggest-replacement`: Recibe el resultado de `evaluate` cuando se detecta un ingrediente discordante. Invoca al LLM con ese contexto (afinidades ya calculadas) para sugerir un reemplazo con sentido gastronómico y redactar la justificación. Se llama solo bajo demanda del usuario (botón explícito), no automáticamente en cada evaluación.
* `POST /api/v1/ai/explain-pairing`: Recibe `[ingredient_id_1, ingredient_id_2, ...]`. Invoca la interfaz de LLM y devuelve la explicación organoléptica en tiempo real.

```json
// POST /api/v1/pairings/evaluate Body:
{
  "ingredient_ids": [12, 45, 88] // ej: Tomate, Albahaca, Chocolate
}

// Response 200 OK (cálculo determinístico, sin IA):
{
  "overall_synergy_score": 58.5,
  "synergy_label": "Maridaje Moderado / Arriesgado",
  "pairwise_matrix": [
    {"pair": ["Tomate", "Albahaca"], "affinity": 0.96, "status": "excellent"},
    {"pair": ["Tomate", "Chocolate"], "affinity": 0.35, "status": "clash"},
    {"pair": ["Albahaca", "Chocolate"], "affinity": 0.44, "status": "weak"}
  ],
  "clashing_ingredients": ["Chocolate"]
}

// POST /api/v1/ai/suggest-replacement Body (solo si el usuario lo solicita):
{
  "ingredient_ids": [12, 45, 88],
  "clashing_ingredient": "Chocolate"
}

// Response 200 OK (generado por LLM):
{
  "recommendation": "El Chocolate presenta baja compatibilidad con el Tomate. Se sugiere reemplazar por Queso Mozzarella."
}
```

### 6.4 Servicio de Recetas y Estrategia de Caché Permanente (`/api/v1/recipes`)
* `GET /api/v1/recipes/search?ingredient_ids=12,45,88`: Recibe una lista de ingredientes y busca recetas coincidentes.

#### ¿La información es temporal (usuario) o permanente (servidor)?
La información **QUEDA GUARDADA DE FORMA PERMANENTE EN EL SERVIDOR (Base de Datos PostgreSQL)**. No es temporal del navegador del usuario.

#### Razones Técnicas de esta Decisión:
1. **Ahorro de Cuota de API (Límite Spoonacular):** La cuota gratuita de Spoonacular ofrece solo 150 puntos/día. Guardar las recetas en el servidor evita agotar la cuota con búsquedas repetidas.
2. **Reducción de Latencia:** Una búsqueda a Spoonacular tarda entre 800ms y 2000ms. Consultar recetas ya cacheadas en PostgreSQL es sensiblemente más rápido, al tratarse de una lectura local sin llamada HTTP externa.
3. **Construcción Progresiva del Dataset:** Con el uso diario de los usuarios, el servidor va construyendo automáticamente su propio repositorio enriquecido de recetas.

#### Idioma de las Recetas y Traducción Automática al Español
La base de datos original de **Spoonacular está principalmente en inglés**. Para ofrecer una experiencia 100% nativa en español:

1. **Pipeline de Traducción al Cachear (Translation-on-Cache):**
   * Cuando FastAPI recupera una receta nueva de Spoonacular (en inglés), **antes de guardarla en PostgreSQL**, el backend realiza un pase automático rápido por el servicio de LLM (Gemini Flash / GPT-4o-mini) con el prompt: *"Traduce al español neutro el título, ingredientes e instrucciones de preparación manteniendo la estructura JSON"*.
2. **Cero Latencia Adicional para el Usuario:**
   * La traducción ocurre **una sola vez por receta** (al momento de ser descubierta e ingresada a la tabla `recipes`).
   * Todas las consultas posteriores leen el texto traducido directamente desde PostgreSQL en < 10ms.

#### Flujo de Obtención, Traducción e Indexación (FastAPI Backend):
```
       [ Usuario consulta: Tomate (12) + Albahaca (45) + Queso (88) ]
                                      │
                                      ▼
                Calcular Hash de Búsqueda: SHA256("12,45,88")
                                      │
                  ¿Existe `cache_key` en `recipe_search_cache`?
                           /                     \
                       SÍ                         NO
                      /                             \
 Obtener `recipe_ids` de DB             Llamar API Spoonacular [EN]
 Cargar recetas desde `recipes`                      │
 Retornar en español (<10ms)            Traducir al Español vía LLM
                                                     │
                                        Guardar en DB `recipes`
                                        Guardar Hash en `recipe_search_cache`
                                                     │
                                         Retornar al usuario en Español
```

### 6.5 Contratos de Entrada/Salida y Esquemas de Validación (Pydantic v2)
Todos los datos procesados por FastAPI son estrictamente validados mediante modelos **Pydantic v2**:

```python
# Ejemplo de Esquema de Validación de Evaluación Multi-Ingrediente
class PairingEvaluationRequest(BaseModel):
    ingredient_ids: List[int] = Field(..., min_items=2, max_items=10, description="Lista de IDs de ingredientes a evaluar")

class PairwiseStatus(str, Enum):
    EXCELLENT = "excellent"  # > 0.75
    NEUTRAL = "neutral"      # 0.45 - 0.74
    CLASH = "clash"          # < 0.45

class PairwiseDetail(BaseModel):
    pair: Tuple[str, str]
    affinity: float = Field(..., ge=0.0, le=1.0)
    status: PairwiseStatus

class PairingEvaluationResponse(BaseModel):
    overall_synergy_score: float = Field(..., ge=0.0, le=100.0)
    synergy_label: str
    pairwise_matrix: List[PairwiseDetail]
    clashing_ingredients: List[str]
```

### 6.6 Especificación de Seguridad, Autenticación y Control de Tasa (Hardening)
1. **Hashing de Contraseñas:** Se utiliza **Passlib** con el algoritmo **Argon2id** (o `bcrypt` con factor de costo 12), garantizando resistencia contra ataques de fuerza bruta y Rainbow Tables.
2. **Ciclo de Vida, Rotación y Revocación de Tokens JWT:**
   * `access_token`: Firma HMAC-SHA256 con tiempo de expiración corto de **30 minutos**.
   * `refresh_token`: Almacenado en galleta de solo lectura HTTP-Only y SameSite=Strict con validez de **7 días**.
   * **Rotación y Revocación:** Al refrescar o cerrar sesión (`POST /api/v1/auth/logout`), el `refresh_token` utilizado se invalida registrando su `jti` (JWT ID) en la tabla `revoked_tokens` en PostgreSQL (o caché en memoria Redis) evitando su reutilización.
3. **Control Dual de Tasa de Peticiones (Rate Limiting con `slowapi`):**
   * Peticiones anónimas: Limitadas por Dirección IP (**60 req/min**).
   * Peticiones autenticadas: Limitadas por **`user_id`** (**120 req/min** para endpoints REST de lectura, **10 req/min** para IA generativa en Tier Free y **30 req/min** en Tier Pro).
4. **Monitoreo de SLAs y Alertas Operativas:**
   * Registro estructurado en consola (JSON Logs) midiendo tiempos de respuesta de llamadas externas.
   * Disparo de métrica/alerta si la tasa de fallback a la DB sobrepasa el **5% de las solicitudes** en un intervalo de 15 minutos.

### 6.7 Resiliencia del Servicio de IA (Timeout, Retries & Fallback Hierarchy)
Para evitar que problemas de red o latencia en los proveedores cloud de IA afecten la experiencia del usuario:
1. **Timeout Estricto:** Peticiones HTTP a proveedores de IA (Gemini/OpenAI) configuradas con un tiempo límite máximo de **3.0 segundos**.
2. **Reintentos Exponenciales:** En caso de error de red 5xx, se ejecuta como máximo **1 reintento** con *backoff* exponencial.
3. **Jerarquía de Fallback (Degradación Grácil):**
   * *Nivel 1 (Cloud Principal):* Google Gemini 1.5 Flash.
   * *Nivel 2 (Cloud Secundario):* OpenAI GPT-4o-mini.
   * *Nivel 3 (Fallback Local inmutable):* Si ambos servicios fallan o sobrepasan los 3 segundos, la API responde utilizando la justificación prediseñada almacenada en PostgreSQL durante el pipeline offline (`ai_rationale`), garantizando disponibilidad del 100%.

---

## 7. Diseño Frontend y Experiencia Visual

El frontend se estructurará con **React (Vite)** y **Tailwind CSS**.

```
+-----------------------------------------------------------------------------------+
| Navbar: Logo  |  Buscador: [Tomate x] [Albahaca x]  |  Filtros  |  [ Evaluar ]    |
+------------------------------------------------------+----------------------------+
|                                                      |   Panel Lateral (Drawer)   |
|               ÁREA PRINCIPAL DEL GRAFO               |                            |
|                (react-force-graph-2d)                |  📊 Sinergia Global: 92%   |
|                                                      |  [██████████████████░░]    |
|              ( QUESO )                               |                            |
|                  │ (Verde 92%)                       |  Matriz de Compatibilidad: |
|                  ▼                                   |  • Tomate + Albahaca: 98%  |
|             ( TOMATE ) ════════════ ( ALBAHACA )     |  • Tomate + Queso: 92%     |
|                  │      (Verde 98%)                  |                            |
|                  ┊ (Rojo punteado 35%)               |  [ ✨ Explicación de Chef ] |
|                  ▼                                   |  [ 🍳 14 Recetas ]         |
|            ( CHOCOLATE )                             |                            |
+------------------------------------------------------+----------------------------+
```

### 7.1 Landing Page y Experiencia de Búsqueda Inicial
1. **Buscador Central con Sugerencias Rápidas:**
   * La pantalla de inicio presenta una barra de búsqueda centrada y limpia con sugerencias o etiquetas de tendencias debajo (ej: `[Tomate y Albahaca]`, `[Palta y Limón]`, `[Chocolate y Naranja]`, `[Café y Vainilla]`).
   * Al seleccionar o tipear una sugerencia, la interfaz realiza la transición suave hacia la vista del grafo interactivo.

### 7.2 Lógica Dinámica y Progresiva del Grafo (1, 2 y N Ingredientes)
El renderizado del grafo responde en tiempo real a medida que el usuario agrega o remueve ingredientes:

1. **Selección de 1 Ingrediente (ej: *Tomate*):**
   * El ingrediente seleccionado se ubica en el centro del lienzo.
   * Se despliegan aristas radiales conectándolo exclusivamente con sus **Top 5-8 ingredientes de mayor afinidad** (ej: *Albahaca, Ajo, Queso Mozzarella, Orégano, Aceite de Oliva*).
2. **Selección de 2 Ingredientes (ej: *Tomate + Albahaca*):**
   * Se dibuja una arista principal entre ambos nodos con un color que representa su nivel de afinidad (ej: Verde Esmeralda para afinidad alta $> 75\%$).
   * **Resaltado por Intensidad Armónica:** Los ingredientes vecinos conectados que presentan alta afinidad **con AMBOS ingredientes seleccionados a la vez** se iluminan con **mayor intensidad visual (brillo/opacidad 100%)**, destacando la verdadera sinergia gastronómica.
3. **Incorporación de un Ingrediente Incompatible (ej: *Tomate + Albahaca + Chocolate*):**
   * La arista que conecta el ingrediente discordante (*Chocolate*) se grafica en **ROJO destellante o punteado** (indicando choque de sabor / incompatibilidad $< 45\%$).
   * Los ingredientes vecinos alrededor del grupo se atenúan con **menor intensidad visual (opacidad reducida al 30%)**, señalando que la combinación global ha perdido armonía.
4. **Escala Progresiva a N Ingredientes:**
   * La matriz de intensidad y colores de aristas se recalculan dinámicamente en < 16ms (60 FPS) a medida que se suman más ingredientes a la receta.

### 7.3 Panel Lateral (Drawer) e Interacciones
* **Medidor Visual de Sinergia (Synergy Gauge):** Indicador porcentual de maridaje global del plato.
* **Matriz Interactiva $N \times N$:** Tabla de afinidades cruzadas para inspección rápida de pares.
* **Detector del Elemento Discordante (*Clashing Alert*):** Alerta en rojo identificando el ingrediente desentonante y habilitando la opción de sugerir reemplazo.

---

## 💎 11. Niveles de Suscripción y Modelo Freemium (Tiers de Servicio)

Para garantizar la viabilidad comercial y el control de recursos del servidor, el sistema implementa una estructura de cuentas dividida en dos niveles:

| Característica / Funcionalidad | Tier Gratuito (Free) | Tier Pago (Pro / Premium) |
| :--- | :--- | :--- |
| **Límite de Ingredientes por Búsqueda** | **Hasta 3 ingredientes** (ideal para tríadas gastronómicas) | **Hasta 10 ingredientes** (platos complejos / recetas completas) |
| **Visualización de Grafo y Sinergia** | ✅ Acceso Completo | ✅ Acceso Completo |
| **Explicación de Chef con IA** | ✅ Incluido (Límite diario) | ✅ Ilimitado |
| **Búsqueda de Recetas** | ✅ Incluido | ✅ Incluido |
| **Guardado en Servidor (Workspace)** | ✅ Solo Combinaciones Favoritas | ✅ **Combinaciones Favoritas + Recetas Completas con Notas** |
| **Exportación de Datos (Export & API)** | ❌ No disponible | ✅ **Exportar a Texto Plano, JSON y Acceso a API Key** |

### 💡 Justificación del Límite de 3 Ingredientes en el Tier Gratuito:
Un límite de 3 ingredientes en el plan gratuito permite a los usuarios experimentar tríadas culinarias icónicas (ej: *Mirepoix*, *Tríada Caprese: Tomate + Albahaca + Mozzarella*), comprobando el valor de la sinergia y la IA. Para chefs profesionales, sommeliers o mixólogos que diseñan recetas complejas de 5 a 8 componentes, el **Tier Pro** desbloquea la capacidad total y la exportación de datos en JSON.

---

## 8. Estrategia de Pruebas Automatizadas y Metodología TDD (Test-Driven Development)

El proyecto adopta una disciplina estricta de **Desarrollo Guiado por Pruebas (TDD)** siguiendo el ciclo continuo **Red ➔ Green ➔ Refactor**. Toda funcionalidad del backend y del frontend debe contar con sus correspondientes pruebas automatizadas escritas *antes* del código de producción.

```
       ┌────────────────────────────────────────────────────────┐
       │                 CICLO TDD (Red-Green-Refactor)         │
       └────────────────────────────────────────────────────────┘
            1. RED ──► Escribir prueba fallida que define el requisito
            2. GREEN ─► Escribir el código mínimo para pasar la prueba
            3. REFACTOR ► Limpiar y optimizar el código manteniendo la prueba en verde
```

### 8.1 Stack de Pruebas en Backend (Python / FastAPI)
* **Framework Principal:** `pytest` + `pytest-asyncio` para la ejecución asíncrona de pruebas en FastAPI.
* **Cliente HTTP de Pruebas:** `httpx.AsyncClient` para testear endpoints REST sin levantar un servidor real.
* **Acceso a Base de Datos en Tests:** Base de datos PostgreSQL aislada de testing en contenedor Docker con `alembic` ejecutado previo a cada suite de pruebas.
* **Cobertura Mínima Exigida:** **85% de cobertura de código** medida con `pytest-cov`.
* **Pruebas Unitarias Clave (TDD):**
  * Verificación determinística de la matriz de sinergia $N \times N$, cálculo del score global y detección del ingrediente discordante.
  * Verificación de la restricción `ingredient_a_id < ingredient_b_id` y ordenamiento de pares.
  * Verificación del pipeline de hashing SHA-256 para `cache_key` de recetas.
* **Pruebas de Integración y Mocks:**
  * Inyección de *Mocks* para llamadas a Spoonacular y LLM (Gemini/OpenAI) simulando respuestas exitosas, respuestas traducidas, timeouts (3s) y fallbacks a la DB.

### 8.2 Stack de Pruebas en Frontend (React / Vite)
* **Runner de Pruebas:** `Vitest` (ejecución ultrarrápida nativa de Vite).
* **Renderizado y Aseveraciones UI:** `React Testing Library` (@testing-library/react) enfocada en testear comportamiento de usuario y accesibilidad.
* **Mock de Respuestas API HTTP:** `MSW` (Mock Service Worker) para interceptar peticiones de red y testear estados de carga, error y renderizado de recetas.
* **Pruebas de Componentes Clave (TDD):**
  * Renderizado del componente buscador central y sugerencias de etiquetas.
  * Comportamiento del panel lateral (Drawer) al recibir datos de sinergia ($N \times N$) e indicador de porcentaje.
  * Activación del modo de visualización de ingredientes discordantes en rojo y atenuación de nodos.

---

## 9. Plan Global de Implementación Ágil (8 Sprints de 2 Semanas)

Para mitigar riesgos y asegurar la entrega en tiempo, el plan de 4 meses se divide en **8 Sprints ágiles de 2 semanas** con *Criterios de Aceptación (Definition of Done)* explícitos por Sprint:

### 🚀 Fase 1: Arquitectura, Data Pipeline y Prototipado Temprano (Mes 1)
* **Sprint 1 (Sem. 1-2) — Cimientos, DDL y Migraciones Alembic:**
  * *Entregable:* Base de datos PostgreSQL configurada en Docker con esquemas relacionales, índices compuestos y migraciones iniciales de `Alembic`.
  * *Criterios TDD:* Tests en `pytest` pasando para restricciones DDL y funciones de consulta bidireccional.
* **Sprint 2 (Sem. 3-4) — Pipeline Offline de Datos + Prototipo Temprano del Grafo (Spike):**
  * *Entregable Backend:* Script `seed_flavor_network.py` con LLM generando el dataset inicial (~250 ingredientes y ~1,500 relaciones).
  * *Entregable Frontend (Spike):* Prototipo temprano en React con `react-force-graph-2d` renderizando datos estáticos mock para evaluar rendimiento y usabilidad.

### ⚙️ Fase 2: Backend Core, Autenticación y Caché Permanente (Mes 2)
* **Sprint 3 (Sem. 5-6) — Endpoints REST de Grafo y Sinergia Determinística:**
  * *Entregable:* Endpoints `GET /api/v1/graph`, `GET /api/v1/ingredients` y `POST /api/v1/pairings/evaluate` (cálculo de sinergia y detección de elemento discordante 100% en DB).
  * *Criterios TDD:* Cobertura de tests unitarios al 90% para la matemática de sinergia y ordenamiento.
* **Sprint 4 (Sem. 7-8) — Autenticación JWT, Seguridad y Caché de Recetas:**
  * *Entregable:* Sistema de Auth (Argon2id + JWT `access_token` y `refresh_token`), control de tasa `slowapi` y cliente de Spoonacular con almacenamiento permanente en PostgreSQL.

### 🎨 Fase 3: Frontend Interactivo, Visualización Progresiva e IA Online (Mes 3)
* **Sprint 5 (Sem. 9-10) — Frontend Grafo Progresivo e Intensidad Armónica:**
  * *Entregable:* Buscador central con etiquetas de sugerencia y renderizado dinámico del grafo (nodos radiales para 1 ingrediente, aristas verdes/amarillas/rojas y resaltado por intensidad armónica).
* **Sprint 6 (Sem. 11-12) — Integración de Drawers, Recetas Traducidas e IA Online:**
  * *Entregable:* Panel lateral de sinergia, visualización de matriz $N \times N$, tarjetas de recetas traducidas automáticamente al español e integración del endpoint de explicaciones generativas en vivo (`/api/v1/ai/explain-pairing`).

### 🛡️ Fase 4: Resiliencia, Pruebas E2E, QA y Defensa Académica (Mes 4)
* **Sprint 7 (Sem. 13-14) — Tiers de Suscripción, Resiliencia de IA y Fallbacks:**
  * *Entregable:* Control de límites por Tier (Free: 3 ingredientes, Pro: 10 ingredientes), timeout de 3s en llamadas a la IA y fallback automático a la justificación inmutable de PostgreSQL.
* **Sprint 8 (Sem. 15-16) — Buffer de QA, Pruebas E2E, Refactor TDD y Memoria de Tesis:**
  * *Entregable:* Suite completa de pruebas TDD ejecutándose en verde (`pytest` + `Vitest`), optimización de velocidad de carga, documentación final y preparación de la defensa ante el tribunal.
### 9.1 Prioridad de Siguientes Acciones Rápida (Kickoff del Código - Sprint 1)
Para iniciar la fase de desarrollo sin fricción, se establece la siguiente secuencia de ejecución ordenada:

1. **Configuración de Entorno Local:** Crear `.env.example` y la infraestructura base de `docker-compose.yml` (PostgreSQL + FastAPI).
2. **Migración Inicial de Base de Datos:** Inicializar `Alembic` y generar el script de migración inicial `001_initial_schema.py` con el DDL completo.
3. **Scaffolding del Data Pipeline:** Estructurar `scripts/seed_flavor_network.py` implementando el soporte del flag `--dry-run` para validar esquemas Pydantic y prompts sin consumir API.
4. **Implementación del Servicio de IA:** Crear la interfaz `LLMProvider` con los adaptadores (Gemini / OpenAI), manejando timeouts (3s), retries y el fallback a la DB.
5. **Primeras Pruebas Unitarias TDD:** Escribir las pruebas con `pytest` para la matemática determinística del endpoint `POST /api/v1/pairings/evaluate`.

---

## 9. Matriz de Riesgos y Mitigación

| Riesgo Identificado | Impacto | Mitigación Planificada |
| :--- | :--- | :--- |
| **Agotamiento de cuota en API de Recetas** | Medio | Implementación obligatoria de tabla caché en PostgreSQL; límite de solicitudes en frontend. |
| **Saturación visual en el grafo por demasiados nodos** | Alto | Filtro estricto en frontend con min_affinity por defecto en 0.50 y paginación de nodos vecinos. |
| **Alucinaciones o latencia en respuestas de IA** | Medio | Prompting estructurado con Pydantic/JSON Mode; fallback a la justificación pre-calculada en la DB si la llamada API falla o sobrepasa el timeout (3s). |
| **Demoras en el objetivo opcional (Modelo Local)** | Bajo | El modelo local es un *Stretch Goal*. Si no se completa a tiempo, el proyecto principal con API Cloud se mantiene 100% funcional. |

---

## 10. Análisis de Viabilidad Económica y Escalabilidad

El diseño arquitectónico del proyecto garantiza una **alta eficiencia de costos y sostenibilidad financiera**, permitiendo operar a costo **$0.00 USD** durante toda la fase de desarrollo y defensa, manteniendo costos marginales mínimos ante un crecimiento de usuarios a escala.

### 10.1 Estrategia de Optimización de Costos de API
1. **API de Recetas (Spoonacular) — Amortización por Caché Local:**
   * La cuota gratuita ofrece 150 puntos/día. 
   * Gracias al **Caché Progresivo en PostgreSQL (`recipe_search_cache`)**, la dependencia de la API disminuye asintóticamente con el uso: más del 90% de las búsquedas frecuentes de usuarios leen directamente de la base de datos local (< 10ms) sin consumir cuota externa.
2. **APIs de Inteligencia Artificial (LLM) — Modelos de Alta Eficiencia:**
   * Se utilizan modelos de última generación ultralivianos (Google Gemini 1.5 Flash / OpenAI GPT-4o-mini).
   * **Generación en tiempo real:** $0.075 USD por millón de tokens en Gemini Flash (~$0.00005 USD por explicación de chef).
   * **Pipeline Offline (Mes 1):** Compilación inicial del grafo de 1,500 afinidades por **~$0.30 USD por única vez**.

### 10.2 Cuadro Comparativo de Proyección de Costos por Nivel de Escala

| Nivel de Escala | Usuarios Activos / Mes | API Recetas (Con Caché DB) | API IA (Gemini Flash / GPT-4o-mini) | Hosting & PostgreSQL | **Costo Total Estimado** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MVP / Defensa Tesis** | 1 – 100 | **$0.00** (Free Tier) | **$0.00** (Free Tier) | **$0.00** (Render / Supabase Free) | **$0.00 USD / mes** |
| **Producción Inicial** | 1,000 | **$0.00** (Caché DB absorbe 95%) | ~$0.15 USD | $0 – $5.00 USD | **~$0.15 – $5.00 USD / mes** |
| **Escala Media** | 25,000 | ~$29.00 USD (Spoonacular Builder) | ~$2.50 USD | ~$10.00 USD (DB 5GB) | **~$41.50 USD / mes** |

### 10.3 Argumentación de Viabilidad para la Defensa Academica
Este análisis demuestra criterio de ingeniería de software enfocado en la **economía de recursos y optimización operativa**, probando que el sistema no solo es funcional y estéticamente atractivo, sino también **financieramente viable y preparado para producción real**.