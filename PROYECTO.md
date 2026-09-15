# Mapa de Sabores - Propuesta de Proyecto Final

## Proyecto Final Desarrollo de Sistemas Web

**Alumno:** Diego Rafael Guaraz
**Docente / Cátedra:** Proyecto Final Desarrollo de Sistemas Web
**Documento de Presentación Académica del Proyecto**

---

## 1. Resumen

**Mapa de Sabores** es un sistema web interactivo de descubrimiento gastronómico basado en una arquitectura híbrida de **Base de Datos Relacional + Inteligencia Artificial (IA)**.

El proyecto resuelve el problema del maridaje e innovación culinaria mediante una representación en forma de **Grafo de Sabores** interactivo y dinámico. Permite a profesionales de la cocina, estudiantes de gastronomía y aficionados explorar combinaciones de ingredientes basados en afinidad química y culinaria, y recibir explicaciones organolépticas generadas por modelos de lenguaje (LLM).

### Principales Pilares de Ingeniería

1. **Certeza en el Core (Base Relacional Estable):** la red de sabores reside en PostgreSQL con índices compuestos bidireccionales. La estructura del grafo se define por datos curados y validados, garantizando consistencia, respuestas instantáneas (< 10ms) y cero alucinaciones en la navegación UI.
2. **Pipeline de Datos Sintéticos Offline con Curación Humana:** un pipeline de ingeniería de prompts compila un dataset inicial de ~250 ingredientes y ~1.500 pares de afinidad, con una capa de validación automática y una **cola de revisión manual** para los pares dudosos antes de que entren al grafo.
3. **Capa de IA Desacoplada e Intercambiable:** un servicio backend agnóstico en FastAPI permite alternar entre proveedores cloud (Google Gemini, OpenAI) con fallback a texto pre-generado en base.
4. **Visualización React en 2D:** renderizado dinámico de nodos y aristas mediante HTML5 Canvas (`react-force-graph-2d`) con experiencia de usuario fluida y panel lateral descriptivo.

---

## 2. Marco Académico y Planteamiento del Problema

### 2.1 Problema Identificado

El descubrimiento de combinaciones de ingredientes (maridaje o _flavor pairing_) tradicionalmente ha dependido de la intuición empírica o de enciclopedias culinarias estáticas. Aunque existen teorías científicas de maridaje de sabores (compartir compuestos aromáticos clave), no existen herramientas web abiertas e interactivas en español que combinen exploración visual intuitiva en forma de grafo dinámico con explicaciones organolépticas personalizadas en lenguaje natural.

### 2.2 Objetivos del Proyecto

* **Objetivo General:** desarrollar una aplicación web full-stack funcional que permita explorar redes de sabores e interacciones de ingredientes asistida por Inteligencia Artificial.
* **Objetivos Específicos:**
  1. Diseñar un esquema relacional optimizado en PostgreSQL para modelar grafos bidireccionales de afinidad, con consultas de vecinos resueltas mediante índices compuestos.
  2. Implementar un pipeline offline en Python para la generación de un dataset sintético de afinidades culinarias, con validación automática y curación manual de casos dudosos.
  3. Crear una API REST en FastAPI con arquitectura limpia y abstracción del proveedor de LLM.
  4. Desarrollar una interfaz de usuario interactiva en React utilizando `react-force-graph-2d`.
  5. Integrar autenticación JWT para áreas personalizadas de usuarios (guardar combinaciones favoritas).

### 2.3 Defensa de Decisiones de Diseño y Arquitectura

* **PostgreSQL vs. Neo4j:** se optó por PostgreSQL debido a que en una red de 300 a 1.000 ingredientes las consultas de 1 o 2 saltos (_hops_) no justifican la sobrecarga operativa y de memoria de un motor de grafos nativo como Neo4j. Mediante índices compuestos y ordenamiento de IDs (`ingredient_a_id < ingredient_b_id`), Postgres resuelve estas consultas de forma directa (sin recorridos recursivos) en **< 10ms**, con un costo operativo y de despliegue significativamente menor.

* **Arquitectura Híbrida de IA:** la IA no actúa como la base de datos (evitando alucinaciones o respuestas lentas en navegación UI), sino como un potenciador en dos fases: compilación de dataset en pipeline offline (con curación humana) y generación de prosa culinaria en línea bajo demanda del usuario.

* **Curación Humana como Salvaguarda, no como Automatismo:** en lugar de confiar ciegamente en el score que devuelve el LLM, los pares que caen en una matriz de incompatibilidades conocidas o presentan valores atípicos se enrutan a una cola de revisión (`pairing_review_queue`) y solo entran al grafo público tras aprobación manual. Esto prioriza la corrección editorial sobre la cobertura automática total del dataset.

* **Autenticación Estateless Simplificada (JWT de Sesión):** se optó por una autenticación JWT stateless de sesión única almacenada en el cliente. La validación se realiza criptográficamente en FastAPI sin consultas de revocación a base de datos, optimizando el desarrollo sin comprometer la seguridad funcional para usuarios autenticados.

---

## 3. Arquitectura General del Sistema

El sistema utiliza un patrón de **Arquitectura Multicapa Desacoplada**:

```
+-----------------------------------------------------------------------------------+
|                                  CAPA FRONTEND                                    |
|         React (Vite) + Tailwind CSS + Context API + react-force-graph-2d          |
+-----------------------------------------------------------------------------------+
                                         |
                                  HTTP / REST (JWT)
                                         v
+-----------------------------------------------------------------------------------+
|                                  CAPA BACKEND                                     |
|                                FastAPI (Python)                                   |
|   |- Auth Controller & Security (JWT / Passlib)                                   |
|   |- Ingredients & Pairings Service (SQLAlchemy Core)                             |
|   |- LLM Provider Service Interface (Gemini / OpenAI Adapter)                     |
|   |- Curation Service (Pairing Review Queue)                                      |
+-----------------------------------------------------------------------------------+
               |                                 |
     SQL (SQLAlchemy/asyncpg)               HTTP API
               v                                 v
+-----------------------------+           +--------------------+
|     PostgreSQL Database     |           |  External LLM API  |
| (Ingredients, Pairings, DB) |           | (Gemini / OpenAI)  |
+-----------------------------+           +--------------------+
```

### 3.1 Flujo de Datos Principal

1. **Carga Inicial del Grafo:** el cliente React solicita `GET /api/v1/graph`. FastAPI consulta PostgreSQL y retorna los nodos y enlaces activos (subgrafo paginado).
2. **Exploración y Filtrado:** el usuario selecciona un nodo (ej: _Tomate_). El frontend resalta vecinos y solicita `GET /api/v1/ingredients/{id}/pairings`.
3. **Evaluación de Sinergia:** al combinar varios ingredientes, el frontend invoca `POST /api/v1/pairings/evaluate`, que devuelve el índice de sinergia global, la matriz NxN y el ingrediente discordante si lo hay.
4. **Explicación con IA (Online):** al presionar "¿Por qué combinan?", el frontend invoca `POST /api/v1/ai/explain-pairing`. FastAPI utiliza la interfaz `LLMProvider` para generar un párrafo descriptivo con tono gastronómico.

El detalle técnico completo de este flujo está en **[SPEC.md](./SPEC.md)**.

---

## 4. Dataset de Sabores y Pipeline Offline

El dataset no se construye por relevamiento manual, sino mediante un pipeline en tres etapas:

1. **Síntesis con IA:** un script en Python (`scripts/seed_flavor_network.py`) consulta en lote a un LLM mediante solicitudes estructuradas (JSON Mode con Pydantic), generando un score de afinidad (0.0 a 1.0) y una explicación culinaria por cada par de ingredientes evaluado.
2. **Validación Automática:** cada par generado pasa por chequeos de rango, coherencia sintáctica y comparación contra una matriz curada de ~50 pares antagónicos conocidos (ej. _Pescado Blanco + Dulce de Leche_). Los pares que no presentan señales de alerta se insertan directamente en `flavor_pairings`.
3. **Curación Manual de Casos Dudosos:** los pares que sí disparan una alerta (por ejemplo, un score alto en un par listado como antagónico) no se descartan automáticamente: se enrutan a una cola de revisión (`pairing_review_queue`) donde el alumno, mediante un CLI simple (`scripts/curate.py --approve/--reject`), decide caso por caso si el par entra al grafo o se descarta. El detalle del funcionamiento de esta cola está en **[SPEC.md](./SPEC.md#2-pipeline-offline-y-origen-del-dataset-de-sabores)**.

Este enfoque prioriza que ningún dato dudoso llegue al usuario final sin revisión, sin requerir la complejidad de un sistema de moderación multiusuario: hay un único rol de curador (el alumno), ejercido por línea de comandos.

---

## 5. Experiencia de Usuario y Diseño Frontend

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
|                  v                                   |                            |
|            ( CHOCOLATE )                             |                            |
+------------------------------------------------------+----------------------------+
```

### 5.1 Landing y Búsqueda Inicial
Buscador central con sugerencias de tendencias (`[Tomate y Albahaca]`, `[Palta y Limón]`, `[Chocolate y Naranja]`) y transición fluida hacia la vista de grafo.

### 5.2 Lógica Progresiva del Grafo (1, 2 y N Ingredientes)
1. **1 Ingrediente** (ej. _Tomate_): nodo central con aristas radiales a sus Top 5-8 vecinos de mayor afinidad.
2. **2 Ingredientes** (ej. _Tomate + Albahaca_): arista principal coloreada por afinidad (verde si > 75%); los vecinos con alta afinidad con ambos se iluminan con mayor intensidad (opacidad 100%).
3. **Ingrediente Incompatible** (ej. _+ Chocolate_): arista en **rojo punteado** (< 45%) y atenuación del resto del grupo (opacidad 30%).
4. **Escala a N Ingredientes:** recálculo en tiempo real (< 16ms / 60 FPS) al sumar o restar componentes.

### 5.3 Panel Lateral (Drawer)
* Medidor visual de sinergia global (_Synergy Gauge_).
* Matriz interactiva NxN de afinidades cruzadas.
* Detector de elemento discordante (_Clashing Alert_) con sugerencia de reemplazo vía IA.

---

## 6. Modelo de Usuario y Accesibilidad de la Plataforma

La plataforma ofrece acceso completo a todas sus funcionalidades para los usuarios registrados:

| Característica / Funcionalidad | Especificación (Acceso Completo) |
| :--- | :--- |
| **Límite de Ingredientes por Búsqueda** | Hasta 10 ingredientes |
| **Visualización de Grafo y Sinergia** | Acceso completo e interactivo en 2D |
| **Explicación de Chef con IA** | Generación en tiempo real con fallback a PostgreSQL |
| **Guardado en Servidor** | Guardado de combinaciones favoritas por usuario |
| **Autenticación** | Registro e inicio de sesión simplificado mediante JWT de sesión única |

---

## 7. Plan de Implementación (Resumen de 2 Meses)

El desarrollo se estructura en **4 sprints de 2 semanas**, con tiempo reservado en cada uno para integración y comprensión del código generado con asistencia de IA. Cronograma detallado y *Definition of Done* por sprint en **[PLAN.md](./PLAN.md)**.

```
       +-----------------------------------------------------------------+
       |    MES 1: Cimientos, Pipeline de Datos & Prototipado            |
       |    - Sprint 1: DDL Postgres, Alembic, Entorno Docker & Auth     |
       |    - Sprint 2: Seed LLM + Curación & Spike Grafo React 2D       |
       +------------------------------+----------------------------------+
                                      |
                                      v
       +------------------------------------------------------------------+
       |    MES 2: Backend Core & Frontend Completo                       |
       |    - Sprint 3: REST API Grafo, Sinergia N x N & Caché de Auth    |
       |    - Sprint 4: UI Grafo 2D, IA Online, QA Manual & Defensa       |
       +------------------------------------------------------------------+
```

---

## 8. Matriz de Riesgos y Viabilidad Económica

### 8.1 Matriz de Riesgos

| Riesgo Identificado | Impacto | Mitigación Planificada |
| :--- | :--- | :--- |
| **Saturación visual en el grafo** | Alto | Subgrafo paginado (`GET /graph?limit=50`) y `min_affinity` por defecto en 0.50. |
| **Alucinaciones en pares generados por IA** | Medio | Prompting estructurado, matriz de incompatibilidades y cola de revisión manual (`pairing_review_queue`). |
| **Tiempo de curación manual subestimado** | Medio | Se reserva tiempo explícito en Sprint 2 para revisar los pares marcados como dudosos. |
| **Latencia o caída del proveedor de IA online** | Bajo | Timeout de 3s, reintentos y fallback al `ai_rationale` guardado en base. |
| **Brecha entre "código generado" y "código comprendido"** | Medio | Tiempo de integración/comprensión reservado en cada sprint; el alumno debe poder justificar cada decisión de diseño en la defensa. |

### 8.2 Viabilidad Económica

El diseño arquitectónico permite operar el MVP a costo prácticamente nulo durante la fase de desarrollo y defensa académica (capas gratuitas de Render, Supabase y PostgreSQL).

* **MVP / Defensa de Tesis (1-100 usuarios):** ~$0.00 USD/mes (Free Tier).
* **Producción Inicial (1.000 usuarios):** costo dominado por las llamadas a LLM cloud; estimado bajo (< USD 5/mes) gracias al fallback y al bajo volumen de llamadas en línea (solo explicaciones bajo demanda, no navegación del grafo).

---

## 9. Trabajo Futuro

Como extensiones naturales del proyecto, quedan planteadas las siguientes líneas de trabajo futuro:

1. **Integración con API externa de recetas (ej. Spoonacular):** permitiría mostrar recetas reales para una combinación de ingredientes evaluada por el sistema, enriqueciendo la propuesta de valor para el usuario final. Implica gestionar cuotas de uso, sanitización de payloads externos y una capa de caché.
2. **Pipeline de CI/CD (GitHub Actions):** automatizaría la ejecución de tests y migraciones en cada push, aportando valor especialmente a medida que el proyecto escale a un equipo de más de un desarrollador.
3. **Control de varianza del dataset contra fuentes académicas externas (FlavorDB/Flavornet):** cruzar los scores generados por el LLM contra un dataset académico externo permitiría detectar divergencias adicionales a las que ya cubren la matriz de incompatibilidades y la cola de revisión manual. Requiere resolver el *matching* de nombres de ingredientes entre idiomas y nomenclaturas.

---

## Referencias a la Documentación Técnica Completa

* **[SPEC.md](./SPEC.md):** especificación técnica detallada con el DDL completo, pipeline de datos, endpoints REST y estrategia de pruebas.
* **[PLAN.md](./PLAN.md):** plan de implementación sprint por sprint, secuencia de kickoff y archivos de infraestructura.
* **[README.md](./README.md):** portada del repositorio y guía de arranque rápido.
