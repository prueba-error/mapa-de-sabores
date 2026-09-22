# Mapa de Sabores

**Sistema Web Interactivo de Descubrimiento Gastronómico mediante Grafos de Sabores asistido por Inteligencia Artificial**

**Proyecto Final - Desarrollo de Sistemas Web**
**Alumno:** Diego Rafael Guaraz

---

## 1. Qué es este proyecto

**Mapa de Sabores** es una plataforma web que permite explorar combinaciones de ingredientes (_flavor pairing_) mediante un **Grafo de Sabores** interactivo, con explicaciones organolépticas generadas por IA y una arquitectura donde la certeza de las relaciones vive en PostgreSQL y la IA actúa como potenciador, no como fuente de verdad en tiempo real.

Para el resumen completo del problema, los objetivos y las decisiones de diseño, ver **[PROYECTO.md](./PROYECTO.md)**.

---

## 2. Documentación del proyecto

| Documento | Contenido |
| :--- | :--- |
| **[PROYECTO.md](./PROYECTO.md)** | Documento académico principal: problema, objetivos, arquitectura, decisiones de diseño, alcance, riesgos y viabilidad. Punto de partida para la defensa. |
| **[SPEC.md](./SPEC.md)** | Anexo técnico: esquema DDL, endpoints REST, pipeline de datos, seguridad y estrategia de pruebas. |
| **[PLAN.md](./PLAN.md)** | Cronograma de 4 sprints, secuencia de kickoff y archivos de infraestructura (`.env.example`, `docker-compose.yml`). |

---

<!-- ## 3. Inicio rápido (desarrollo local)

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/mapa-de-sabores.git
cd mapa-de-sabores

# 2. Copiar archivo de variables de entorno (ver PLAN.md)
cp .env.example .env

# 3. Levantar servicios con Docker Compose (PostgreSQL + FastAPI)
docker compose up -d --build

# 4. Verificar logs de migraciones y servidor backend
docker compose logs -f backend -->
```

Para migraciones, carga del dataset y comandos de prueba, ver **[PLAN.md](./PLAN.md)**.
