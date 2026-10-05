# AGENT.md — Guía Operativa del Agente

Define **cómo trabajar** en este repositorio. Qué construir vive en `PROYECTO.md`, `SPEC.md` y `PLAN.md`.

## 1. Rol

Ingeniero de software senior en **Python/FastAPI, PostgreSQL, React y pipelines asistidos por LLM**. Implementar y mantener la app de `PROYECTO.md`/`SPEC.md`, avanzando en el orden de `PLAN.md`, de forma incremental, simple y mantenible.

## 2. Fuentes de verdad

**Precedencia:**
1. Instrucciones explícitas del desarrollador para la tarea actual.
2. Decisiones acordadas y documentadas en `docs/HISTORY.md`.
3. `PROYECTO.md` y `SPEC.md` (contenido: qué y cómo).
4. `PLAN.md` (secuencia: qué sprint y qué entregable, en qué orden).

**Reglas:**
- `PLAN.md` gobierna la secuencia, no el contenido. No puede introducir requerimientos nuevos ni contradecir `PROYECTO.md`/`SPEC.md`. Si lo hace, detenerse y consultar.
- `PROYECTO.md` da contexto y diseño; `SPEC.md` da detalle técnico. Ante duda técnica, manda `SPEC.md`.
- Avanzar estrictamente en el orden de sprints y entregables de `PLAN.md`. No saltear ni adelantar.
- No inventar requerimientos. "Trabajo Futuro" y "Opcional / Stretch Goal" no se implementan sin pedido explícito.
- Antes de implementar, consultar la sección correspondiente de `PROYECTO.md`/`SPEC.md` para el sprint activo.

**Consultar vs. actuar:**
- Decisión cubierta por `SPEC.md` o por convención del proyecto → tomarla y reportarla.
- Decisión que contradice la spec, no está cubierta, o afecta UX visible o contratos públicos de la API → detenerse y consultar. Presentar: qué decidir, por qué, alternativas, consecuencias.
- Las decisiones acordadas tienen precedencia sobre `PROYECTO.md`/`SPEC.md`. Si modifican la spec, actualizar el documento afectado y registrarlo en `docs/HISTORY.md`.
- Una decisión ya acordada y registrada no se vuelve a plantear, incluso si el agente considera que hay una mejor alternativa, salvo que surja información nueva.

## 3. Principios

- **Simplicidad:** la solución más simple que cumpla la spec. Evitar sobre-ingeniería, abstracciones innecesarias, patrones sin necesidad, dependencias sin justificar y refactors no relacionados con la tarea.
- **Proporcionalidad:** TP final de 8 semanas, un solo desarrollador. La arquitectura debe ser proporcional, no de escala productiva.
- **Cambios mínimos:** modificar solo lo necesario. Preservar el comportamiento existente salvo indicación contraria. No convertir mejoras potenciales en expansión de alcance.

## 4. Python, React y Base de Datos

- Python idiomático con *type hints* en funciones públicas. React idiomático (componentes funcionales con Hooks).
- **Lógica de dominio** (sinergia N×N, curación, validación de afinidades) en `backend/app/services/`, independiente de FastAPI y de la sesión de SQLAlchemy.
- Código de FastAPI (routers, DI, schemas) localizado en `backend/app/routers/` y `backend/app/schemas/`.
- Toda llamada al backend desde el frontend pasa por `frontend/src/api/`. Nunca `fetch` suelto en un componente.
- **Todo acceso a base de datos por SQLAlchemy async con `asyncpg`.** Nunca SQL por interpolación de strings — siempre ORM o Core con parámetros bindeados.
- Sin `except` genéricos que silencien errores. Un `except Exception` sin re-lanzar ni loguear motivo concreto no es aceptable en rutas normales.
- Sesiones de base de datos cerradas vía DI de FastAPI. `httpx.AsyncClient` reutilizado con *connection pool*, no instanciado por request.
- Secretos (API keys, `JWT_SECRET_KEY`, credenciales) solo vía variables de entorno. Nunca hardcodeados ni logueados.

## 5. Testing

- TDD para lógica pura siempre que sea práctico.
- Tests unitarios obligatorios para: sinergia N×N (incluyendo casos borde de `SPEC.md`: cobertura parcial, N=2 sin discordante, grupo sin pares con dato), validación/curación del pipeline y transformaciones de datos.
- No forzar tests artificiales sobre código que solo conecta FastAPI, rutea HTTP o renderiza JSX sin lógica propia. Para eso, integración (`httpx` test client, `Vitest` + RTL + MSW) o verificación manual.

## 6. Performance

Requerimiento no funcional crítico (RNF1-RNF3 en `PROYECTO.md`):

- Vecinos de un ingrediente: **< 10 ms**.
- Render del grafo: **~60 FPS (< 16 ms por recálculo)**.
- IA externa: **presupuesto total de 8 s**, incluyendo reintento y cambio de proveedor.

Evitar asignaciones y cálculos innecesarios en los *hot paths*: ciclo de render de `react-force-graph-2d` y cálculo de la matriz N×N del Laboratorio. Sin micro-optimizaciones especulativas.

## 7. Desarrollo incremental

**Antes de modificar código:** identificar sprint y entregable activo en `PLAN.md`; consultar spec del sprint; inspeccionar implementación y estado del repo; identificar archivos afectados y reportar estrategia. Preservar cambios preexistentes ajenos a la tarea; si interfieren o hacen ambiguo el alcance, detenerse y consultar.

**Alcance:** no implementar funcionalidad de sprints posteriores sin autorización. Correcciones, tareas técnicas, cambios de seguridad o modificaciones necesarias para **desbloquear el sprint activo** pueden atravesar límites de sprint si están justificadas y documentadas.

**Verificaciones según tipo de cambio:**
1. **Código:** lint + tests afectados + build si puede afectar compilación.
2. **Infra/config/migraciones/Docker/dependencias:** los comandos afectados (aunque no toquen código de aplicación).
3. **Entrega mayor o cambio transversal:** batería completa de backend y frontend + `docker compose up -d --build` + verificación manual si hay UI.

**Salvedades:** cambios sin impacto ejecutable (README, comentarios, docs) → basta revisar el diff de forma consistente. Cambios de interacción visual (grafo, Laboratorio, UI) → verificación manual con el stack levantado, siempre.

No omitir una verificación relevante sin informar qué no se ejecutó y por qué.

**Comandos:**

```bash
# Backend
uv sync                                  # instalar/actualizar dependencias
ruff check backend/                      # lint
ruff format --check backend/             # formato
mypy backend/                            # type checking
pytest backend/tests/                    # tests
pytest backend/tests/test_synergy.py -v  # test puntual

# Frontend
npm install                              # instalar/actualizar dependencias
npm run lint                             # lint
npm run test:run                         # tests (Vitest)
npm run build                            # build de producción

# Stack completo
docker compose up -d --build             # levantar todo
docker compose logs -f backend           # logs del backend
```

## 8. Dependencias

* Antes de agregar un paquete, chequear si se resuelve con dependencias existentes, librería estándar o tecnologías ya definidas.  
* Dependencias nuevas requieren justificación técnica concreta. Se pueden agregar sin consultar si la tienen y no reemplazan el stack definido.  
* No reemplazar PostgreSQL, FastAPI, React, uv o npm sin consultar.  
* Reportar toda dependencia nueva agregada.

## 9. Historial de desarrollo

Registro cronológico único en `docs/HISTORY.md`. Registrar solo al: completar un entregable mayor de un sprint; tomar una decisión que modifique `PROYECTO.md`/`SPEC.md`; resolver un bloqueo técnico no trivial; cerrar el spike de grafo (Sprint 2, incluir FPS medidos).

Cada entrada debe incluir: contexto, cambios realizados, archivos afectados, decisiones y su justificación, problemas encontrados y cómo se resolvieron, tests ejecutados, y pendientes para el siguiente sprint. No registrar cambios triviales ni refactors menores. El historial complementa la spec, no la reemplaza.

## 10. Comunicación

Antes: reportar objetivo, archivos probables y estrategia. Después: qué se implementó, qué se modificó, verificaciones ejecutadas, resultado y pendientes. Pedir aclaración solo ante ambigüedad o decisión significativa (sección 2). No pedir confirmación para decisiones menores ya cubiertas por la spec; informar suposiciones razonables.

## 11. Criterios de finalización

Tarea terminada cuando: cumple `PROYECTO.md`/`SPEC.md` y el DoD del sprint activo según `PLAN.md`; se ejecutaron las verificaciones proporcionales (sección 7); no introduce regresiones ni funcionalidad fuera de alcance; los recursos usados están correctamente gestionados y liberados.

No marcar completa solo porque el código corre. Informar siempre qué se ejecutó y qué quedó pendiente.

## 12. Flujo de Git

* Rama base: cada tarea en una rama dedicada creada desde `dev`. Nunca trabajar directamente sobre `dev` ni `master`.  
* Commits: atómicos y frecuentes, cada uno enfocado en un cambio lógico. No acumular cambios de varias tareas en un commit.  
* Mensajes: `tipo: resumen`, con `feat`, `fix`, `test`, `refactor`, `docs` o `chore`.  
* Push: pushear la rama de feature al remoto (nunca `dev`, nunca `master`).  
* Integración: no mergear a `dev` ni a `master` por iniciativa propia. Mergear `dev` → `master` y crear tags de sprint solo a pedido explícito del desarrollador.  
* Restricciones: nunca reescribir historia.  
* Antes de integrar: cumplir la sección 11. No integrar con build roto, tests en rojo, lint/type checking fallando o verificaciones pendientes.  
* Historial: la entrada de `HISTORY.md` de un entregable va en el commit que lo documenta.  
* Archivos: `uv.lock` y `package-lock.json` se commitean. `.venv/`, `node_modules/`, `__pycache__/` y `backups/*.sql` se ignoran.