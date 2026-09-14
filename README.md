# Mapa de Sabores

**Sistema Web Interactivo de Descubrimiento Gastronómico mediante Grafos de Sabores asistido por Inteligencia Artificial**

**Proyecto Final - Desarrollo de Sistemas Web**  
**Alumno:** Diego Rafael Guaraz  

---

## 1. Visión General del Proyecto

**Mapa de Sabores** es una plataforma web que resuelve el desafío de la innovación y el maridaje culinario (_flavor pairing_) mediante una representación visual en forma de **Grafo de Sabores** interactivo y dinámico.

Permite a chefs, aficionados, sommeliers y mixólogos explorar combinaciones de ingredientes basadas en afinidad organoléptica y química, consultar recetas reales integradas y recibir explicaciones culinarias generadas en lenguaje natural por Inteligencia Artificial (LLM).

---

## 2. El Problema y la Solución

### El Problema
Tradicionalmente, el maridaje de ingredientes ha dependido de la intuición empírica o de enciclopedias culinarias estáticas. Aunque existen teorías científicas de maridaje de sabores (compartir compuestos aromáticos clave), no existen herramientas web abiertas e interactivas en español que combinen:
* Exploración visual intuitiva mediante grafos interactivos.
* Explicaciones organolépticas personalizadas generadas por IA.
* Búsqueda e indexación en tiempo real de recetas aplicadas.

### La Solución
Una aplicación web *Full-Stack* con arquitectura híbrida donde **la certeza de las relaciones reside en PostgreSQL** (garantizando consistencia, respuestas instantáneas y cero alucinaciones en la navegación) y **la Inteligencia Artificial actúa como un potenciador** en dos fases: compilación offline del dataset inicial y generación de prosa gastronómica online bajo demanda.

---

## 3. Stack Tecnológico

| Capa / Componente | Tecnología Seleccionada | Justificación Técnica |
| :--- | :--- | :--- |
| **Frontend UI** | **React (Vite) + Tailwind CSS** | Desarrollo modular rápido, bundle liviano y excelente rendimiento en renderizado. |
| **Grafo 2D** | **`react-force-graph-2d`** | Motor de simulación física en HTML5 Canvas (60 FPS) para visualización de nodos y aristas. |
| **Backend REST** | **FastAPI (Python 3.11)** | Asincronía nativa (`async/await`), rendimiento cercano a Node/Go y documentación OpenAPI automática. |
| **Base de Datos** | **PostgreSQL 16** | Modelo relacional robusto con índices compuestos bidireccionales (`ingredient_a_id < ingredient_b_id`). |
| **Migraciones DDL** | **Alembic + SQLAlchemy Core** | Control de versiones del esquema relacional y ejecución automática al desplegar. |
| **Inteligencia Artificial** | **Google Gemini Flash / OpenAI GPT-4o-mini / Ollama** | Interfaz agnóstica desacoplada (`LLMProvider`) con timeouts (3s), retries y fallback a DB. |
| **Testing Backend** | **Pytest + pytest-asyncio + httpx** | Pruebas unitarias TDD centradas en la lógica crítica de negocio (sinergia N x N, auth). |
| **Testing Frontend** | **Vitest + React Testing Library + MSW** | Pruebas de componentes, accesibilidad e interceptación de llamadas HTTP. |
| **CI/CD & DevOps** | **GitHub Actions + Docker Compose** | Integración continua automatizada y orquestación reproducible en contenedores. |

---

## 4. Arquitectura de Alto Nivel

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
|   |- Auth Controller & Security (JWT Session / Passlib)                          |
|   |- Ingredients & Pairings Service (SQLAlchemy Core)                             |
|   |- LLM Provider Service Interface (Gemini / OpenAI Adapter)                     |
|   |- Recipe Integration Service (Spoonacular Client + DB Cache)                   |
+-----------------------------------------------------------------------------------+
               |                                 |                         |
     SQL (SQLAlchemy/asyncpg)               HTTP API                  HTTP API
               v                                 v                         v
+-----------------------------+   +--------------------+    +----------------------+
|     PostgreSQL Database     |   |  External LLM API  |    |   Spoonacular API    |
| (Ingredients, Pairings, DB) |   | (Gemini / OpenAI)  |    | (Recetas Culinarias) |
+-----------------------------+   +--------------------+    +----------------------+
```

### Decisión Clave: PostgreSQL vs. Neo4j
Se optó por PostgreSQL debido a que en una red de 300 a 1,000 ingredientes las consultas de 1 o 2 saltos (_hops_) no justifican la sobrecarga operativa ni el consumo de memoria de Neo4j. Mediante índices compuestos y ordenamiento de IDs (`ingredient_a_id < ingredient_b_id`), Postgres resuelve las búsquedas bidireccionales en **< 10ms**, reduciendo drásticamente los costos de infraestructura.

---

## 5. Documentación del Proyecto

El proyecto cuenta con dos documentos técnicos detallados:

1. **[SPEC.md](./SPEC.md) - Especificación Técnica Detallada:**
   * Esquema relacional DDL completo y migraciones con Alembic.
   * Pipeline offline de datos, prompts en JSON Mode y suite anti-alucinaciones (`verify_coherence.py`).
   * Especificación de endpoints REST, contratos Pydantic v2 y función de sanitización de recetas (`sanitize_recipe_payload`).
   * Hardening de seguridad (Argon2id, JWT de sesión, Rate Limiting y resiliencia con fallbacks).
   * Lógica visual del grafo (1, 2 y N ingredientes, intensidad armónica) y Modelo Único de Accesibilidad.
   * Estrategia TDD, CI/CD en GitHub Actions y análisis de viabilidad económica.

2. **[PLAN.md](./PLAN.md) - Plan de Implementación Ágil (2 Meses / 4 Sprints):**
   * Cronograma detallado en 4 Sprints de 2 semanas con *Definition of Done*.
   * Secuencia inmediata de Kickoff en 5 pasos.
   * Configuración completa de entorno (`.env.example`, `docker-compose.yml`, `scripts/backup.sh`).

---

## 6. Inicio Rápido (Desarrollo Local)

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/mapa-de-sabores.git
cd mapa-de-sabores

# 2. Copiar archivo de variables de entorno (ver PLAN.md)
cp .env.example .env

# 3. Levantar servicios con Docker Compose (PostgreSQL + FastAPI)
docker compose up -d --build

# 4. Verificar logs de migraciones y servidor backend
docker compose logs -f backend
```

Para más detalles sobre la ejecución de migraciones, carga de datos y comandos de prueba, consultar **[PLAN.md](./PLAN.md)**.