# Historial de Desarrollo (HISTORY.md)

Registro cronológico único de entregables mayores, decisiones técnicas acordadas y resolución de bloqueos, conforme a la Sección 9 de `AGENT.md`.

---

## Sprint 1: Cimientos, DDL, Entorno Local y Auth Base

* **Contexto:** Inicialización del entorno de desarrollo, esquema relacional DDL en PostgreSQL 16 con SQLAlchemy async / Alembic, y autenticación base según `SPEC.md` y `PLAN.md`.
* **Cambios realizados:**
  * Configuración del entorno local con `uv` (Python 3.13), `docker-compose.yml`, `.env.example`, `.gitignore` y `scripts/backup.sh`.
  * Modelado relacional completo en SQLAlchemy async (`Category`, `Ingredient`, `FlavorPairing`, `User`, `FavoriteCombination`, `FavoriteCombinationItem`, `PairingReviewQueue`).
  * Generación y ejecución de la migración inicial de Alembic (`001_initial_schema.py`) aplicando restricciones canónicas (`ingredient_a_id < ingredient_b_id`), integridad referencial en cascada, índices y constraints de validación.
  * Módulo de seguridad y endpoints de autenticación: hashing con Argon2id (`argon2-cffi`), emisión/validación de JWT (`PyJWT`), endpoints `POST /api/v1/auth/register`, `POST /api/v1/auth/login` y `GET /api/v1/auth/me`.
* **Decisiones y resolución de bloqueos:**
  * **Conflicto de puerto PostgreSQL:** Se detectó el servicio nativo `postgresql-x64-18` activo en el host (puerto 5432). Se reconfiguró el mapeo en `docker-compose.yml` a `${POSTGRES_PORT:-5433}:5432` y se ajustó la configuración por defecto de conexión en backend a 5433 para evitar colisiones sin alterar la red interna de Docker (`db:5432`).
  * **Validación de correos en Pydantic:** Se implementó validación por expresión regular nativa para evitar dependencias accesorias no estrictamente requeridas (`email-validator`).
  * **Aislamiento de sesiones en testing:** Se configuró `NullPool` en el motor de pruebas de `pytest-asyncio` para garantizar que las conexiones asíncronas no queden retenidas entre bucles de eventos en Windows.
* **Archivos afectados:** `pyproject.toml`, `uv.lock`, `docker-compose.yml`, `.env.example`, `backend/Dockerfile`, `backend/requirements.txt`, `backend/app/*`, `backend/alembic/*`, `backend/tests/*`.
* **Tests y verificaciones:**
  * `ruff check backend/` & `ruff format --check backend/`: 0 errores.
  * `mypy backend/app`: 0 errores en 17 archivos.
  * `pytest backend/tests/ -v`: 6/6 tests pasando (hashing Argon2id, ciclo JWT, flujo e2e auth con registro/duplicados/login/me, restricción `ingredient_a_id < ingredient_b_id`, consultas bidireccionales y restricciones de la cola de revisión).

