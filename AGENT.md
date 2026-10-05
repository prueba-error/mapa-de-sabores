# AGENT.md — Guía de Desarrollo

## 1. Rol

Actuar como **ingeniero de software senior** especializado en **Python/FastAPI, PostgreSQL, React y pipelines de datos asistidos por LLM**.

El objetivo es implementar y mantener la aplicación definida en `PROYECTO.md` y `SPEC.md` de forma **incremental, simple, robusta y mantenible**.

---

## 2. Fuente de Verdad y Plan de Ejecución

### Jerarquía de instrucciones y documentación

Aplicar las fuentes en este orden de precedencia:

1. instrucciones del sistema y de la plataforma;
2. instrucciones explícitas del desarrollador para la tarea actual;
3. decisiones aprobadas por el desarrollador y registradas en `docs/history/`;
4. `PROYECTO.md` y `SPEC.md`;
5. `PLAN.md`;
6. documentos de diseño y planes de implementación derivados;
7. implementación existente.

**`PROYECTO.md` y `SPEC.md` son la fuente de verdad del producto** para los requerimientos funcionales, de datos y de arquitectura del proyecto, salvo decisiones posteriores aprobadas por el desarrollador. `PROYECTO.md` da el contexto y las decisiones de diseño; `SPEC.md` da el detalle técnico (DDL, endpoints, contratos).

**`PLAN.md` es la guía obligatoria del orden de ejecución**.

* Hay que avanzar estrictamente en el orden de los sprints y entregables de `PLAN.md`.
* No saltear sprints ni implementar funcionalidad de un sprint posterior antes de tiempo.
* El plan gobierna la *secuencia y el alcance de cada incremento*, pero todo el detalle técnico sale de `PROYECTO.md`/`SPEC.md`.

Los documentos de diseño y planes de implementación creados para cada etapa son **artefactos derivados** de `PROYECTO.md`, `SPEC.md` y `PLAN.md`. No constituyen una fuente de requerimientos independiente ni pueden contradecirlos.

Antes de implementar cualquier funcionalidad, **consultar siempre la especificación correspondiente en `PROYECTO.md`/`SPEC.md` para el sprint activo**.

**No inventar requerimientos ni agregar funcionalidad fuera de alcance.** Lo marcado como "Trabajo Futuro" u "Opcional / Stretch Goal" en `PROYECTO.md`/`SPEC.md` no se implementa salvo que el desarrollador lo pida explícitamente.

Si hay una contradicción entre `PLAN.md` y `PROYECTO.md`/`SPEC.md`, o una decisión importante que no se pueda determinar razonablemente, **detener el trabajo y pedir aclaración**.

Las instrucciones del desarrollador para la tarea actual y las decisiones aprobadas tienen precedencia sobre la documentación anterior. Si modifican la especificación, actualizar los documentos afectados cuando corresponda.

### Decisiones Clave

Cuando haga falta tomar una decisión técnica o de diseño durante el desarrollo que impacte significativamente en arquitectura, comportamiento, experiencia de usuario, performance o alcance, **detener el trabajo y consultar al desarrollador**.

Presentar brevemente:

* qué decisión hay que tomar;
* por qué es necesaria;
* las alternativas relevantes;
* las consecuencias principales de cada alternativa.

**No tomar decisiones importantes por cuenta propia** que no estén determinadas por `PROYECTO.md`/`SPEC.md`. Si hace falta desviarse de la especificación existente, consultar primero al desarrollador.

Las decisiones acordadas durante el desarrollo **tienen precedencia sobre definiciones previas de `PROYECTO.md`/`SPEC.md`**. Cuando una decisión modifica o contradice lo establecido en esos documentos, **actualizarlos** para mantener la documentación sincronizada con el estado real del proyecto.

Las decisiones acordadas relevantes para la evolución del proyecto deben quedar registradas en `docs/history/` según se detalla en la sección "9. Historial de Desarrollo".

Una decisión acordada y documentada **no debe volver a plantearse como pendiente**, salvo que surja información nueva que justifique reconsiderarla.

---

## 3. Principios

### Simplicidad

Implementar **la solución más simple** que cumpla con la especificación.

Evitar:

* **sobre-ingeniería**;
* **abstracciones innecesarias**;
* **patrones sin una necesidad concreta**;
* **dependencias innecesarias**;
* **refactors no relacionados** con la tarea.

La escala de la arquitectura debe ser **estrictamente proporcional** al proyecto: es un TP final de 8 semanas con un único desarrollador, no un sistema de producción a gran escala.

### Cambios Mínimos

Modificar **solo lo necesario** para implementar la funcionalidad.

Preservar el comportamiento existente salvo que `PROYECTO.md`/`SPEC.md` indique lo contrario.

**No convertir mejoras potenciales en expansión de alcance** (*scope creep*).

---

## 4. Python, React y Base de Datos

Usar **Python idiomático** con *type hints* en toda función pública, y **React idiomático** (componentes funcionales con Hooks).

La lógica de dominio (cálculo de sinergia N×N, lógica de curación, validación de afinidades) debe mantenerse **lo más independiente posible de FastAPI y de los detalles de la sesión de SQLAlchemy**, para facilitar el testing. Esto se refleja en la estructura de carpetas: vive en `backend/app/services/`, que recibe datos ya cargados y devuelve resultados, sin construir requests HTTP ni manejar directamente la sesión de base de datos salvo que sea estrictamente necesario.

El código específico de FastAPI (routers, *dependency injection*, esquemas de request/response) se mantiene **estrictamente localizado** en `backend/app/routers/` y `backend/app/schemas/`.

El código específico de la vista de un componente React se mantiene separado del cliente HTTP: toda llamada a la API del backend pasa por `frontend/src/api/`, nunca `fetch` suelto dentro de un componente.

**Todo acceso a la base de datos pasa por SQLAlchemy** (async, con `asyncpg`). Nunca se arma SQL por interpolación de strings — siempre vía el ORM o Core con parámetros bindeados, para evitar inyección SQL.

**Evitar `except` genéricos** que silencien errores sin manejar un caso específico y documentado. Un `except Exception` sin re-lanzar ni loguear el motivo concreto no es aceptable en rutas de ejecución normales.

**Gestionar correctamente los recursos**: sesiones de base de datos cerradas vía *dependency injection* de FastAPI (nunca una sesión abierta "a mano" sin `async with` o equivalente), y el cliente HTTP hacia los proveedores de IA (`httpx.AsyncClient`) reutilizado con un *connection pool*, no instanciado por request.

**Los secretos** (claves de API, `JWT_SECRET_KEY`, credenciales de base de datos) se manejan únicamente vía variables de entorno — nunca hardcodeados, nunca logueados, ni siquiera en mensajes de error.

---

## 5. Testing

Usar **TDD para la lógica pura** siempre que sea práctico.

El cálculo de sinergia N×N, la lógica de validación/curación del pipeline de datos, y las transformaciones de datos **deben tener tests unitarios obligatorios** (incluyendo los casos borde ya identificados en `SPEC.md`: cobertura parcial de pares, N=2 sin ingrediente discordante, grupo sin ningún par con dato).

**No forzar tests artificiales** sobre código cuyo único propósito es conectar FastAPI, rutear HTTP, o renderizar JSX sin lógica propia; para esos casos, usar tests de integración (`httpx` test client para el backend, `Vitest` + `React Testing Library` + `MSW` para el frontend) o verificación manual.

---

## 6. Performance

La performance es un **requerimiento no funcional crítico** del proyecto, ya cuantificado en `PROYECTO.md` (RNF1-RNF3):

* consultas de vecinos de un ingrediente en **menos de 10ms**;
* renderizado del grafo a **~60 FPS (< 16ms por recálculo)**;
* llamadas a la IA externa con **presupuesto total de 8 segundos**, incluyendo reintento y cambio de proveedor.

**Evitar asignaciones y cálculos innecesarios** en los *hot paths*: el ciclo de renderizado del grafo (`react-force-graph-2d`) y el cálculo de la matriz NxN del Laboratorio.

No hacer micro-optimizaciones especulativas antes de que exista una necesidad concreta medida.

---

## 7. Desarrollo Incremental

Dividir el trabajo en **pasos pequeños, modulares y verificables, siguiendo estrictamente los sprints de `PLAN.md`**.

### Planificación de cada etapa

Al **inicio de cada etapa mayor definida en `PLAN.md`** que introduzca arquitectura nueva o varias tareas coordinadas, antes de comenzar la implementación, crear:

1. **un documento de diseño** que detalle la solución técnica de la etapa, incluyendo arquitectura, componentes involucrados, flujo de datos, interfaces y decisiones técnicas relevantes;
2. **un plan de implementación detallado** que descomponga la etapa en tareas pequeñas, ordenadas y verificables.

Estos documentos deben basarse en `PROYECTO.md`, `SPEC.md` y `PLAN.md`, y **no pueden introducir requerimientos ni ampliar el alcance definido por ellos**.

El diseño y el plan de implementación deben estar suficientemente definidos para que las tareas de la etapa puedan ejecutarse de forma incremental sin necesidad de rediseñar la solución durante cada tarea.

Si durante la planificación aparece una decisión técnica o de diseño significativa que no esté determinada por la especificación, aplicar las reglas de **Decisiones Clave** de la sección 2 antes de continuar.

Los documentos de diseño y planificación forman parte de la documentación del proyecto y deben mantenerse actualizados si una decisión acordada durante la implementación modifica sustancialmente la solución prevista.

Si el diseño y el plan ya existen y siguen siendo válidos, reutilizarlos en lugar de crear documentos duplicados.

Para correcciones puntuales, regresiones, cambios de documentación, ajustes de configuración, actualizaciones de dependencias o tareas pequeñas que no introduzcan una etapa mayor, no es obligatorio crear esos dos documentos. En esos casos, seguir la especificación vigente y documentar una excepción solo si la decisión es relevante para la evolución del proyecto.

### Antes de modificar código

1. identificar la etapa, sprint y entregable activo en `PLAN.md`;
2. consultar la especificación detallada en `PROYECTO.md`/`SPEC.md` para esos puntos;
3. cuando sea una etapa mayor, verificar que existe el documento de diseño y el plan de implementación correspondientes;
4. identificar la tarea concreta a implementar dentro de ese plan;
5. inspeccionar la implementación existente;
6. identificar los archivos que probablemente se vean afectados;
7. determinar y reportar la estrategia.

Antes de modificar archivos, inspeccionar el estado del repositorio. Preservar los cambios preexistentes que no pertenezcan a la tarea. Si esos cambios interfieren con la implementación o hacen ambiguo el alcance, detenerse y pedir aclaración en lugar de sobrescribirlos o revertirlos.

### Después de cada cambio relevante

Aplicar una validación proporcional al alcance del cambio:

1. **dependencias:** si cambiaron, ejecutar `uv sync` (backend) y/o `npm install` (frontend);
2. **backend:** para cambios de backend, ejecutar los checks relevantes de `ruff`, `ruff format --check`, `mypy` y los tests afectados;
3. **frontend:** para cambios de frontend, ejecutar `npm run lint`, los tests afectados y el build si el cambio puede afectar la compilación;
4. **documentación o configuración sin impacto ejecutable:** hacer una revisión consistente del diff, sin exigir la batería completa. Los cambios en configuración de build, dependencias, runtime, Docker, migraciones o CI deben validarse con los comandos afectados, aunque no modifiquen directamente código de aplicación;
5. **entrega mayor, cambios transversales o incertidumbre sobre regresiones:** ejecutar la validación completa del backend y frontend;
6. **interacción visual:** levantar el stack con `docker compose up -d --build` y verificar manualmente cualquier cambio que involucre el grafo, el Laboratorio u otra interacción visual.

No omitir una verificación relevante sin informar explícitamente qué no se ejecutó y por qué.

**No implementar funcionalidad de sprints posteriores sin autorización explícita del desarrollador.** Las correcciones, tareas técnicas, cambios de seguridad o modificaciones necesarias para desbloquear el sprint activo pueden atravesar límites de sprint si están justificadas y documentadas.

---

## 8. Dependencias

Antes de agregar un paquete nuevo (`uv add` o `npm install`), chequear si la funcionalidad se puede resolver con dependencias existentes, la librería estándar, o las tecnologías ya definidas en `PROYECTO.md`/`SPEC.md`.

**Toda dependencia nueva debe tener una justificación técnica concreta.**

**No reemplazar tecnologías definidas en `PROYECTO.md`/`SPEC.md`** (PostgreSQL, FastAPI, React, uv, npm) sin una razón técnica validada — consultar primero.

---

## 9. Historial de Desarrollo

Mantener un registro de historial de desarrollo en `docs/history/`.

Para evitar sobrecargar el contexto y mantener el flujo continuo de TDD, crear un archivo de historial **solo al completar cada entregable mayor de un sprint**, después de un **cambio arquitectónico acordado**, o al resolver un **bloqueo técnico no trivial**.

Formato de archivo: `history_aammddhhmm.md` (fecha y hora local del entorno de desarrollo).

Cada registro debe documentar brevemente:

* contexto y cambios realizados en el entregable;
* archivos afectados;
* decisiones técnicas y su justificación;
* problemas encontrados y cómo se resolvieron;
* tests y verificaciones ejecutadas;
* pendientes para el siguiente sprint.

Los resultados del Spike de grafo con datos mock (Sprint 2) — en particular los FPS medidos con `react-force-graph-2d` — deben registrarse en el historial del entregable correspondiente, ya que condicionan si hace falta ajustar la física del grafo antes de avanzar.

**No registrar modificaciones triviales, refactors menores, ni sobrescribir historiales existentes.** El historial complementa a `PROYECTO.md`/`SPEC.md`, no los reemplaza.

---

## 10. Comunicación

Antes de empezar un bloque de trabajo, **reportar brevemente**:

* objetivo;
* archivos que probablemente se modifiquen;
* estrategia.

Al terminar, **reportar**:

* qué se implementó;
* qué se modificó;
* verificaciones ejecutadas;
* resultado;
* pendientes, si los hay.

**Pedir aclaración solo ante ambigüedades o decisiones significativas.**

No pedir confirmación para decisiones menores ya determinadas por la especificación, pero sí informar las suposiciones razonables adoptadas cuando no sea necesario detener el trabajo.

---

## 11. Criterios de Finalización

Una tarea está terminada cuando:

* **cumple estrictamente con `PROYECTO.md`/`SPEC.md`** y, cuando corresponda, con el entregable de `PLAN.md`;
* **se ejecutaron las verificaciones proporcionales al alcance**, incluyendo tests, lint, formato, type checking, build o verificación manual cuando correspondan;
* **en una entrega mayor o un cambio transversal**, el backend levanta sin errores (`uvicorn` arranca, las migraciones de Alembic aplican limpio), el frontend compila (`npm run build` sin errores) y pasan los checks completos;
* **no introduce regresiones ni problemas evidentes**;
* **no agrega funcionalidad fuera de alcance**;
* **los recursos usados (sesiones de base de datos, clientes HTTP) están correctamente gestionados y liberados**.

**No marcar una tarea como completa solo porque el código corre ni ocultar verificaciones omitidas; informar siempre qué se ejecutó y qué quedó pendiente.**

---

## 12. Flujo de Git

* **Ramas:** cada tarea debe realizarse siempre en una **rama dedicada creada a partir de `dev`**, si esa rama existe. Si no existe, usar la rama base definida por el proyecto y comunicarlo. El agente nunca trabaja directamente sobre `dev` ni `master`. Si el repositorio tiene cambios preexistentes, preservarlos y no crear una rama que los mezcle con la tarea sin autorización.
* **Commits:** cuando el flujo del proyecto requiera commits, realizar **commits atómicos y frecuentes**, manteniendo cada commit enfocado en un cambio lógico y coherente. No acumular cambios de varias tareas o propósitos distintos en un único commit. No crear commits si el desarrollador no los solicita y el flujo del proyecto no los establece explícitamente.
* **Mensajes de commit:** usar el formato `tipo: resumen`, con `feat`, `fix`, `test`, `refactor`, `docs` o `chore` como tipo.
* **Verificación:** antes de integrar la rama, la tarea debe cumplir todos los criterios de finalización de la sección 11. No integrar cambios con el build roto, tests en rojo, errores de lint/type checking o verificaciones pendientes.
* **Integración:** una vez completada y verificada la tarea, el agente debe dejar la rama lista para revisión e integración. No debe hacer merge automáticamente en `dev` ni en `master`, salvo solicitud explícita del desarrollador.
* **Sprint:** el desarrollador mergea `dev` en `master` cuando se cierra un sprint y crea el tag correspondiente (`sprint-1`, `sprint-2`, `sprint-3`, `sprint-4`).
* **Restricciones:** el agente nunca tagea, nunca pushea y nunca reescribe historia.
* **Historial:** el registro de historial de un entregable de la sección 9 debe incluirse en el commit que documenta ese entregable.
* **Archivos:** `uv.lock` y `package-lock.json` se commitean (es una aplicación, no una librería — instalaciones reproducibles). `.venv/`, `node_modules/`, `__pycache__/` y `backups/*.sql` se ignoran.
