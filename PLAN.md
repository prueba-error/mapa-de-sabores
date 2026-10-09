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
       |   * Sprint 3: REST API, Sinergia N x N, Favoritos & Base UI  |
       |   * Sprint 4: UI 3 Vistas, IA Online, QA & Defensa           |
       +--------------------------------------------------------------+
```

---

## 2. Detalle de Sprints y Criterios de Aceptación (Definition of Done)

### Fase 1: Cimientos, Data Pipeline y Prototipado Temprano (Mes 1)

#### **Sprint 1 (Semanas 1-2) — Cimientos, DDL, Entorno Local y Auth Base**
* **Objetivo:** establecer la infraestructura base y el esquema de base de datos relacional.
* **Entregables:**
  * PostgreSQL 16 configurado en `docker-compose.yml`.
  * Esquema DDL aplicado: `categories`, `ingredients`, `flavor_pairings`, `users`, `favorite_combinations`, `favorite_combination_items`, `pairing_review_queue`.
  * Migración inicial de Alembic en `backend/alembic/versions/`.
  * Endpoints de auth (`register`, `login`, `me`) funcionando de punta a punta.
* **Tiempo reservado (integración/comprensión):** ~2 días para leer y poder explicar el esquema DDL generado y el flujo de JWT antes de avanzar al Sprint 2.
* **Criterios de Aceptación (TDD):** tests en `pytest` verificando la restricción `ingredient_a_id < ingredient_b_id`, las consultas bidireccionales de vecinos, y emisión/validación de JWT.

#### **Sprint 2 (Semanas 3-4) — Pipeline Offline de Datos, Curación y Spike Frontend**
* **Objetivo:** procesar el dataset empírico de Food Pairing derivado de FlavorDB y Ahn et al., generar explicaciones organolépticas asistidas por IA, curar los casos dudosos y validar el renderizado del grafo.
* **Entregables:**
  * Datasets moleculares en `data/compounds.json` (82 compuestos volátiles) y `data/ingredients.json` (>330 ingredientes categorizados con nombres localizados en español `name_es`).
  * `scripts/seed_flavor_network.py` con flag `--dry-run`, cálculo determinista de afinidad mediante similitud de Jaccard y recuento molecular ($N_s$), generación de `flavor_profile` (6 ejes fijos) y enriquecimiento textual asistido por IA (`ai_rationale`).
  * Matriz de ~50 pares antagónicos conocidos (`scripts/antagonistic_pairs.py`) cargada como regla de validación de seguridad.
  * `scripts/curate.py` con soporte `--list / --approve / --reject / --stats` sobre `pairing_review_queue`.
  * Carga inicial del dataset (>330 ingredientes, piso de score 0.15 y preservación de pares débiles 0.15-0.45 para el modo "Peores"), con la cola de revisión en cero pendientes antes de cerrar el sprint.
  * Informe de auditoría y fundamentación teórica en `docs/JUSTIFICACION_TEORICA_FOOD_PAIRING.md`.
  * Spike en React con `react-force-graph-2d` renderizando datos mock estáticos, para evaluar velocidad en Canvas a 60 FPS.
* **Tiempo reservado:** ~1,5 días de curación manual real (pares marcados por la matriz antagónica + muestra aleatoria), más ~1 día de ajuste de la física del grafo en el spike.
* **Criterios de Aceptación:** dataset cargado sin pares pendientes de revisión y con todos los ingredientes con perfil de 6 ejes; spike del grafo corriendo a ~60 FPS con datos mock.

---

### Fase 2: Backend Core y Frontend Completo (Mes 2)

#### **Sprint 3 (Semanas 5-6) — REST API, Sinergia N x N y Favoritos**
* **Objetivo:** implementar la lógica de sinergia y la gestión de combinaciones favoritas.
* **Entregables:**
  * Endpoints: `GET /api/v1/graph` (paginado, `limit=50`, `sort=best|worst|all`), `GET /api/v1/ingredients`, `GET /api/v1/ingredients/{id}` (incluye `flavor_profile`), `GET /api/v1/ingredients/{id}/pairings` (con `sort=best|worst` para ranking de mejores/peores), `POST /api/v1/pairings/evaluate`.
  * Algoritmo determinístico de evaluación: índice de sinergia global como promedio de `affinity_score` sobre los pares del grupo con dato, indicador `coverage` (ej. 4 de 6 pares), matriz de pares cruzados NxN con celdas nulas y detección del ingrediente discordante (solo N ≥ 3; menor afinidad promedio contra el resto, calculada sobre los pares con dato).
  * **Base del frontend:** Vite + Tailwind, rutas `/explore`, `/ingredient/:id` y `/lab`, `LabContext`, cliente de API tipado y Vista 1 conectada a `GET /api/v1/graph` (sin filtros avanzados), con Vitest configurado y un test de humo del cliente.
  * Endpoints de favoritos: `GET` / `POST` / `DELETE /api/v1/users/me/favorites`, modelados como conjuntos de ingredientes (`favorite_combinations`).
* **Tiempo reservado:** ~1 día para verificar que los contratos Pydantic del backend coincidan exactamente con lo que consume el frontend (punto típico de fricción entre piezas generadas por separado).
* **Criterios de Aceptación (TDD):** pruebas unitarias en `pytest` para la matemática de sinergia (incluidos pares sin dato, cobertura y el caso N=2) y para el guardado/recuperación de favoritos.

#### **Sprint 4 (Semanas 7-8) — Frontend 3 Vistas (Explorar, Ficha, Laboratorio), IA Online y Defensa**
* **Objetivo:** construir la interfaz interactiva completa dividida en 3 vistas principales, integrar la IA en línea y preparar la defensa académica.
* **Entregables:**
  * **Navbar & Navegación Modular:** Barra superior con pestañas (el estado compartido `LabContext` ya existe desde el Sprint 3).
  * **Vista 1 (Explorar Grafo):** Completar, sobre la base del Sprint 3, la visualización progresiva 2D con `react-force-graph-2d`, controles **Mejores / Todas / Peores**, slider de cantidad y botón **"Explorar extremos"**.
  * **Vista 2 (Ficha de Ingrediente):** Ficha sensorial con barras de `flavor_profile`, ranking de mejores/peores afinidades y **tabla comparativa de perfiles** para pares específicos.
  * **Vista 3 (Laboratorio de Combinaciones):** Constructor por **chips** interactivos, medidor de sinergia con indicador de cobertura, matriz cruzada $N \times N$ (celdas "sin dato") y alerta de ingrediente discordante.
  * Endpoints `POST /api/v1/ai/explain-pairing` y `POST /api/v1/ai/suggest-replacement`, con presupuesto total de 8 s y fallback a `ai_rationale` guardado o mensaje genérico (campo `source`).
  * Suite de tests `pytest` + `Vitest` corriendo en verde localmente.
  * Memoria técnica final y preparación de la defensa ante el tribunal.
* **Opcional (solo si sobra tiempo, no forma parte del Definition of Done):** endpoint `GET /api/v1/pairings/suggest-additions` y las dos listas correspondientes ("Para aumentar sinergia" / "Para experimentar") en la Vista 3, según la especificación ya resuelta en `SPEC.md`, Sección 3.2.1.
* **Tiempo reservado:** ~2 días de margen sin entregables nuevos, dedicados exclusivamente a pulir UX del grafo y a repasar la justificación de cada decisión de diseño de cara a la defensa.

---

## 3. Estructura del Repositorio

```
mapa-de-sabores/
├── backend/
│   ├── app/
│   │   ├── main.py            # entrypoint FastAPI, registra routers y CORSMiddleware
│   │   ├── config.py          # carga de variables de entorno
│   │   ├── database.py        # engine y sesión async de SQLAlchemy
│   │   ├── security.py        # hashing (Argon2id) y JWT
│   │   ├── models/             # modelos SQLAlchemy (tablas del DDL de SPEC.md)
│   │   ├── schemas/            # esquemas Pydantic de request/response
│   │   ├── routers/            # auth.py, graph.py, ingredients.py, pairings.py, ai.py, favorites.py
│   │   └── services/           # llm_provider.py, synergy.py, curation.py
│   ├── alembic/versions/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # Explore.jsx, IngredientDetail.jsx, Lab.jsx
│   │   ├── components/
│   │   ├── context/              # LabContext.jsx
│   │   └── api/                   # cliente HTTP tipado hacia el backend
│   ├── Dockerfile
│   └── package.json
├── scripts/
│   ├── seed_flavor_network.py
│   ├── curate.py
│   └── backup.sh
├── backups/
├── docker-compose.yml
├── .env.example
└── README.md · PROYECTO.md · SPEC.md · PLAN.md
```

---

## 4. Secuencia de Kickoff del Código (Pasos Inmediatos para el Sprint 1)

1. **Configuración de Entorno Local:** crear `.env.example` y la infraestructura base de `docker-compose.yml` (PostgreSQL + FastAPI).
2. **Migración Inicial de Base de Datos:** inicializar Alembic y generar la migración DDL inicial (`001_initial_schema.py`).
3. **Scaffolding del Data Pipeline:** crear `scripts/seed_flavor_network.py` con el flag `--dry-run` para validar esquemas Pydantic sin gastar cuota de API.
4. **Implementación de Servicio de IA:** crear la interfaz agnóstica `LLMProvider` (adaptadores Gemini/OpenAI con modelo configurable por entorno, presupuesto total de 8 s, retries y fallback).
5. **Primeras Pruebas Unitarias TDD:** escribir las pruebas con `pytest` para la matemática determinística de `POST /api/v1/pairings/evaluate`.

---

## 5. Archivos de Configuración e Infraestructura

### 5.1 Variables de Entorno (`.env.example`)

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
GEMINI_MODEL=id_del_modelo_flash_vigente   # verificar en la documentación del proveedor
OPENAI_MODEL=id_del_modelo_mini_vigente    # verificar en la documentación del proveedor
LLM_TIMEOUT_SECONDS=8.0 # presupuesto total por solicitud (reintentos y cambio de proveedor incluidos)

# CORS (backend) y conexión al backend (frontend)
CORS_ORIGINS=http://localhost:5173 # lista separada por comas; agregar el dominio de producción cuando exista
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 5.2 Orquestación con Docker Compose (`docker-compose.yml`)

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: mapa_sabores_db
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    container_name: mapa_sabores_backend
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

  frontend:
    build: ./frontend
    container_name: mapa_sabores_frontend
    restart: always
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=${VITE_API_BASE_URL}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev -- --host 0.0.0.0

volumes:
  postgres_data:
```

Docker Compose lee `.env` para sustituir las variables `${...}`, de modo que las credenciales viven en un único lugar. El `healthcheck` evita que el backend intente migrar antes de que PostgreSQL esté listo. El servicio `frontend` monta el código como volumen para hot-reload y usa `--host 0.0.0.0` para que Vite escuche fuera del contenedor, no solo en `localhost`; `/app/node_modules` como volumen anónimo evita que el `node_modules` del host (si existe, con binarios de otro SO) pise al que se instaló dentro de la imagen.

### 5.3 Script de Snapshot y Restauración (`scripts/backup.sh`)

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
    docker exec -i mapa_sabores_db pg_dump -U postgres -d mapa_sabores --clean --if-exists > "$FILENAME"
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

El volcado usa `--clean --if-exists`, por lo que `restore` reemplaza los objetos existentes en lugar de chocar con ellos (y `docker exec -i`, sin `-t`, evita que la pseudo-terminal altere el archivo). Correr `scripts/backup.sh backup` antes de cada corrida masiva del pipeline de seed (Sprint 2), como red de seguridad ante datos corruptos por un error de curación.
