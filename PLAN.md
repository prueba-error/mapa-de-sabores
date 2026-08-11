# Mapa de Sabores - Plan de Implementación Ágil (PLAN.md)

**Proyecto Final - Desarrollo de Sistemas Web**  
**Alumno:** Diego Rafael Guaraz  
**Duración Total:** 3 Meses (12 Semanas) / 6 Sprints de 2 Semanas  

---

## 📅 1. Hoja de Ruta Global en 6 Sprints (3 Meses)

```
       ┌──────────────────────────────────────────────────────────────┐
       │   FASE 1: Cimientos, Pipeline de Datos & Prototipado (Mes 1)  │
       │   • Sprint 1: DDL Postgres, Redis, Alembic & Entorno Docker  │
       │   • Sprint 2: Seed LLM (--dry-run) & Spike Grafo React 2D    │
       └──────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
       ┌──────────────────────────────────────────────────────────────┐
       │   FASE 2: Backend Core, Auth & Caché de Recetas (Mes 2)      │
       │   • Sprint 3: REST API Grafo, Sinergia N x N & Pytest TDD     │
       │   • Sprint 4: Auth Argon2id, Redis Blacklist & Spoonacular 30k│
       └──────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
       ┌──────────────────────────────────────────────────────────────┐
       │   FASE 3: Frontend Progresivo, IA Online & Defensa (Mes 3)   │
       │   • Sprint 5: UI Grafo 2D, Intensidad Armónica & Drawers     │
       │   • Sprint 6: IA Online Fallbacks, CI/CD, QA & Tesis         │
       └──────────────────────────────────────────────────────────────┘
```

---

## 🎯 2. Detalle de Sprints y Criterios de Aceptación (Definition of Done)

### 🚀 Fase 1: Cimientos, Data Pipeline y Prototipado Temprano (Mes 1)

#### **Sprint 1 (Semanas 1-2) — Cimientos, DDL y Entorno Local**
* **Objetivo:** Establecer la infraestructura base en contenedores y el esquema de base de datos relacional.
* **Entregables:**
  * Base de datos PostgreSQL 16 y Redis 7 configuradas en `docker-compose.yml`.
  * Esquema DDL aplicado con tablas `categories`, `ingredients`, `flavor_pairings` (con provenance), `users`, `revoked_tokens`, `recipes`, `recipe_search_cache` y `pairing_review_queue`.
  * Migración inicial de `Alembic` en `backend/alembic/versions/`.
* **Criterios de Aceptación (TDD):** Tests unitarios en `pytest` verificando las restricciones DDL (`ingredient_a_id < ingredient_b_id`) y las consultas bidireccionales de vecinos resueltas en verde.

#### **Sprint 2 (Semanas 3-4) — Pipeline Offline de Datos y Spike Frontend**
* **Objetivo:** Generar el dataset inicial de sabores asistido por IA y validar el motor de renderizado gráfico.
* **Entregables:**
  * Script `scripts/seed_flavor_network.py` con soporte para el flag `--dry-run` y prompts estructurados en JSON Mode.
  * Suite de control de calidad `scripts/verify_coherence.py` y script de arbitraje CLI `./scripts/curate.py`.
  * Carga inicial del dataset curado (~250 ingredientes y ~1,500 relaciones).
  * Prototipo temprano (_Spike_) en React con `react-force-graph-2d` renderizando datos mock estáticos para evaluar velocidad en HTML5 Canvas.

---

### ⚙️ Fase 2: Backend Core, Autenticación y Caché de Recetas (Mes 2)

#### **Sprint 3 (Semanas 5-6) — Endpoints REST y Sinergia Determinística $N \times N$**
* **Objetivo:** Implementar la lógica matemática de compatibilidad multi-ingrediente 100% resuelta en PostgreSQL.
* **Entregables:**
  * Endpoints REST: `GET /api/v1/graph` (paginado con `limit=50`), `GET /api/v1/ingredients` y `POST /api/v1/pairings/evaluate`.
  * Algoritmo determinístico de evaluación: cálculo del Índice de Sinergia Global (0-100%), matriz de pares cruzados $N \times N$ y detección del elemento discordante (_clashing element_).
* **Criterios de Aceptación (TDD):** Cobertura de pruebas unitarias $> 85\%$ en `pytest` para la matemática de sinergia y el ordenamiento de respuestas Pydantic v2.

#### **Sprint 4 (Semanas 7-8) — Autenticación, Redis Blacklist y Caché de Recetas**
* **Objetivo:** Asegurar la API con tokens JWT revocables y proteger la cuota externa de la API de recetas.
* **Entregables:**
  * Autenticación segura: Passlib (Argon2id) + JWT `access_token` (30 min) y `refresh_token` (7 días en cookie HTTP-Only).
  * Revocación ultra-rápida: Middleware en FastAPI comprobando la clave `revoked_token:<jti>` en Redis en **< 1ms**.
  * Control dual de tasa de peticiones con `slowapi` (por IP anónima y por `user_id` autenticado).
  * Cliente HTTP para Spoonacular con *Translation-on-Cache* (LLM traduce una sola vez al guardar) e inyección de la rutina `sanitize_recipe_payload` (recorte estricto a 30 KB por receta).

---

### 🎨 Fase 3: Frontend Interactivo, IA Online y Entrega Final (Mes 3)

#### **Sprint 5 (Semanas 9-10) — Frontend Grafo Progresivo e Intensidad Armónica**
* **Objetivo:** Construir la interfaz de usuario interactiva y reactiva en tiempo real.
* **Entregables:**
  * Landing page de búsqueda con sugerencias rápidas de tendencias (`[Tomate y Albahaca]`, `[Palta y Limón]`).
  * Visualización dinámica progresiva del grafo en React:
    * 1 Ingrediente: Nodo central con aristas radiales a Top 5-8 vecinos.
    * 2 Ingredientes: Arista coloreada por nivel de afinidad (Verde $>75\%$) e iluminación intensa (opacidad 100%) en ingredientes vecinos que combinan con ambos.
    * Ingrediente discordante: Arista en ROJO punteado ($<45\%$) y atenuación periférica (opacidad 30%).
  * Panel lateral (_Drawer_): Medidor porcentual de sinergia, matriz $N \times N$ y alerta de elemento discordante.

#### **Sprint 6 (Semanas 11-12) — IA Online, Tiers Freemium, CI/CD y Defensa Académica**
* **Objetivo:** Finalizar la resiliencia del sistema, automatizar el control de calidad y presentar la tesis.
* **Entregables:**
  * Endpoints generativos en tiempo real: `POST /api/v1/ai/explain-pairing` y `POST /api/v1/ai/suggest-replacement`.
  * Resiliencia de IA: Timeout de 3.0s, máximo 1 reintento y fallback automático a PostgreSQL `ai_rationale`.
  * Control de límites por Tier (Free: 3 ingredientes, Pro: 10 ingredientes).
  * Pipeline de CI/CD en GitHub Actions (`.github/workflows/ci.yml`) ejecutando `alembic upgrade head`, `pytest` y `Vitest`.
  * Memoria técnica final y preparación de la defensa ante el tribunal académico.

---

## ⚡ 3. Secuencia de Kickoff del Código (Pasos Inmediatos para el Sprint 1)

Para arrancar el desarrollo del proyecto de forma inmediata y ordenada, seguir estos 5 pasos:

1. **Configuración de Entorno Local:** Crear `.env.example` y la infraestructura base de `docker-compose.yml` (PostgreSQL + Redis + FastAPI).
2. **Migración Inicial de Base de Datos:** Inicializar `Alembic` y generar la migración DDL inicial (`001_initial_schema.py`).
3. **Scaffolding del Data Pipeline:** Crear `scripts/seed_flavor_network.py` con el flag `--dry-run` para validar esquemas Pydantic sin gastar cuota de API.
4. **Implementación de Servicio de IA:** Crear la interfaz agnóstica `LLMProvider` (adaptadores Gemini/OpenAI, timeout 3s, retries y fallback).
5. **Primeras Pruebas Unitarias TDD:** Escribir las pruebas con `pytest` para la matemática determinística de `POST /api/v1/pairings/evaluate`.

---

## 🛠️ 4. Archivos de Configuración e Infraestructura

### 4.1 Variables de Entorno (`.env.example`)
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
