# Mapa de Sabores

**Sistema Web Interactivo de Descubrimiento Gastronómico mediante Grafos de Sabores asistido por Inteligencia Artificial**

**Proyecto Final - Desarrollo de Sistemas Web**
**Alumno:** Diego Rafael Guaraz

---

## 1. Qué es este proyecto

**Mapa de Sabores** es una plataforma web que permite explorar combinaciones de ingredientes (_flavor pairing_) mediante un **Grafo de Sabores** interactivo. La certeza y afinidad de las relaciones se fundamenta en **datos empíricos de química de aromas (FlavorDB y el estudio fundamental de Ahn et al., Nature Scientific Reports 2011)** calculados matemáticamente mediante el índice de Jaccard sobre compuestos volátiles compartidos. La Inteligencia Artificial actúa estrictamente como enriquecedor organoléptico y lingüístico en lenguaje natural, garantizando que el sistema sea verificable, científico y libre de alucinaciones.

Para el resumen completo del problema, los objetivos y las decisiones de diseño, ver **[PROYECTO.md](./PROYECTO.md)**.

---

## 2. Documentación del proyecto

| Documento | Contenido |
| :--- | :--- |
| **[PROYECTO.md](./PROYECTO.md)** | Documento académico principal: problema, objetivos, arquitectura, decisiones de diseño, alcance, riesgos y viabilidad. Punto de partida para la defensa. |
| **[SPEC.md](./SPEC.md)** | Anexo técnico: esquema DDL, endpoints REST, pipeline de datos, seguridad y estrategia de pruebas. |
| **[PLAN.md](./PLAN.md)** | Cronograma de 4 sprints, secuencia de kickoff y archivos de infraestructura (`.env.example`, `docker-compose.yml`). |

---

Para instrucciones de arranque local, migraciones, carga del dataset y comandos de prueba, ver **[PLAN.md](./PLAN.md)**.
