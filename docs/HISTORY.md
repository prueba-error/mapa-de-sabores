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
* **Hito de Dominio (Kickoff Sprint 1 - Algoritmo de Sinergia NxN):**
  * Implementación mediante TDD del servicio determinístico en `backend/app/services/synergy.py`.
  * Esquemas Pydantic `EvaluatePairingsRequest`, `CoverageInfo`, `ClashingIngredient`, `SynergyEvaluationResponse` en `backend/app/schemas/synergy.py`.
  * Reglas de negocio cubiertas al 100%:
    * `synergy_score`: promedio simple escalado a 0-100 sobre pares con dato (`None` si no hay pares).
    * `coverage`: recuento de pares con dato vs total combinatorio $N(N-1)/2$.
    * `pairwise_matrix`: matriz simétrica $N \times N$ con diagonal nula y celdas sin dato en `null`.
    * `clashing_ingredients`: detección de ingredientes con afinidad media $< 0.45$ para $N \ge 3$ ordenados de menor a mayor (vacío para $N = 2$, aislados sin dato no participan).
  * 6 tests unitarios dedicados en `backend/tests/test_synergy.py` pasando en 0.05 s (suite total: 12 tests en verde).
* **Hito de Integración y Datos (Kickoff Sprint 1 - LLM Provider y Data Pipeline):**
  * Esquemas Pydantic en `backend/app/schemas/ai.py` (`FlavorProfileSchema` con 6 ejes normalizados 0.00-1.00, `BatchPairingItem`, `BatchPairingResponse`, `AIExplanationResponse`, `AIReplacementResponse`).
  * Servicio agnóstico `LLMService` en `backend/app/services/llm_provider.py` con adaptadores para Gemini y OpenAI vía `httpx.AsyncClient`, presupuesto estricto de 8.0s (`RNF3`), conmutación por error entre proveedores y fallbacks determinísticos.
  * Matriz curada de 50 pares antagónicos conocidos en `scripts/antagonistic_pairs.py` como filtro de seguridad contra alucinaciones del LLM.
  * Script de sembrado `scripts/seed_flavor_network.py` con flag `--dry-run` para simulación y auditoría sin costo de API ni escritura en base de datos.
* **Hito de Verdad Empírica y Afinidad Molecular (Food Pairing Científico):**
  * Desacoplamiento total del cálculo de afinidades de las alucinaciones de modelos de lenguaje: las afinidades se calculan de manera 100% determinista y matemática a partir de química de aromas real.
  * Incorporación de datasets científicos en `data/compounds.json` (82 moléculas volátiles clave clasificadas en 15 familias químicas con descriptores sensoriales) y `data/ingredients.json` (326 ingredientes clasificados en 17 categorías con nombres localizados en español `name_es` y perfiles moleculares derivados de FlavorDB y Ahn et al., Nature 2011).
  * Redacción del documento formal de fundamentación científica y metodológica en `docs/JUSTIFICACION_TEORICA_FOOD_PAIRING.md`, detallando el índice de similitud de Jaccard, el recuento de moléculas compartidas ($N_s$), la fórmula ponderada calibrada ($S_{AB}$) y el rol exclusivo del LLM como redactor elocuente (`ai_rationale`).
  * Refactorización completa de `scripts/seed_flavor_network.py` para cargar los datasets en disco, aplicar `calculate_molecular_affinity()` y procesar los ingredientes de forma determinista y reproducible.
  * Verificación técnica con `ruff check` (100% limpio), `mypy --explicit-package-bases` (0 errores en 32 archivos) y tests unitarios en verde.

---

## Sprint 2: Curación Editorial, Data Pipeline y Spike Frontend

* **Contexto:** Implementación de la gestión editorial de `pairing_review_queue` (Human-in-the-Loop) y construcción del spike interactivo en React para validar el rendimiento a 60 FPS de `react-force-graph-2d`.
* **Cambios realizados:**
  * **Servicio de Curación (`backend/app/services/curation.py`):** Lógica de negocio para `list_pending`, `approve` (migra a `flavor_pairings` con `source_type='manual_review'` y permite reajuste de score/prosa), `reject` (marca como descartado) y `get_stats` con tasa de descarte de la auditoría aleatoria.
  * **CLI de Curación (`scripts/curate.py`):** Herramienta de terminal con comandos `--list`, `--approve <id>`, `--reject <id>` y `--stats` para la labor del alumno curador.
  * **Suite de Pruebas TDD (`backend/tests/test_curation_service.py`):** Cobertura completa del ciclo de vida de curación y restricciones de estado.
  * **Spike Frontend React 2D (`frontend/`):**
    * Inicialización de la aplicación frontend con Vite y React.
    * Instalación e integración de `react-force-graph-2d`, `lucide-react`, `clsx` y `tailwind-merge`.
    * Datos estáticos mock representativos en `frontend/src/data/mockGraph.js` (22 nodos y aristas con tres niveles de afinidad y notas aromáticas).
    * Componente interactivo `frontend/src/App.jsx` con panel lateral de control (filtros *Todas / Mejores / Peores*, slider de piso de afinidad, selección y centrado suave de nodo, leyenda de colores y tooltip reactivo de maridajes).
    * Build de producción de Vite verificado con éxito (`dist/` generado en 19.8s).
* **Tests y verificaciones:**
  * `ruff check scripts/ backend/`: 100% limpio.
  * `mypy --explicit-package-bases scripts/ backend/`: 0 errores en 35 archivos fuente.
  * `pytest backend/tests/`: 19/19 tests pasando con PostgreSQL activo.
  * `npm --prefix frontend run build`: compilación de producción de Vite limpia y verificada.
* **Hito Final de Datos, Persistencia y Documentación Técnica (Cierre Sprint 2):**
  * **Expansión y Catalogación del Dataset:** Ampliación a **360 ingredientes únicos** clasificados en 17 categorías y mapeados contra la biblioteca de 82 compuestos volátiles en `data/compounds.json`. Reconstrucción y ordenamiento alfabético de `catalogo_ingredientes.txt`.
  * **Monografías Científicas y Bromatológicas:** Incorporación de documentos de sustento cromatográfico en `docs/`: `datos_carne.md` (cortes vacunos magros/grasos/colágeno), `datos_ddl.md` (dulce de leche, catálisis Maillard), `datos_salsa_ostras.md` (hidrólisis péptidos y volátiles marinos), `datos_soja_texturizada.md` (termoextrusión y lipoxigenasa) y `justificacion_evaluacion_sinergia.md` (matemática de evaluación $N \times N$, cobertura, celdas nulas y cálculo on-the-fly).
  * **Ajuste de UX/UI en Spike Frontend:** Corrección del layout en `frontend/src/index.css` y `frontend/src/App.jsx` para evitar colapso de ancho del panel lateral en Flexbox (`flexShrink: 0`, `minWidth: 0`).
  * **Persistencia Real a PostgreSQL:** Implementación en `scripts/seed_flavor_network.py` del flag `--persist` y la rutina asíncrona de guardado en base de datos.
  * **Sembrado Exitoso de la Red:** Ejecución en PostgreSQL 16 persistiendo los 360 ingredientes, sincronizando 2.078 maridajes directos en `flavor_pairings` (incluyendo más del 70% de pares débiles/contrastes para exploración) y 204 ítems en `pairing_review_queue` auditables vía `scripts/curate.py`.



