# Mapa de Sabores con IA

## Proyecto Final Desarrollo de Sistemas Web 

Esta es mi recomendación final, bajada a tierra y diseñada específicamente para que **te luzcas en la defensa, aprendas un montón de IA, pero sobre todo, te recibas en el tiempo estimado sin arriesgar el título**.

El enfoque ideal es **"Certeza en el Core, Innovación en los Extras"**. Vamos a estructurar el proyecto en tres capas bien definidas: la base sólida, el toque de IA seguro y la "frutilla del postre" (el experimento local) solo si el tiempo te sonríe.

---

## 🏗️ La Arquitectura del Proyecto

```
[ Frontend: React ] <---> [ Backend: FastAPI ] <---> [ Base de Datos: PostgreSQL ]
       │                         │
       │ (Grafo Visual)          ├─> [ API de IA Externa ] (Explicaciones en vivo)
       └─> (Rápido y Estable)    │
                                 └─> [ API de Recetas ] (Spoonacular)

```

1. **La Verdad está en SQL:** PostgreSQL es el motor del proyecto. Controlás los datos, los ingredientes y las relaciones. El grafo visual del frontend se alimenta de acá de forma 100% predecible.
2. **IA como Potenciador, no como Cimiento:** Usás un LLM grande del mercado (vía API) para dos tareas muy acotadas: poblar la base de datos antes de arrancar (offline) y dar contexto en vivo al usuario.

---

## 📅 Plan de Acción y Cronograma (4 Meses)

### Mes 1: El Dataset y los Cimientos (La fase de Data Science)

* **Diseño de DB:** Creás el modelo en Postgres (`ingredients` y `pairings` con índice compuesto ordenado por ID menor).
* **Pipeline Offline (Tu primer contacto con IA):** Armás tu lista semilla de 200 ingredientes. Creás un script en Python que recorra pares y le pida a un LLM (vía API) evaluar la afinidad (0 a 1) y una justificación.
* **Limpieza de Datos:** Validás que el JSON generado no tenga errores y poblás tu base de datos. Al terminar el mes, tenés tu "Flavor Network" lista en local.

### Mes 2: El Backend Core y Conectividad

* **Endpoints en FastAPI:** Desarrollás los CRUDs básicos, la lógica de autenticación (JWT simple) y, clave, el endpoint de búsqueda que calcule combinaciones válidas basándose en los datos de tu Postgres.
* **Integración de Recetas:** Conectás Spoonacular. Implementás una caché simple en memoria o en la misma DB para no quemar los créditos de la API gratuita cada vez que alguien busca "tomate + albahaca".

### Mes 3: El Frontend y el "Monstruo" del Grafo

* **El Prototipo Visual:** Arrancás el mes peleándote con `react-force-graph` o la librería que elijas. Hacés que pinte nodos y uniones usando datos estáticos. **No avances a otras pantallas hasta que el grafo no se mueva bien.**
* **Integración UI:** Conectás las pantallas de Login, el historial de combinaciones guardadas del usuario y las tarjetas de recetas que vienen del backend.

### Mes 4: Integración de IA en Vivo, Pulido y el "As bajo la manga"

* **Feature Online:** Agregás el botón de "¿Por qué combinan?" en la UI, que hace una llamada limpia a la API de IA para que redacte el párrafo con tono de chef.
* **El As bajo la manga (Opcional - Stretch Goal):** Si hiciste las cosas bien y te quedan 2 o 3 semanas libres, **ahí recién** te metés a jugar con un Colab, `Unsloth` y `Llama 3.2 3B`. Intentás entrenar el modelo con el dataset que creaste en el Mes 1 y exportarlo a GGUF para correrlo local con `Ollama`.
  - *¿Funcionó?* Lo agregás a la tesis como un capítulo espectacular de "Investigación y Trabajo Futuro" y cambiás la llamada de la API por tu modelo local en la demo.
  - *¿Falló o te quedaste sin tiempo?* No pasa nada. Tu proyecto principal con Postgres y la API funciona impecable. No arriesgaste nada.



---

## 🎓 Cómo defender este proyecto ante el Tribunal (El relato académico)

Para que los profesores te pongan un 10, tenés que vender las decisiones de diseño no como "lo que me salió más fácil", sino como **decisiones estratégicas de ingeniería**:

* **¿Por qué Postgres y no Neo4j?:** *"Evalué motores de grafos nativos como Neo4j, pero para un MVP de 300 ingredientes las travesías no requieren recursividad compleja. Elegí PostgreSQL por simplicidad operativa, menor sobrecarga en el despliegue y rendimiento óptimo mediante índices compuestos, demostrando criterio de economía de recursos."*
* **¿Por qué un Dataset Híbrido con IA?:** *"Compilar un mapa de sabores profesional requiere años de trabajo sommelier. Utilicé ingeniería de prompts sobre un LLM para generar un pipeline de datos sintéticos fuera de línea, aplicando técnicas de curación y limpieza manual posterior para garantizar la fidelidad de la base de conocimiento."*
* **El enfoque de Arquitectura:** *"Diseñé una arquitectura desacoplada donde la base de datos relacional actúa como la 'fuente de verdad' inmutable para garantizar la estabilidad de la interfaz de usuario, delegando en los modelos de lenguaje únicamente las tareas de generación de lenguaje natural y análisis organoléptico en tiempo real."*

Este camino te garantiza aprender a estructurar un proyecto real de software, tocar IA de forma seria (tanto offline en pipelines como online en features) y tener el control absoluto del reloj.