# Justificación Teórica: Evaluación de Sinergia NxN, Pares Débiles y Cobertura

---

## 1. Contexto y Problema Computacional

En el sistema **Mapa de Sabores**, el catálogo de ingredientes cuenta con $N = 360$ elementos clasificados. El espacio combinatorio total de pares no dirigidos posibles es:

$$\binom{N}{2} = \frac{N \cdot (N - 1)}{2} = \frac{360 \cdot 359}{2} = 64.620 \text{ pares posibles}$$

La literatura científica en química de alimentos (*Ahn et al., Nature 2011*) demuestra que la red de maridajes moleculares es un **grafo disperso** (*sparse graph*): la inmensa mayoría de las combinaciones posibles entre ingredientes de reinos o ecosistemas disímiles poseen una intersección molecular nula ($C_A \cap C_B = \emptyset$) o irrelevante.

Por razones de eficiencia computacional, renderizado fluido en el Canvas 2D (60 FPS) y limpieza de ruido visual, la base de datos no persiste 64.000 aristas vacías. Esto plantea dos preguntas arquitectónicas fundamentales que este documento fundamenta:
1. ¿Cómo se tratan los ingredientes con **poca afinidad**?
2. ¿Qué ocurre cuando un usuario elige en el Laboratorio dos ingredientes **muy distantes, sin enlace precargado o sin afinidad**?

---

## 2. Tratamiento de Maridajes de Baja Afinidad ($0.15 \le S < 0.45$)

Contrario a la intuición de descartar toda afinidad baja, **Mapa de Sabores preserva deliberadamente más de 1.500 maridajes débiles/discordantes** en la base de datos relacional (`flavor_pairings`):

### A. Valor Culinario y Pedagógico
En gastronomía profesional, conocer qué ingredientes **no armonizan** o chocan químicamente es tan valioso como conocer las sinergias clásicas. Permite al usuario:
- Identificar pares antagónicos o discordantes.
- Utilizar el modo de exploración **"Peores Maridajes / Contrastes Extremos"** (estipulado en `SPEC.md`, Sección 5).
- Detectar desbalances en recetas complejas.

### B. Algoritmo del Ingrediente Discordante (`clashing_ingredients`)
Al evaluar una combinación grupal de $N \ge 3$ ingredientes en el Laboratorio (`POST /api/v1/pairings/evaluate`):
1. El backend computa la afinidad promedio de cada ingrediente frente a todos los demás miembros del grupo que poseen dato:
   $$\bar{S}_i = \frac{1}{|D_i|} \sum_{j \in D_i} S(i, j)$$
   *(donde $D_i$ es el subconjunto de ingredientes del grupo con dato frente a $i$)*.
2. Todo ingrediente cuya afinidad promedio caiga por debajo del umbral armónico ($\bar{S}_i < 0.45$) es marcado como **ingrediente discordante** (*clashing*), ordenados de menor a mayor afinidad promedio.
3. Para combinaciones binarias ($N = 2$), la lista `clashing_ingredients` permanece vacía por definición, ya que un par aislado representa una relación directa y no un elemento que desentona respecto a un colectivo.

---

## 3. Tratamiento de Ingredientes Distantes y Pares sin Dato

Cuando un usuario somete al Laboratorio ingredientes sin vínculo previo en la base de datos (por ejemplo, *Almeja + Chocolate* o *Brandy + Poroto Pallar*), el sistema responde bajo dos mecanismos complementarios:

### A. Modelo de Cobertura Científica (`coverage`) y Celdas Nulas
El sistema no inventa puntuaciones ficticias. Para reflejar total honestidad epistemológica y rigor metodológico:
- La matriz de adyacencia devuelta (`pairwise_matrix`) asigna **`null`** a toda intersección no documentada empíricamente.
- El objeto de respuesta incorpora un indicador explícito de **cobertura**:
  ```json
  "coverage": {
    "pairs_with_data": 2,
    "pairs_total": 3
  }
  ```
- **Cálculo del Índice Global (`synergy_score`):** El promedio se calcula **exclusivamente sobre los pares con dato real comprobable**, escalado a una escala porcentual entera ($0$ a $100$). Si ningún par del grupo posee dato, `synergy_score` es `null`.

### B. Capacidad de Evaluación Determinista Sobre la Marcha (*On-The-Fly*)
Dado que cada ingrediente almacena su vector de compuestos aromáticos volátiles en la tabla `ingredients`, el backend puede ejecutar la fórmula determinista en tiempo real con complejidad $O(|C_A| + |C_B|)$ ($\sim 1\,\mu\text{s}$ de CPU):

$$S(A, B) = \min\left(1.00, \; 0.50 \cdot \frac{|C_A \cap C_B|}{|C_A \cup C_B|} + 0.50 \cdot \frac{\min(|C_A \cap C_B|, 6)}{6}\right)$$

- **Si la intersección es vacía ($C_A \cap C_B = \emptyset$):**  
  El score matemático es determinísticamente **$0.00$** (cero puente aromático).
- **Si comparten moléculas no indexadas previamente en el seed:**  
  El cálculo sobre la marcha asigna instantáneamente el valor exacto y lo integra a la matriz grupal.

---

## 4. Ejemplo de Contrato de Respuesta

Para una terna donde dos ingredientes poseen alta y moderada afinidad, pero el tercero carece de enlace en la red o resulta discordante:

```json
{
  "synergy_score": 53,
  "coverage": {
    "pairs_with_data": 2,
    "pairs_total": 3
  },
  "pairwise_matrix": [
    [null, 0.94, 0.12],
    [0.94, null, null],
    [0.12, null, null]
  ],
  "clashing_ingredients": [
    {
      "ingredient_id": 88,
      "avg_affinity": 0.12
    }
  ]
}
```

---

## 5. Garantías para la Defensa Académica

1. **Determinismo Absoluto:** El score de sinergia grupal no depende de respuestas no reproducibles de un LLM; es una función matemática cerrada sobre datos físico-químicos.
2. **Transparencia Epistémica:** El usuario y el tribunal pueden distinguir claramente entre combinaciones validadas por la literatura empírica, maridajes de contraste estudiados, y vacíos de datos moleculares.
3. **Escalabilidad:** Separar la topología visual precomputada del grafo del cálculo analítico $N \times N$ permite sostener 60 FPS en el cliente mientras se brinda flexibilidad analítica en el servidor.
