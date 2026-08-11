# Mapa de Sabores - Propuesta de Proyecto y Especificación Técnica

## Proyecto Final Desarrollo de Sistemas Web

**Alumno:** Diego Rafael Guaraz  
**Documento de Arquitectura y Especificación Técnica para Pares**

---

## 1. Resumen Ejecutivo

**Mapa de Sabores** es un sistema web interactivo de descubrimiento gastronómico basado en una arquitectura híbrida de _Base de Datos Relacional + Inteligencia Artificial (IA)_.

El proyecto resuelve el problema del maridaje e innovación culinaria mediante una representación en forma de un _Grafo de Sabores_ interactivo y dinámico. Permite a profesionales de la cocina y aficionados explorar combinaciones de ingredientes basados en afinidad química y culinaria, consultar recetas reales integradas y recibir justificaciones organolépticas generadas por modelos de lenguaje (LLM).

### Principales Pilares de Ingeniería
1. **Certeza en el Core (Base Relacional Estable):** La red de sabores reside en una base de datos PostgreSQL optimizada con índices compuestos bidireccionales. La estructura del grafo se define por datos curados y validados, no por generación inestable en tiempo real de un modelo de lenguaje.
2. **Pipeline de Datos Sintéticos Offline:** Un pipeline de ingeniería de prompts sobre LLMs compila y cura un dataset inicial de 200–300 ingredientes y miles de pares de afinidad.
3. **Capa de IA Desacoplada e Intercambiable:** Un servicio backend agnóstico en FastAPI permite alternar entre proveedores cloud (Google Gemini, OpenAI) y ejecución 100% local (Ollama / Llama 3.2 3B).
4. **Visualización React en 2D:** Renderizado dinámico de nodos y aristas mediante `react-force-graph-2d` con experiencia de usuario fluida y paneles laterales descriptivos.

---

## 2. Planteamiento del Problema y Objetivos

### 2.1 Problema Identificado
El descubrimiento de combinaciones de ingredientes (_flavor pairing_) tradicionalmente ha dependido de la intuición empírica o de enciclopedias culinarias estáticas. Aunque existen teorías científicas de maridaje de sabores (compartir compuestos aromáticos clave), no existen herramientas web abiertas e interactivas en español que combinen:
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

### 2.3 Justificación de Decisiones de Arquitectura
* **PostgreSQL vs. Neo4j:** Se optó por PostgreSQL debido a que en una red de 300 a 1,000 ingredientes las consultas de 1 o 2 saltos (_hops_) no justifican la sobrecarga operativa y de consumo de memoria de un motor de grafos nativo como Neo4j. Mediante índices compuestos y ordenamiento de IDs, Postgres resuelve estas consultas de forma directa (sin recorridos recursivos), con un costo operativo y de despliegue significativamente menor.
* **Arquitectura Híbrida de IA:** La IA no actúa como la base de datos (evitando alucinaciones o respuestas lentas en navegación UI), sino como un potenciador en dos fases: compilación de dataset en pipeline offline y generación de prosa culinaria en línea.

---

## 3. Arquitectura General y Entorno de Desarrollo Local

El sistema utiliza un patrón de _Arquitectura Multicapa Desacoplada_ (Frontend Client, Backend API, Relational Storage & External Services).

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
|   ├─ Auth Controller & Security (JWT / Passlib / Redis Blacklist)                 |
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
2. **Exploración y Filtrado:** El usuario selecciona un nodo (ej: _Tomate_). El frontend resalta vecinos y solicita `GET /api/v1/ingredients/{id}/pairings`.
3. **Explicación con IA (Online):** Al presionar "¿Por qué combinan?", el frontend invoca `POST /api/v1/ai/explain-pairing`. FastAPI utiliza la interfaz `LLMProvider` para generar un párrafo descriptivo con tono gastronómico.
4. **Recetas Relacionadas:** Al solicitar recetas para una combinación (ej: _Tomate + Albahaca + Ajo_), FastAPI consulta la caché local. Si no existe en caché, llama a la API de Spoonacular y guarda el resultado.

### 3.2 Configuración de Entorno (`.env.example`)
```ini
# Base de Datos & Caché
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secret
POSTGRES_DB=mapa_sabores
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres_secret@db:5432/mapa_sabores
REDIS_URL=redis://redis:6379/0

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

### 3.3 Orquestación con Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: mapa_sabores_db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres_secret
      POSTGRES_DB: mapa_sabores
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: mapa_sabores_redis
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    container_name: mapa_sabores_backend
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

volumes:
  postgres_data:
```

### 3.4 Script de Respaldo y Restauración (`scripts/backup.sh`)
```bash
#!/usr/bin/env bash
# scripts/backup.sh - Utilidad de Snapshot pg_dump / pg_restore
set -euo pipefail

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/snapshot_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

case "${1:-backup}" in
  backup)
    echo "📦 Generando snapshot de base de datos..."
    docker exec -t mapa_sabores_db pg_dump -U postgres -d mapa_sabores > "$FILENAME"
    echo "✅ Snapshot guardado exitosamente en: $FILENAME"
    ;;
  restore)
    if [ -z "${2:-}" ]; then
      echo "❌ Error: Debe especificar la ruta del archivo SQL a restaurar."
      echo "Uso: ./scripts/backup.sh restore ./backups/snapshot_YYYYMMDD_HHMMSS.sql"
      exit 1
    fi
    echo "⚠️ Restaurando base de datos desde $2..."
    docker exec -i mapa_sabores_db psql -U postgres -d mapa_sabores < "$2"
    echo "✅ Base de datos restaurada correctamente."
    ;;
  *)
    echo "Uso: ./scripts/backup.sh [backup|restore <archivo.sql>]"
    ;;
esac
```

---

## 4. Modelo de Datos y Estrategia de Grafos (PostgreSQL)

### 4.1 Esquema Relacional (DDL)
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

### 4.2 Lógica de Consulta Bidireccional
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

### 4.3 Estrategia de Migraciones con Alembic
* **Control de Versiones:** Cambios DDL registrados en `backend/alembic/versions/` con hashes secuenciales.
* **Ejecución Automática:** En el arranque del backend se invoca `alembic upgrade head`.
* **Rollback Seguro:** Métodos explícitos `upgrade()` y `downgrade()`.

---

## 5. Pipeline Offline y Origen del Dataset de Sabores

### 5.1 Fuentes Prácticas de Información
1. **La IA como Sintetizador de Conocimiento (Pipeline Offline):** Solicitudes en lote sobre LLMs (JSON Mode con Pydantic) evaluando combinaciones mediante `scripts/seed_flavor_network.py`.
2. **Datasets Abiertos Académicos:** FlavorDB / Flavornet (compuestos moleculares volátiles) y dataset del estudio de Yong-Yeol Ahn (_Nature Flavor Network_).
3. **Co-ocurrencia Estadística en Recetas:** Frecuencia de aparición conjunta en recetas procesadas.

### 5.2 Fases del Pipeline Offline
1. **Semilla de Ingredientes:** JSON/CSV con ~250 ingredientes clasificados por categoría.
2. **Generación Automatizada:** Ejecución en lotes con soporte del flag `--dry-run` para validar prompts sin escribir en DB ni gastar créditos.
3. **Sanitización y Filtrado:** Exclusión de pares $<0.40$, validación Pydantic e inserción ordenada `ingredient_a_id < ingredient_b_id`.

### 5.3 Prompts, Criterios de Curado y Respaldos
1. **Prompt Estructurado (JSON Mode):**
   > _"Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. Evalúa la afinidad organoléptica entre [Ingrediente A] y [Ingrediente B]. Responde estrictamente en JSON con la siguiente estructura: `{"affinity_score": float (0.00 a 1.00), "ai_rationale": string (máximo 250 caracteres en español explicativo)}`."_
2. **Curado Manual:** Muestreo aleatorio del 10% del dataset verificando coherencia gastronómica.
3. **Snapshot Previo:** `pg_dump -U postgres -d mapa_sabores -f backups/pre_seed_snapshot.sql`.
4. **Métricas de Aceptación:** Cobertura de al menos 80% con 4+ conexiones y 100% consistencia sintáctica.

### 5.4 Control de Alucinaciones y Workflow de Arbitraje
1. **Suite de Verificación (`scripts/verify_coherence.py`):** Pruebas de validación cruzada antes de autorizar la carga en producción.
2. **Matriz de Incompatibilidad Prohibida:** Listado de ~50 pares antagónicos conocidos (ej: _Pescado Blanco + Dulce de Leche_). Puntuaciones $>0.35$ en estos pares fallan automáticamente.
3. **Control de Varianza:** Alerta de divergencia si la nota del LLM discrepa en $>\pm 0.40$ con FlavorDB.
4. **Arbitraje CLI (`./scripts/curate.py`):** Pares sospechosos se envían a `pairing_review_queue` con estado `'pending_review'`, donde el administrador los aprueba (`--approve`) o rechaza (`--reject`).

---

## 6. Especificación de la API REST (FastAPI)

### 6.1 Autenticación (`/api/v1/auth`)
* `POST /api/v1/auth/register`: Registro de nuevo usuario.
* `POST /api/v1/auth/login`: Autenticación y retorno de Access Token JWT.
* `POST /api/v1/auth/logout`: Revocación del refresh token.
* `GET /api/v1/auth/me`: Perfil del usuario autenticado.

### 6.2 Red y Grafo (`/api/v1/graph`)
* `GET /api/v1/graph`: Subgrafo paginado para `react-force-graph` (`limit` default 50, max 100, `offset`, `min_affinity`).
* `GET /api/v1/ingredients`: Lista paginada con filtro de búsqueda.
* `GET /api/v1/ingredients/{id}/pairings`: Vecinos directos (Top-N) y afinidades.

### 6.3 Evaluación Multi-Ingrediente e IA (`/api/v1/pairings`, `/api/v1/ai`)
* `POST /api/v1/pairings/evaluate`: Cálculo **determinístico** (matriz $N \times N$, índice de sinergia 0-100% y elementos discordantes).
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

### 6.4 Servicio de Recetas y Sanitización de Payload
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

### 6.5 Contratos Pydantic v2
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

## 7. Seguridad, Autenticación y Resiliencia Operativa

### 7.1 Hardening de Seguridad
1. **Hashing de Contraseñas:** Passlib con **Argon2id** (o `bcrypt` costo 12).
2. **Tokens JWT & Redis Blacklist:** `access_token` (30 min) y `refresh_token` HTTP-Only (7 días). Invalidation mediante Redis `revoked_token:<jti>` con TTL de 7 días (< 1ms latencia).
3. **Control Dual de Tasa (`slowapi`):** 60 req/min por IP anónima; 120 req/min por `user_id` autenticado (10 req/min para IA Free, 30 req/min Pro).

### 7.2 Resiliencia del Servicio de IA
1. **Timeout Estricto:** 3.0 segundos en llamadas HTTP a LLMs cloud.
2. **Reintentos Exponenciales:** Máximo 1 reintento en errores 5xx.
3. **Jerarquía de Fallback:** Gemini 1.5 Flash ➔ OpenAI GPT-4o-mini ➔ Fallback local a PostgreSQL `ai_rationale` (100% disponibilidad).
4. **Monitoreo SLA:** Registro en JSON logs y alerta si la tasa de fallback supera el 5% en 15 minutos.

---

## 8. Diseño Frontend y Experiencia de Usuario (React / Vite)

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

### 8.1 Landing Search y Visualización Progresiva
1. **Landing de Búsqueda:** Buscador central con etiquetas de tendencias (`[Tomate y Albahaca]`, `[Palta y Limón]`).
2. **Grafo con 1 Ingrediente:** Nodo en el centro con aristas radiales a sus Top 5-8 vecinos de mayor afinidad.
3. **Grafo con 2 Ingredientes:** Arista de afinidad coloreada (Verde $>75\%$) e iluminación intensa (100% opacidad) en los ingredientes vecinos que combinan bien con ambos.
4. **Ingrediente Discordante:** Arista en **ROJO punteado** ($<45\%$) y atenuación visual (30% opacidad) en los nodos periféricos.

### 8.2 Componentes del Panel Lateral (Drawer)
* Medidor Porcentual de Sinergia Global (Synergy Gauge).
* Matriz de afinidades cruzadas $N \times N$.
* Alerta de elemento discordante con botón de sugerencia de reemplazo con IA.

---

## 9. Modelo Freemium y Niveles de Suscripción

| Característica / Funcionalidad | Tier Gratuito (Free) | Tier Pago (Pro / Premium) |
| :--- | :--- | :--- |
| **Límite de Ingredientes por Búsqueda** | **Hasta 3 ingredientes** (tríadas gastronómicas) | **Hasta 10 ingredientes** (platos complejos) |
| **Visualización de Grafo y Sinergia** | ✅ Acceso Completo | ✅ Acceso Completo |
| **Explicación de Chef con IA** | ✅ Incluido (Límite diario) | ✅ Ilimitado |
| **Búsqueda de Recetas** | ✅ Incluido | ✅ Incluido |
| **Guardado en Servidor (Workspace)** | ✅ Solo Combinaciones Favoritas | ✅ **Combinaciones + Recetas con Notas** |
| **Exportación de Datos (Export & API)** | ❌ No disponible | ✅ **Exportar a Texto Plano, JSON y API Key** |

### Justificación del Límite de 3 Ingredientes en el Tier Gratuito
Un límite de 3 ingredientes permite a los usuarios experimentar tríadas culinarias icónicas (ej: _Tríada Caprese: Tomate + Albahaca + Mozzarella_), comprobando el valor del sistema. Para chefs profesionales o mixólogos que diseñan recetas complejas de 5 a 8 componentes, el **Tier Pro** desbloquea la capacidad total.

---

## 10. Estrategia de Pruebas (TDD) y Pipeline de CI/CD

El proyecto adopta la disciplina de **Desarrollo Guiado por Pruebas (TDD)** (_Red ➔ Green ➔ Refactor_).

### 10.1 Stack de Testing
* **Backend:** `pytest` + `pytest-asyncio` + `httpx.AsyncClient` con base de datos PostgreSQL aislada en Docker (cobertura mínima del **85%** con `pytest-cov`).
* **Frontend:** `Vitest` + `React Testing Library` + `MSW` (Mock Service Worker).

### 10.2 Pipeline de CI/CD (GitHub Actions)
```yaml
# .github/workflows/ci.yml
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

## 11. Plan de Implementación Ágil (8 Sprints) y Kickoff

### 11.1 Plan Global de Sprints (2 Semanas c/u)
* **Sprint 1 (Sem. 1-2):** Cimientos, DDL Postgres, Redis, Docker Compose y Alembic.
* **Sprint 2 (Sem. 3-4):** Pipeline Offline (`seed_flavor_network.py` con `--dry-run`) y Spike temprano del Grafo React 2D.
* **Sprint 3 (Sem. 5-6):** Endpoints REST de Grafo y Evaluación Determinística $N \times N$.
* **Sprint 4 (Sem. 7-8):** Auth JWT (Argon2id + Redis Blacklist), `slowapi` y Caché de Recetas con sanitización 30 KB.
* **Sprint 5 (Sem. 9-10):** Frontend Grafo Progresivo e Intensidad Armónica (nodos 1, 2 y N).
* **Sprint 6 (Sem. 11-12):** Drawers, Recetas traducidas e integración online de LLMs.
* **Sprint 7 (Sem. 13-14):** Tiers Freemium, resiliencia 3s y fallbacks a DB.
* **Sprint 8 (Sem. 15-16):** QA, Pruebas E2E, memoria de tesis y preparación de defensa.

### 11.2 Secuencia de Kickoff del Código (Sprint 1)
1. **Entorno Local:** Crear `.env.example`, `docker-compose.yml` y `scripts/backup.sh`.
2. **Migración Inicial:** Inicializar `Alembic` y generar migración DDL inicial.
3. **Scaffolding Pipeline:** Estructurar `scripts/seed_flavor_network.py` con `--dry-run`.
4. **Servicio de IA:** Crear interfaz `LLMProvider` (timeout 3s, retries, fallback).
5. **Tests TDD Iniciales:** Pruebas `pytest` para `POST /api/v1/pairings/evaluate`.

---

## 12. Matriz de Riesgos y Análisis de Viabilidad Económica

### 12.1 Matriz de Riesgos
| Riesgo Identificado | Impacto | Mitigación Planificada |
| :--- | :--- | :--- |
| **Agotamiento de cuota en API de Recetas** | Medio | Tabla caché en PostgreSQL (`recipe_search_cache`); depuración a 30 KB. |
| **Saturación visual en el grafo** | Alto | Subgrafo paginado (`GET /graph?limit=50`) y `min_affinity` por defecto en 0.50. |
| **Alucinaciones o latencia de IA** | Medio | Prompting estructurado, suite `verify_coherence.py`, cola de revisión `pairing_review_queue` y fallback a `ai_rationale`. |
| **Demoras en modelo local (Ollama)** | Bajo | El modelo local es un _Stretch Goal_ opcional; la arquitectura cloud se mantiene 100% funcional. |

### 12.2 Viabilidad Económica
| Nivel de Escala | Usuarios Activos / Mes | API Recetas (Con Caché DB) | API IA (Gemini Flash / GPT-4o-mini) | Hosting & PostgreSQL | **Costo Total Estimado** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MVP / Defensa Tesis** | 1 – 100 | **$0.00** (Free Tier) | **$0.00** (Free Tier) | **$0.00** (Render / Supabase Free) | **$0.00 USD / mes** |
| **Producción Inicial** | 1,000 | **$0.00** (Caché DB absorbe 95%) | ~$0.15 USD | $0 – $5.00 USD | **~$0.15 – $5.00 USD / mes** |
| **Escala Media** | 25,000 | ~$29.00 USD (Spoonacular Builder) | ~$2.50 USD | ~$10.00 USD (DB 5GB) | **~$41.50 USD / mes** |

### 12.3 Argumentación para la Defensa Académica
Este análisis demuestra criterio de ingeniería de software enfocado en la _economía de recursos y optimización operativa_, probando que el sistema no solo es funcional y estéticamente atractivo, sino también _financieramente viable y preparado para producción real_.