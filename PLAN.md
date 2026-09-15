# Mapa de Sabores - Plan de Implementación Ágil (PLAN.md)

**Proyecto Final - Desarrollo de Sistemas Web**
**Alumno:** Diego Rafael Guaraz
**Duración Total:** 2 Meses (8 Semanas) / 4 Sprints de 2 Semanas

---

## 1. Hoja de Ruta Global en 4 Sprints

```
       +--------------------------------------------------------------+
       |   FASE 1: Cimientos, Data Pipeline & Spike Frontend (Mes 1)  |
       |   * Sprint 1: DDL Postgres, Alembic, Docker & Auth base      |
       |   * Sprint 2: Seed LLM + Curación & Spike Grafo React 2D     |
       +------------------------------+-------------------------------+
                                      |
                                      v
       +--------------------------------------------------------------+
       |   FASE 2: Backend Core & Frontend Completo (Mes 2)           |
       |   * Sprint 3: REST API Grafo, Sinergia N x N & Favoritos     |
       |   * Sprint 4: UI Grafo 2D, IA Online, QA Manual & Defensa    |
       +--------------------------------------------------------------+
```

---

## 2. Detalle de Sprints y Criterios de Aceptación (Definition of Done)

### Fase 1: Cimientos, Data Pipeline y Prototipado Temprano (Mes 1)

#### **Sprint 1 (Semanas 1-2) — Cimientos, DDL, Entorno Local y Auth Base**
* **Objetivo:** establecer la infraestructura base y el esquema de base de datos relacional.
* **Entregables:**
  * PostgreSQL 16 configurado en `docker-compose.yml`.
  * Esquema DDL aplicado: `categories`, `ingredients`, `flavor_pairings`, `users`, `user_favorite_pairings`, `pairing_review_queue`.
  * Migración inicial de Alembic en `backend/alembic/versions/`.
  * Endpoints de auth (`register`, `login`, `me`) funcionando de punta a punta.
* **Tiempo reservado (integración/comprensión):** ~2 días para leer y poder explicar el esquema DDL generado y el flujo de JWT antes de avanzar al Sprint 2.
* **Criterios de Aceptación (TDD):** tests en `pytest` verificando la restricción `ingredient_a_id < ingredient_b_id`, las consultas bidireccionales de vecinos, y emisión/validación de JWT.

#### **Sprint 2 (Semanas 3-4) — Pipeline Offline de Datos, Curación y Spike Frontend**
* **Objetivo:** generar el dataset inicial de sabores asistido por IA, curar manualmente los casos dudosos, y validar el motor de renderizado gráfico.
* **Entregables:**
  * `scripts/seed_flavor_network.py` con flag `--dry-run` y prompts estructurados en JSON Mode.
  * Matriz de ~50 pares antagónicos conocidos, cargada como regla de validación.
  * `scripts/curate.py` con soporte `--list / --approve / --reject` sobre `pairing_review_queue`.
  * Carga inicial del dataset (~200 ingredientes, ~1.000 relaciones), con la cola de revisión en cero pendientes antes de cerrar el sprint.
  * Spike en React con `react-force-graph-2d` renderizando datos mock estáticos, para evaluar velocidad en Canvas.
* **Tiempo reservado:** ~1 día de curación manual real de los pares marcados (no delegable a IA), más ~1 día de ajuste de la física del grafo en el spike.
* **Criterios de Aceptación:** dataset cargado sin pares pendientes de revisión; spike del grafo corriendo a ~60 FPS con datos mock.

---

### Fase 2: Backend Core y Frontend Completo (Mes 2)

#### **Sprint 3 (Semanas 5-6) — REST API, Sinergia N x N y Favoritos**
* **Objetivo:** implementar la lógica de sinergia y la gestión de combinaciones favoritas.
* **Entregables:**
  * Endpoints: `GET /api/v1/graph` (paginado, `limit=50`), `GET /api/v1/ingredients`, `GET /api/v1/ingredients/{id}/pairings`, `POST /api/v1/pairings/evaluate`.
  * Algoritmo determinístico de evaluación: índice de sinergia global (0–100%), matriz de pares cruzados NxN y detección del ingrediente discordante.
  * Endpoints de favoritos: `GET` / `POST /api/v1/users/me/favorites`.
* **Tiempo reservado:** ~1 día para verificar que los contratos Pydantic del backend coincidan exactamente con lo que consume el frontend (punto típico de fricción entre piezas generadas por separado).
* **Criterios de Aceptación (TDD):** pruebas unitarias en `pytest` para la matemática de sinergia y para el guardado/recuperación de favoritos.

#### **Sprint 4 (Semanas 7-8) — Frontend Grafo Progresivo, IA Online, QA y Defensa**
* **Objetivo:** construir la interfaz interactiva completa, integrar la IA en línea, y preparar la defensa académica.
* **Entregables:**
  * Landing page de búsqueda con sugerencias rápidas.
  * Visualización progresiva del grafo (1, 2 y N ingredientes) según lo especificado en `PROYECTO.md`, Sección 5.2.
  * Panel lateral (Drawer): medidor de sinergia, matriz NxN, alerta de elemento discordante.
  * Endpoints `POST /api/v1/ai/explain-pairing` y `POST /api/v1/ai/suggest-replacement`, con timeout de 3.0s y fallback a `ai_rationale`.
  * Suite de tests `pytest` + `Vitest` corriendo en verde localmente. La automatización de estos tests en un pipeline de CI/CD queda planteada como trabajo futuro (ver `PROYECTO.md`, Sección 9).
  * Memoria técnica final y preparación de la defensa ante el tribunal.
* **Tiempo reservado:** ~2 días de margen sin entregables nuevos, dedicados exclusivamente a pulir UX del grafo y a repasar la justificación de cada decisión de diseño de cara a la defensa.

---

## 3. Secuencia de Kickoff del Código (Pasos Inmediatos para el Sprint 1)

1. **Configuración de Entorno Local:** crear `.env.example` y la infraestructura base de `docker-compose.yml` (PostgreSQL + FastAPI).
2. **Migración Inicial de Base de Datos:** inicializar Alembic y generar la migración DDL inicial (`001_initial_schema.py`).
3. **Scaffolding del Data Pipeline:** crear `scripts/seed_flavor_network.py` con el flag `--dry-run` para validar esquemas Pydantic sin gastar cuota de API.
4. **Implementación de Servicio de IA:** crear la interfaz agnóstica `LLMProvider` (adaptadores Gemini/OpenAI, timeout 3s, retries y fallback).
5. **Primeras Pruebas Unitarias TDD:** escribir las pruebas con `pytest` para la matemática determinística de `POST /api/v1/pairings/evaluate`.

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

Correr `scripts/backup.sh backup` antes de cada corrida masiva del pipeline de seed (Sprint 2), como red de seguridad ante datos corruptos por un error de curación.
