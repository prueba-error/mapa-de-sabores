# Mapa de Sabores - Plan de Implementación Ágil Acotado (PLAN.md)

**Proyecto Final - Desarrollo de Sistemas Web**  
**Alumno:** Diego Rafael Guaraz  
**Duración Total:** 2 Meses (8 Semanas) / 4 Sprints de 2 Semanas (Versión Acotada - Opción 2)  

---

## 1. Hoja de Ruta Global en 4 Sprints (2 Meses)

```
       +--------------------------------------------------------------+
       |   FASE 1: Cimientos, Data Pipeline & Spike Frontend (Mes 1)  |
       |   * Sprint 1: DDL Postgres, Alembic & Entorno Docker         |
       |   * Sprint 2: Seed LLM / JSON & Spike Grafo React 2D         |
       +------------------------------+-------------------------------+
                                      |
                                      v
       +--------------------------------------------------------------+
       |   FASE 2: Backend Core, Auth Simplificada & Recetas (Mes 2)  |
       |   * Sprint 3: REST API Grafo, Sinergia N x N, Auth JWT & Caché|
       |   * Sprint 4: UI Grafo 2D, IA Online, CI/CD & Defensa        |
       +--------------------------------------------------------------+
```

---

## 2. Detalle de Sprints y Criterios de Aceptación (Definition of Done)

### Fase 1: Cimientos, Data Pipeline y Prototipado Temprano (Mes 1)

#### **Sprint 1 (Semanas 1-2) — Cimientos, DDL y Entorno Local**
* **Objetivo:** Establecer la infraestructura base en contenedores y el esquema de base de datos relacional.
* **Entregables:**
  * Base de datos PostgreSQL 16 configurada en `docker-compose.yml`.
  * Esquema DDL aplicado con tablas `categories`, `ingredients`, `flavor_pairings` (con provenance), `users`, `user_favorite_pairings`, `recipes` y `recipe_search_cache`.
  * Migración inicial de `Alembic` en `backend/alembic/versions/`.
* **Criterios de Aceptación (TDD):** Tests unitarios en `pytest` verificando las restricciones DDL (`ingredient_a_id < ingredient_b_id`) y las consultas bidireccionales de vecinos resueltas en verde.

#### **Sprint 2 (Semanas 3-4) — Pipeline Offline de Datos y Spike Frontend**
* **Objetivo:** Generar el dataset inicial de sabores asistido por IA y validar el motor de renderizado gráfico.
* **Entregables:**
  * Script `scripts/seed_flavor_network.py` con soporte para el flag `--dry-run` y prompts estructurados en JSON Mode.
  * Suite de control de calidad `scripts/verify_coherence.py` para asegurar validez de scores (0.0 a 1.0) y coherencia gastronómica.
  * Carga inicial del dataset curado (~200 ingredientes y ~1,000 relaciones).
  * Prototipo temprano (_Spike_) en React con `react-force-graph-2d` renderizando datos mock estáticos para evaluar velocidad en HTML5 Canvas.

---

### Fase 2: Backend Core, Autenticación y Frontend Completo (Mes 2)

#### **Sprint 3 (Semanas 5-6) — REST API, Sinergia N x N, Auth JWT & Caché de Recetas**
* **Objetivo:** Implementar la lógica matemática de sinergia, la autenticación simplificada y la gestión de recetas.
* **Entregables:**
  * Endpoints REST: `GET /api/v1/graph` (paginado con `limit=50`), `GET /api/v1/ingredients` y `POST /api/v1/pairings/evaluate`.
  * Algoritmo determinístico de evaluación: cálculo del Índice de Sinergia Global (0-100%), matriz de pares cruzados N x N y detección del elemento discordante (_clashing element_).
  * Autenticación JWT de sesión única: Endpoints `/api/v1/auth/register`, `/api/v1/auth/login` y `/api/v1/auth/me` con hashing Argon2id/bcrypt.
  * Cliente HTTP para Spoonacular con *Translation-on-Cache* (LLM traduce una sola vez al guardar) e inyección de `sanitize_recipe_payload` (recorte a 30 KB por receta).
* **Criterios de Aceptación (TDD):** Pruebas unitarias en `pytest` para la matemática determinística de sinergia y la emisión/validación de tokens JWT.

#### **Sprint 4 (Semanas 7-8) — Frontend Grafo Progresivo, IA Online, CI/CD y Defensa Académica**
* **Objetivo:** Construir la interfaz interactiva completa, integrar fallbacks de IA, automatizar pruebas y presentar la tesis.
* **Entregables:**
  * Landing page de búsqueda con sugerencias rápidas de tendencias (`[Tomate y Albahaca]`, `[Palta y Limón]`).
  * Visualización dinámica progresiva del grafo en React:
    * 1 Ingrediente: Nodo central con aristas radiales a Top 5-8 vecinos.
    * 2 Ingredientes: Arista coloreada por nivel de afinidad (Verde >75%) e iluminación intensa (opacidad 100%) en ingredientes vecinos que combinan con ambos.
    * Ingrediente discordante: Arista en ROJO punteado (<45%) y atenuación periférica (opacidad 30%).
  * Panel lateral (_Drawer_): Medidor porcentual de sinergia, matriz N x N y alerta de elemento discordante.
  * Endpoints generativos en tiempo real: `POST /api/v1/ai/explain-pairing` y `POST /api/v1/ai/suggest-replacement` con timeout de 3.0s y fallback a PostgreSQL `ai_rationale`.
  * Pipeline de CI/CD en GitHub Actions (`.github/workflows/ci.yml`) ejecutando `alembic upgrade head`, `pytest` y `Vitest`.
  * Memoria técnica final y preparación de la defensa ante el tribunal académico.

---

## 3. Secuencia de Kickoff del Código (Pasos Inmediatos para el Sprint 1)

Para arrancar el desarrollo del proyecto de forma inmediata y ordenada, seguir estos 5 pasos:

1. **Configuración de Entorno Local:** Crear `.env.example` y la infraestructura base de `docker-compose.yml` (PostgreSQL + FastAPI).
2. **Migración Inicial de Base de Datos:** Inicializar `Alembic` y generar la migración DDL inicial (`001_initial_schema.py`).
3. **Scaffolding del Data Pipeline:** Crear `scripts/seed_flavor_network.py` con el flag `--dry-run` para validar esquemas Pydantic sin gastar cuota de API.
4. **Implementación de Servicio de IA:** Crear la interfaz agnóstica `LLMProvider` (adaptadores Gemini/OpenAI, timeout 3s, retries y fallback).
5. **Primeras Pruebas Unitarias TDD:** Escribir las pruebas con `pytest` para la matemática determinística de `POST /api/v1/pairings/evaluate`.

---

## 4. Archivos de Configuración e Infraestructura

### 4.1 Variables de Entorno (`.env.example`)
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
ACCESS_TOKEN_EXPIRE_DAYS=7

# Servicios de IA Externa
GEMINI_API_KEY=tu_google_gemini_api_key
OPENAI_API_KEY=tu_openai_api_key
LLM_PRIMARY_PROVIDER=gemini # "gemini" | "openai"
LLM_TIMEOUT_SECONDS=3.0

# API de Recetas
SPOONACULAR_API_KEY=tu_spoonacular_api_key
```

### 4.2 Orquestación con Docker Compose (`docker-compose.yml`)
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
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

volumes:
  postgres_data:
```

### 4.3 Script de Snapshot y Restauración (`scripts/backup.sh`)
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
    echo "Generando snapshot de base de datos..."
    docker exec -t mapa_sabores_db pg_dump -U postgres -d mapa_sabores > "$FILENAME"
    echo "Snapshot guardado exitosamente en: $FILENAME"
    ;;
  restore)
    if [ -z "${2:-}" ]; then
      echo "Error: Debe especificar la ruta del archivo SQL a restaurar."
      echo "Uso: ./scripts/backup.sh restore ./backups/snapshot_YYYYMMDD_HHMMSS.sql"
      exit 1
    fi
    echo "Restaurando base de datos desde $2..."
    docker exec -i mapa_sabores_db psql -U postgres -d mapa_sabores < "$2"
    echo "Base de datos restaurada correctamente."
    ;;
  *)
    echo "Uso: ./scripts/backup.sh [backup|restore <archivo.sql>]"
    ;;
esac
```
