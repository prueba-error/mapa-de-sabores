# Mapa de Sabores - Especificación Técnica Detallada (SPEC.md)

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
    source_type VARCHAR(30) DEFAULT 'llm_synthesis', -- 'llm_synthesis', 'flavordb_chemical', 'recipe_cooccurrence'
    confidence_score NUMERIC(3,2) DEFAULT 0.85 CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Restricción para garantizar que ingredient_a_id siempre sea menor que ingredient_b_id
    CONSTRAINT chk_ordered_pair CHECK (ingredient_a_id < ingredient_b_id),
    CONSTRAINT uq_ingredient_pair UNIQUE (ingredient_a_id, ingredient_b_id),
    CONSTRAINT chk_rationale_len CHECK (length(ai_rationale) <= 300)
);

-- Índices optimizados para búsquedas bidireccionales inmediatas
CREATE INDEX idx_pairings_a ON flavor_pairings(ingredient_a_id);
CREATE INDEX idx_pairings_b ON flavor_pairings(ingredient_b_id);
CREATE INDEX idx_pairings_score ON flavor_pairings(affinity_score DESC);

-- 4. Usuarios, Favoritos y Revocación de Tokens
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE revoked_tokens (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID único
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    revoked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_revoked_jti ON revoked_tokens(jti);

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
    raw_json JSONB NOT NULL, -- Datos sanitizados de la receta (máx 30 KB)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipe_search_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(64) UNIQUE NOT NULL, -- Hash SHA-256 de los ingredient_ids ordenados
    ingredient_ids INT[] NOT NULL,
    recipe_ids INT[] NOT NULL, -- Arreglo de IDs de la tabla 'recipes'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recipe_search_hash ON recipe_search_cache(cache_key);

-- 6. Cola de Revisión para Arbitraje Manual de Alucinaciones
CREATE TABLE pairing_review_queue (
    id SERIAL PRIMARY KEY,
    ingredient_a_id INT NOT NULL REFERENCES ingredients(id),
    ingredient_b_id INT NOT NULL REFERENCES ingredients(id),
    suggested_score NUMERIC(3,2) NOT NULL,
    ai_rationale VARCHAR(300),
    flag_reason VARCHAR(100) NOT NULL, -- ej: 'forbidden_antagonistic_pair', 'high_flavor_db_variance'
    status VARCHAR(20) DEFAULT 'pending_review', -- 'pending_review', 'approved', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2 Lógica de Consulta Bidireccional
Dado que un par (ej: _Tomate_, _Albahaca_) es equivalente a (_Albahaca_, _Tomate_), la restricción `ingredient_a_id < ingredient_b_id` evita duplicados.

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

### 1.3 Estrategia de Migraciones con Alembic
* **Control de Versiones:** Cambios DDL registrados en `backend/alembic/versions/` con hashes secuenciales.
* **Ejecución Automática:** En el arranque del backend se invoca `alembic upgrade head`.
* **Rollback Seguro:** Métodos explícitos `upgrade()` y `downgrade()`.

---

## 2. Pipeline Offline y Origen del Dataset de Sabores

### 2.1 Fuentes Prácticas de Información
1. **La IA como Sintetizador de Conocimiento (Pipeline Offline):** Solicitudes en lote sobre LLMs (JSON Mode con Pydantic) evaluando combinaciones mediante `scripts/seed_flavor_network.py`.
2. **Datasets Abiertos Académicos:** FlavorDB / Flavornet (compuestos moleculares volátiles) y dataset del estudio de Yong-Yeol Ahn (_Nature Flavor Network_).
3. **Co-ocurrencia Estadística en Recetas:** Frecuencia de aparición conjunta en recetas procesadas.

### 2.2 Fases del Pipeline Offline
1. **Semilla de Ingredientes:** JSON/CSV con ~250 ingredientes clasificados por categoría.
2. **Generación Automatizada:** Ejecución en lotes con soporte del flag `--dry-run` para validar prompts sin escribir en DB ni gastar créditos.
3. **Sanitización y Filtrado:** Exclusión de pares < 0.40, validación Pydantic e inserción ordenada `ingredient_a_id < ingredient_b_id`.

### 2.3 Prompts, Criterios de Curado y Respaldos
1. **Prompt Estructurado (JSON Mode):**
   > _"Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. Evalúa la afinidad organoléptica entre [Ingrediente A] y [Ingrediente B]. Responde estrictamente en JSON con la siguiente estructura: `{"affinity_score": float (0.00 a 1.00), "ai_rationale": string (máximo 250 caracteres en español explicativo)}`."_
2. **Curado Manual:** Muestreo aleatorio del 10% del dataset verificando coherencia gastronómica.
3. **Snapshot Previo:** `pg_dump -U postgres -d mapa_sabores -f backups/pre_seed_snapshot.sql`.
4. **Métricas de Aceptación:** Cobertura de al menos 80% con 4+ conexiones y 100% consistencia sintáctica.

### 2.4 Control de Alucinaciones y Workflow de Arbitraje
1. **Suite de Verificación (`scripts/verify_coherence.py`):** Pruebas de validación cruzada antes de autorizar la carga en producción.
2. **Matriz de Incompatibilidad Prohibida:** Listado de ~50 pares antagónicos conocidos (ej: _Pescado Blanco + Dulce de Leche_). Puntuaciones > 0.35 en estos pares fallan automáticamente.
3. **Control de Varianza:** Alerta de divergencia si la nota del LLM discrepa en > +-0.40 con FlavorDB.
4. **Arbitraje CLI (`./scripts/curate.py`):** Pares sospechosos se envían a `pairing_review_queue` con estado `'pending_review'`, donde el administrador los aprueba (`--approve`) o rechaza (`--reject`).

---

## 3. Especificación de la API REST (FastAPI)

### 3.1 Autenticación (`/api/v1/auth`)
* `POST /api/v1/auth/register`: Registro de nuevo usuario.
* `POST /api/v1/auth/login`: Autenticación y retorno de Access Token JWT.
* `POST /api/v1/auth/logout`: Revocación del refresh token.
* `GET /api/v1/auth/me`: Perfil del usuario autenticado.

### 3.2 Red y Grafo (`/api/v1/graph`)
* `GET /api/v1/graph`: Subgrafo paginado para `react-force-graph` (`limit` default 50, max 100, `offset`, `min_affinity`).
* `GET /api/v1/ingredients`: Lista paginada con filtro de búsqueda.
* `GET /api/v1/ingredients/{id}/pairings`: Vecinos directos (Top-N) y afinidades.

### 3.3 Evaluación Multi-Ingrediente e IA (`/api/v1/pairings`, `/api/v1/ai`)
* `POST /api/v1/pairings/evaluate`: Cálculo **determinístico** (matriz N x N, índice de sinergia 0-100% y elementos discordantes).
* `POST /api/v1/ai/suggest-replacement`: Sugerencia **generativa** de reemplazo para ingredientes discordantes.
* `POST /api/v1/ai/explain-pairing`: Explicación generativa organoléptica en vivo.

```json
// POST /api/v1/pairings/evaluate Body:
{ "ingredient_ids": [12, 45, 88] }

// Response 200 OK (Cálculo determinístico):
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
```

### 3.4 Servicio de Recetas y Sanitización de Payload
* `GET /api/v1/recipes/search?ingredient_ids=12,45,88`: Búsqueda con almacenamiento permanente en servidor y traducción al cachear (_Translation-on-Cache_).

```python
# app/services/recipe_sanitizer.py
import json

def sanitize_recipe_payload(raw_data: dict) -> dict:
    sanitized = {
        "id": raw_data.get("id"),
        "title": raw_data.get("title", "").strip(),
        "readyInMinutes": raw_data.get("readyInMinutes"),
        "servings": raw_data.get("servings"),
        "image": raw_data.get("image"),
        "summary": (raw_data.get("summary") or "")[:500],
        "extendedIngredients": [
            {
                "id": ing.get("id"),
                "name": ing.get("name"),
                "amount": ing.get("amount"),
                "unit": ing.get("unit")
            }
            for ing in raw_data.get("extendedIngredients", [])
        ],
        "analyzedInstructions": raw_data.get("analyzedInstructions", [])
    }
    payload_str = json.dumps(sanitized, ensure_ascii=False)
    if len(payload_str.encode('utf-8')) > 30720: # Límite estricto de 30 KB
        sanitized["summary"] = sanitized["summary"][:200]
    return sanitized
```

### 3.5 Contratos Pydantic v2
```python
class PairingEvaluationRequest(BaseModel):
    ingredient_ids: List[int] = Field(..., min_items=2, max_items=10)

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

---

## 4. Seguridad, Autenticación y Resiliencia Operativa

### 4.1 Hardening de Seguridad
1. **Hashing de Contraseñas:** Passlib con **Argon2id** (o `bcrypt` costo 12).
2. **Tokens JWT & Redis Blacklist:** `access_token` (30 min) y `refresh_token` HTTP-Only (7 días). Invalidation mediante Redis `revoked_token:<jti>` con TTL de 7 días (< 1ms latencia).
3. **Control Dual de Tasa (`slowapi`):** 60 req/min por IP anónima; 120 req/min por `user_id` autenticado (10 req/min para IA Free, 30 req/min Pro).

### 4.2 Resiliencia del Servicio de IA
1. **Timeout Estricto:** 3.0 segundos en llamadas HTTP a LLMs cloud.
2. **Reintentos Exponenciales:** Máximo 1 reintento en errores 5xx.
3. **Jerarquía de Fallback:** Gemini 1.5 Flash -> OpenAI GPT-4o-mini -> Fallback local a PostgreSQL `ai_rationale` (100% disponibilidad).
4. **Monitoreo SLA:** Registro en JSON logs y alerta si la tasa de fallback supera el 5% en 15 minutos.

---

## 5. Diseño Frontend y Experiencia Visual (React / Vite)

```
+-----------------------------------------------------------------------------------+
| Navbar: Logo  |  Buscador: [Tomate x] [Albahaca x]  |  Filtros  |  [ Evaluar ]    |
+------------------------------------------------------+----------------------------+
|                                                      |   Panel Lateral (Drawer)   |
|               AREA PRINCIPAL DEL GRAFO               |                            |
|                (react-force-graph-2d)                |    Sinergia Global: 92%    |
|                                                      |  [==================  ]    |
|              ( QUESO )                               |                            |
|                  | (Verde 92%)                       |  Matriz de Compatibilidad: |
|                  v                                   |  * Tomate + Albahaca: 98%  |
|             ( TOMATE ) ============= ( ALBAHACA )    |  * Tomate + Queso: 92%     |
|                  |      (Verde 98%)                  |                            |
|                  : (Rojo punteado 35%)               |  [ Explicación de Chef ]   |
|                  v                                   |  [ 14 Recetas ]            |
|            ( CHOCOLATE )                             |                            |
+------------------------------------------------------+----------------------------+
```

### 5.1 Landing Search y Visualización Progresiva
1. **Landing de Búsqueda:** Buscador central con etiquetas de tendencias (`[Tomate y Albahaca]`, `[Palta y Limón]`).
2. **Grafo con 1 Ingrediente:** Nodo en el centro con aristas radiales a sus Top 5-8 vecinos de mayor afinidad.
3. **Grafo con 2 Ingredientes:** Arista de afinidad coloreada (Verde >75%) e iluminación intensa (100% opacidad) en los ingredientes vecinos que combinan bien con ambos.
4. **Ingrediente Discordante:** Arista en **ROJO punteado** (<45%) y atenuación visual (30% opacidad) en los nodos periféricos.

### 5.2 Componentes del Panel Lateral (Drawer)
* Medidor Porcentual de Sinergia Global (Synergy Gauge).
* Matriz de afinidades cruzadas N x N.
* Alerta de elemento discordante con botón de sugerencia de reemplazo con IA.

---

## 6. Modelo Freemium y Niveles de Suscripción

| Característica / Funcionalidad | Tier Gratuito (Free) | Tier Pago (Pro / Premium) |
| :--- | :--- | :--- |
| **Límite de Ingredientes por Búsqueda** | **Hasta 3 ingredientes** (tríadas gastronómicas) | **Hasta 10 ingredientes** (platos complejos) |
| **Visualización de Grafo y Sinergia** | Incluido Acceso Completo | Incluido Acceso Completo |
| **Explicación de Chef con IA** | Incluido (Límite diario) | Ilimitado |
| **Búsqueda de Recetas** | Incluido | Incluido |
| **Guardado en Servidor (Workspace)** | Solo Combinaciones Favoritas | **Combinaciones + Recetas con Notas** |
| **Exportación de Datos (Export & API)** | No disponible | **Exportar a Texto Plano, JSON y API Key** |

---

## 7. Estrategia de Pruebas (TDD) y Pipeline CI/CD

### 7.1 Testing TDD (Red -> Green -> Refactor)
* **Backend:** `pytest` + `pytest-asyncio` + `httpx` (cobertura mínima 85%).
* **Frontend:** `Vitest` + `React Testing Library` + `MSW`.

### 7.2 GitHub Actions CI/CD (`.github/workflows/ci.yml`)
```yaml
name: CI / Integration Pipeline

on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres_secret
          POSTGRES_DB: mapa_sabores_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run Alembic Migrations Check
        run: |
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres_secret@localhost:5432/mapa_sabores_test
      - name: Run Pytest with Coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=term-missing
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres_secret@localhost:5432/mapa_sabores_test

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm ci
      - name: Run Vitest Tests
        run: |
          cd frontend
          npm run test:run
```

---

## 8. Matriz de Riesgos y Análisis de Viabilidad Económica

### 8.1 Matriz de Riesgos
| Riesgo Identificado | Impacto | Mitigación Planificada |
| :--- | :--- | :--- |
| **Agotamiento de cuota en API de Recetas** | Medio | Tabla caché en PostgreSQL (`recipe_search_cache`); depuración a 30 KB. |
| **Saturación visual en el grafo** | Alto | Subgrafo paginado (`GET /graph?limit=50`) y `min_affinity` por defecto en 0.50. |
| **Alucinaciones o latencia de IA** | Medio | Prompting estructurado, suite `verify_coherence.py`, cola de revisión `pairing_review_queue` y fallback a `ai_rationale`. |
| **Demoras en modelo local (Ollama)** | Bajo | El modelo local es un _Stretch Goal_ opcional; la arquitectura cloud se mantiene 100% funcional. |

### 8.2 Viabilidad Económica
| Nivel de Escala | Usuarios Activos / Mes | API Recetas (Con Caché DB) | API IA (Gemini Flash / GPT-4o-mini) | Hosting & PostgreSQL | **Costo Total Estimado** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MVP / Defensa Tesis** | 1 - 100 | **$0.00** (Free Tier) | **$0.00** (Free Tier) | **$0.00** (Render / Supabase Free) | **$0.00 USD / mes** |
| **Producción Inicial** | 1,000 | **$0.00** (Caché DB absorbe 95%) | ~$0.15 USD | $0 - $5.00 USD | **~$0.15 - $5.00 USD / mes** |
| **Escala Media** | 25,000 | ~$29.00 USD (Spoonacular Builder) | ~$2.50 USD | ~$10.00 USD (DB 5GB) | **~$41.50 USD / mes** |