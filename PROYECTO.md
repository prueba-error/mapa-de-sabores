# Mapa de Sabores - Propuesta de Proyecto Final

## Proyecto Final Desarrollo de Sistemas Web

**Alumno:** Diego Rafael Guaraz
**Docente / Cátedra:** Proyecto Final Desarrollo de Sistemas Web
**Documento de Presentación Académica del Proyecto**

---

## 1. Resumen

**Mapa de Sabores** es un sistema web interactivo de descubrimiento gastronómico basado en una arquitectura híbrida de **Base de Datos Relacional + Inteligencia Artificial (IA)**.

El proyecto resuelve el problema del maridaje e innovación culinaria mediante una representación en forma de **Grafo de Sabores** interactivo y dinámico. Permite a profesionales de la cocina, estudiantes de gastronomía y aficionados explorar combinaciones de ingredientes basadas en una afinidad culinaria respaldada por evidencia molecular comprobable y enriquecida por IA, y recibir explicaciones organolépticas de los mecanismos de maridaje generadas por modelos de lenguaje (LLM).

### Principales Pilares de Ingeniería

1. **Certeza en el Core (Base Relacional Estable y Verdad Empírica):** la red de sabores reside en PostgreSQL con índices compuestos bidireccionales. La afinidad del grafo se basa en **evidencia físico-química comprobable** (compuestos volátiles compartidos documentados en FlavorDB y Ahn et al., Nature 2011), garantizando consistencia, respuestas instantáneas (< 10ms) y cero alucinaciones en la determinación de la gran mayoría de los pares.
2. **Sistema Experto Híbrido en Dos Etapas (Química + IA Flash):** un pipeline científico calcula determinísticamente la similitud de Jaccard y el recuento molecular ($N_s$). En una segunda etapa, un LLM actúa como auditor bibliográfico para rescatar maridajes clásicos de contraste (pares imposibles para la química, como Melón + Jamón Crudo) e incorporarlos al grafo, además de generar explicaciones culinarias fluidas (`ai_rationale`). Todo ello cuenta con una capa de validación contra pares antagónicos, cola de revisión manual y auditoría aleatoria.
3. **Capa de IA Desacoplada e Intercambiable:** un servicio backend agnóstico en FastAPI permite alternar entre proveedores cloud (Google Gemini, OpenAI) con fallback a texto pre-generado en base, utilizando la IA tanto para el rescate en el pipeline offline como para explicaciones online bajo demanda.
4. **Interfaz React Estructurada en 3 Vistas:** experiencia de usuario modular dividida en tres pantallas principales (Explorar Grafo 2D, Ficha de Ingrediente y Laboratorio de Combinaciones) interconectadas mediante estado global compartido (Context API).

---

## 2. Marco Académico y Planteamiento del Problema

### 2.1 Problema Identificado

El descubrimiento de combinaciones de ingredientes (maridaje o _flavor pairing_) tradicionalmente ha dependido de la intuición empírica o de enciclopedias culinarias estáticas. Aunque existen teorías científicas de maridaje de sabores (compartir compuestos aromáticos clave), las herramientas de _flavor pairing_ existentes están mayormente en inglés y son pocas las abiertas e interactivas en español que combinen exploración visual intuitiva en forma de grafo dinámico con explicaciones organolépticas personalizadas en lenguaje natural.

### 2.2 Objetivos del Proyecto

* **Objetivo General:** desarrollar una aplicación web full-stack funcional que permita explorar redes de sabores e interacciones de ingredientes asistida por Inteligencia Artificial.
* **Objetivos Específicos:**
  1. Diseñar un esquema relacional optimizado en PostgreSQL para modelar grafos bidireccionales de afinidad, con consultas de vecinos resueltas mediante índices compuestos.
  2. Implementar un pipeline offline en Python para la generación de un dataset híbrido de afinidades culinarias (determinista por GC-MS + rescate semántico por LLM), con validación automática y curación manual de casos dudosos.
  3. Crear una API REST en FastAPI con arquitectura limpia y abstracción del proveedor de LLM.
  4. Desarrollar una interfaz de usuario interactiva en React estructurada en 3 vistas principales utilizando `react-force-graph-2d`.
  5. Integrar autenticación JWT para áreas personalizadas de usuarios (guardar combinaciones favoritas).

### 2.3 Defensa de Decisiones de Diseño y Arquitectura

* **PostgreSQL vs. Neo4j:** se optó por PostgreSQL debido a que en una red de 300 a 1.000 ingredientes las consultas de 1 o 2 saltos (_hops_) no justifican la sobrecarga operativa y de memoria de un motor de grafos nativo como Neo4j. Mediante índices compuestos y ordenamiento de IDs (`ingredient_a_id < ingredient_b_id`), Postgres resuelve estas consultas de forma directa (sin recorridos recursivos) en **< 10ms**, con un costo operativo y de despliegue significativamente menor.

* **Arquitectura Híbrida de IA en Dos Etapas:** la IA no actúa como una base de datos estocástica (evitando alucinaciones o respuestas lentas en navegación UI), sino que el sistema opera como un **Sistema Experto Híbrido**:
  1. **Etapa 1 (Grafo Molecular Químico):** un motor determinista basado en espectrometría de masas (GC-MS) y similitud de Jaccard detecta armonías moleculares y puentes ocultos de manera instantánea.
  2. **Etapa 2 (Auditor Bibliográfico Flash):** un LLM audita pares de bajo solapamiento molecular (S < 0.15) contra literatura culinaria consagrada (*The Flavor Bible*, *The Flavour Thesaurus*) para rescatar "clásicos de contraste" (ej. Melón + Jamón Crudo, Frutilla + Aceto). Además, tipifica el mecanismo organoléptico de cada enlace: *molecular_harmony*, *basic_taste_contrast* o *trigeminal_activation*.

* **Curación Humana como Salvaguarda, no como Automatismo:** en lugar de confiar ciegamente en el score que devuelve el LLM, los pares que caen en una matriz de incompatibilidades conocidas se enrutan a una cola de revisión (`pairing_review_queue`) y solo entran al grafo público tras aprobación manual. Además, una muestra aleatoria del 5-10 % de los pares restantes también se revisa a mano, y la tasa de correcciones se informa en la memoria como medida de calidad del dataset. Los scores siguen siendo estimaciones de un LLM, no mediciones: la interfaz y la documentación los presentan como "afinidad estimada". Esto prioriza la corrección editorial sobre la cobertura automática total del dataset.

* **Autenticación Estateless Simplificada (JWT de Sesión):** se optó por una autenticación JWT stateless de sesión única almacenada en el cliente. La validación se realiza criptográficamente en FastAPI sin consultas de revocación a base de datos, optimizando el desarrollo sin comprometer la seguridad funcional para usuarios autenticados. El token se guarda en el cliente (`localStorage`), lo que expone el riesgo de XSS; se mitiga con una CSP estricta, sin inyección de HTML y tratando siempre la salida del LLM como texto plano.

---

## 3. Arquitectura General del Sistema

El sistema utiliza un patrón de **Arquitectura Multicapa Desacoplada**:

```
+-----------------------------------------------------------------------------------+
|                                  CAPA FRONTEND                                    |
|   React (Vite) + Tailwind CSS + Context API (3 Vistas) + react-force-graph-2d     |
+-----------------------------------------------------------------------------------+
                                         |
                                  HTTP / REST (JWT)
                                         v
+-----------------------------------------------------------------------------------+
|                                  CAPA BACKEND                                     |
|                                FastAPI (Python)                                   |
|   |- Auth Controller & Security (JWT / Argon2)                                    |
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

1. **Carga Inicial del Grafo:** el cliente React solicita `GET /api/v1/graph`. FastAPI consulta PostgreSQL y retorna los nodos y enlaces activos (subgrafo paginado, ordenable por mayor o menor afinidad).
2. **Exploración y Filtrado:** el usuario selecciona un nodo (ej: _Tomate_). El frontend resalta vecinos y solicita `GET /api/v1/ingredients/{id}/pairings`, pudiendo pedir el ranking de mejores o peores afinidades para ese ingrediente.
3. **Evaluación de Sinergia en el Laboratorio:** al combinar varios ingredientes en la vista de Laboratorio, el frontend invoca `POST /api/v1/pairings/evaluate`, que calcula el índice de sinergia global como el promedio de `affinity_score` de los pares del grupo que tienen dato (e informa la cobertura, por ejemplo 4 de 6 pares), arma la matriz NxN de afinidades cruzadas, y señala como ingrediente discordante (solo con 3 o más ingredientes) al que tiene menor afinidad promedio contra el resto del grupo.
4. **Explicación con IA (Online):** al presionar "¿Por qué combinan?", el frontend invoca `POST /api/v1/ai/explain-pairing`. FastAPI utiliza la interfaz `LLMProvider` para generar un párrafo descriptivo con tono gastronómico, además de devolver el **mecanismo del maridaje** (*armonía molecular, contraste, trigeminal*).

El detalle técnico completo de este flujo está en **[SPEC.md](./SPEC.md)**.

---

## 4. Dataset de Sabores y Pipeline Offline
 
El dataset se construye a partir de evidencia científica comprobable proveniente de **FlavorDB y el estudio fundacional de Ahn et al. (Nature Scientific Reports, 2011)** complementado por auditoría de IA:

1. **Catálogo de Referencia Molecular (`data/`):** se compone de 82 compuestos químicos aromáticos volátiles y más de 330 ingredientes clasificados por categoría y perfil molecular.
2. **Cálculo Determinista de Afinidad (Etapa 1):** para cada par evaluado, se calcula matemáticamente su afinidad molecular combinando la similitud de Jaccard sobre las moléculas compartidas ($J(A, B)$) y el recuento absoluto de moléculas ($N_s$). La fórmula $S(A, B) = 0.5 \cdot J(A, B) + 0.5 \cdot \min(N_s, 6)/6$ asegura un rango determinista en $[0.00, 1.00]$.
3. **Auditoría Bibliográfica con LLM Flash (Etapa 2):** se realiza un barrido sobre pares descartados (S < 0.15) para rescatar combinaciones clásicas de contraste fisiológico (ej. acidez cortando grasa). Estos se incorporan al grafo marcados como `culinary_contrast` y se les asigna un `pairing_mechanism` (ej. *basic_taste_contrast*).
4. **Enriquecimiento Textual Asistido por IA:** el LLM recibe los hechos duros (ingredientes y moléculas volátiles que comparten) y redacta la explicación organoléptica en prosa fluida (`ai_rationale`).
5. **Validación Automática y Filtro Antagónico:** los pares son comparados contra una matriz de incompatibilidades conocidas. Los pares con alerta se enrutan a la cola de curación manual (`pairing_review_queue`). El detalle completo se documenta en **[JUSTIFICACION_TEORICA_FOOD_PAIRING.md](./docs/JUSTIFICACION_TEORICA_FOOD_PAIRING.md)** y **[SPEC.md](./SPEC.md)**.

Este enfoque prioriza que ningún dato dudoso llegue al usuario final sin revisión, sin requerir la complejidad de un sistema de moderación multiusuario: hay un único rol de curador (el alumno), ejercido por línea de comandos.

---

## 5. Experiencia de Usuario y Diseño Frontend

La interfaz se estructura en **tres vistas principales dedicadas**, accesibles mediante una barra de navegación superior (_Navbar_):

```
+-----------------------------------------------------------------------------------+
| [Logo] Mapa de Sabores  |  [ 1. Explorar Grafo ] [ 2. Ficha ] [ 3. Laboratorio ]  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  VISTA 1: EXPLORAR           VISTA 2: FICHA                 VISTA 3: LABORATORIO  |
|  (Grafo 2D en Canvas)        (Perfil Sensorial & Ranking)   (Constructor Chips)   |
|                                                                                   |
|  - Buscador Central          - Barras de Perfil Sabor       - Chips [Tomate x]    |
|  - Selector Mejores/Peores   - Tabla Comparativa de Par     - Sinergia (92%)      |
|  - Slider de Nodos (5-20)    - Rankings Mejor / Peor        - Matriz Cruzada NxN  |
|  - Botón "Extremos"          - Botón "Agregar al Lab"       - Alerta Discordante  |
+-----------------------------------------------------------------------------------+
```

### 5.1 Vista 1: Explorar Grafo (Navegación Visual)
* **Grafo 2D Interactivo:** Renderizado en HTML5 Canvas con `react-force-graph-2d` a 60 FPS.
* **Lógica Progresiva:**
  * 1 Ingrediente: Nodo central con aristas radiales a sus vecinos Top.
  * 2 Ingredientes: Arista principal coloreada por afinidad (verde > 75%, rojo punteado < 45%).
  * N Ingredientes: Recálculo en tiempo real al sumar componentes.
* **Controles de Filtro:**
  * Selector **Mejores / Todas / Peores** (`sort=best|worst|all`).
  * Slider de cantidad de nodos (5 a 20) para evitar saturación visual.
  * Botón **"Explorar extremos"**: Aisla el mejor y peor vecino del nodo activo.
* **Acciones Directas sobre Nodos:** Al seleccionar un nodo, se puede presionar **"Ver Ficha"** o **"Agregar al Laboratorio"**.

### 5.2 Vista 2: Ficha de Ingrediente (Detalle Sensorial)
* **Perfil de Sabor:** Gráficos de barras horizontales mostrando los ejes sensoriales (dulce, ácido, salado, amargo, umami, aromático) desde `ingredients.flavor_profile`.
* **Rankings Directos:** Lista ordenada de mejores y peores combinaciones para ese ingrediente.
* **Tabla Comparativa de Par:** Al examinar la conexión entre dos ingredientes específicos (ej. *Tomate + Albahaca*), muestra una tabla comparativa de perfiles sensoriales (*Acidez: Alta vs. Media*, *Aromático: Medio vs. Muy Alto*).
* **Acción Principal:** Botón directo **"Agregar al Laboratorio"** para sumar el ingrediente a la mesa de trabajo.

### 5.3 Vista 3: Laboratorio (Constructor de Combinaciones)
* **Mesa de Trabajo por Chips:** El usuario construye y modifica combinaciones agregando o quitando ingredientes en forma de etiquetas interactivas (_chips_).
* **Métricas y Análisis Determinístico:**
  * Medidor de **Sinergia Global (0 a 100%)** basado en `POST /pairings/evaluate`, con un indicador de cobertura (ej. "4 de 6 pares con dato").
  * Matriz cruzada $N \times N$ de compatibilidad de pares; las celdas sin dato se muestran como "sin dato".
  * Alerta de ingrediente discordante con sugerencia de reemplazo asistida por IA.
* *Nota de alcance:* Se preservan únicamente las métricas calculadas a partir del backend existente (`synergy_score`, matriz $N \times N$ y discordante). Se descartan tanto métricas adicionales de "contraste" o "complejidad" como un sistema de sugerencias para expandir la combinación (qué ingrediente agregar a continuación), por requerir lógica de agregación nueva no cubierta por los endpoints actuales — ver Sección 9 ("Trabajo Futuro").

---

## 6. Modelo de Usuario y Accesibilidad de la Plataforma

La exploración es pública; solo el guardado de favoritos requiere cuenta:

| Funcionalidad | Anónimo | Registrado |
| :--- | :---: | :---: |
| Grafo 2D, Ficha de ingrediente y Laboratorio (2 a 10 ingredientes) | Sí | Sí |
| Explicación de Chef con IA (con fallback a texto guardado) | Sí | Sí |
| Guardado de combinaciones favoritas | No | Sí |
| Límite de tasa (`slowapi`) | 60 req/min por IP | 120 req/min |
| Autenticación | — | Registro e inicio de sesión mediante JWT de sesión única |

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
       |    - Sprint 3: REST API, Sinergia N x N, Favoritos & Base UI     |
       |    - Sprint 4: UI 3 Vistas, IA Online, QA & Defensa              |
       +------------------------------------------------------------------+
```

---

## 8. Matriz de Riesgos y Viabilidad Económica

### 8.1 Matriz de Riesgos

| Riesgo Identificado | Impacto | Mitigación Planificada |
| :--- | :--- | :--- |
| **Saturación visual en el grafo** | Alto | Subgrafo paginado (`GET /graph?limit=50`) y `min_affinity` por defecto en 0.50 en el modo Mejores. |
| **Alucinaciones en pares generados por IA** | Medio | Prompting estructurado, matriz de incompatibilidades y cola de revisión manual (`pairing_review_queue`). |
| **Tiempo de curación manual subestimado** | Medio | Se reserva tiempo explícito en Sprint 2 para revisar los pares marcados como dudosos y la muestra de auditoría. |
| **Latencia o caída del proveedor de IA online** | Bajo | Presupuesto total de 8 s por solicitud (reintentos y cambio de proveedor incluidos) y fallback al `ai_rationale` guardado o a un mensaje genérico. |
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
4. **Sugerencias para expandir una combinación en el Laboratorio:** dado un grupo de ingredientes ya seleccionado, sugerir qué ingrediente sumar a continuación (por mayor afinidad con el grupo, o por contraste interesante). A diferencia del resto de las funcionalidades del Laboratorio, esto no sale de un simple `ORDER BY` sobre datos existentes: requiere agregación sobre todos los pares posibles contra el conjunto seleccionado y un criterio propio de "mejor sugerencia". **Se marca como opcional para el Sprint 4** (ver `PLAN.md`, Sprint 4) en caso de llegar con tiempo sobrante, y no forma parte del *Definition of Done* del proyecto. Las dos decisiones de diseño que necesitaría, ya resueltas de antemano para no tener que definirlas sobre la marcha, están detalladas en `SPEC.md`, Sección 3.2.1.

---

## Referencias a la Documentación Técnica Completa

* **[SPEC.md](./SPEC.md):** especificación técnica detallada con el DDL completo, pipeline de datos, endpoints REST y estrategia de pruebas.
* **[PLAN.md](./PLAN.md):** plan de implementación sprint por sprint, secuencia de kickoff y archivos de infraestructura.
* **[README.md](./README.md):** portada del repositorio y guía de arranque rápido.
