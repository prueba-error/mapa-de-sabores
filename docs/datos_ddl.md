# Dulce de Leche: Perfil Fisicoquímico, Ontología y Justificación Teórica

---

## 1. Justificación Teórica y Origen Fisicoquímico

### A. Matriz y Cinética de Reacción

El dulce de leche es un concentrado lácteo elaborado a partir de leche fluida y sacarosa sometidas a concentración térmica a presión atmosférica, con el agregado de bicarbonato de sodio ($\text{NaHCO}_3$):

- **Catálisis alcalina de Maillard:** La leche cruda posee un pH natural de $\sim 6.6$. La evaporación concentra las sales minerales (precipitando fosfato de calcio y liberando protones $\text{H}^+$), lo que descendería el pH e inhibiría el pardeamiento no enzimático. La adición de bicarbonato amortigua el sistema en un rango de **pH 6.8 a 7.2**, desprotonando los grupos amino libres ($\varepsilon-\text{NH}_2$ de la **L-lisina** en las caseínas) para maximizar la velocidad de condensación con la **lactosa** (azúcar reductor).

- **Caramelización concurrente:** Por encima de los $100^\circ\text{C}$ sostenidos, la sacarosa sufre hidrólisis parcial (glucosa + fructosa) y deshidratación térmica directa, generando furanos y piranonas en paralelo a las rutas de Amadori.
- **Ciclación lipídica:** La hidrólisis moderada de los triglicéridos de la grasa butirosa provee hidroxiácidos que ciclan térmicamente hacia lactonas.

---

### B. Justificación de Compuestos Volátiles (Datos GC-MS / GC-O)

Cada compuesto asignado proviene del aislamiento cromatográfico validado en matrices lácteas caramelizadas y literatura bromatológica regional (INTA / CONICET / _Journal of Dairy Science_):

| Compuesto               | Familia Química  | Vía Metabólica / Térmica                                                 | Descriptor Sensorial en la Matriz                        |
| :---------------------- | :--------------- | :----------------------------------------------------------------------- | :------------------------------------------------------- |
| **`maltol`**            | Piranona         | Degradación de disacáridos y reordenamiento de Amadori.                  | Algodón de azúcar, caramelo cocido, nota dulce profunda. |
| **`furaneol`**          | Furanona         | Deshidratación y ciclación de intermediarios de Maillard.                | Toffee, azúcar tostado, dulzor frutado cocido.           |
| **`furfural`**          | Furano           | Deshidratación térmica de hexosas/pentosas.                              | Pan tostado, almendrado, corteza horneada.               |
| **`delta_decalactone`** | Lactona          | Ciclación intramolecular de $\delta$-hidroxiácidos de la grasa butirosa. | Manteca cocida, lácteo cremoso, fondo untuoso.           |
| **`gamma_decalactone`** | Lactona          | Ciclación intramolecular de $\gamma$-hidroxiácidos lipídicos.            | Frutado dulce, lácteo aterciopelado.                     |
| **`diacetyl`**          | Dicetona         | Termodegradación de precursores lácteos y citratos.                      | Manteca fresca, untuosidad grasa.                        |
| **`acetoin`**           | Hidroxicetona    | Reducción de diacetilo y piruvato durante el calentamiento.              | Lácteo suave, cremosidad redondeada.                     |
| **`acetylpyrazine`**    | Pirazina         | Reacción de Strecker (dicarbonilos + aminoácidos lácteos).               | Pochoclo/cereal tostado, avellana tostada.               |
| **`methylpyrazine`**    | Pirazina         | Condensación de Strecker por calor prolongado en paila.                  | Fondo de nuez, corteza crujiente tostada.                |
| **`vanillin`**          | Fenol aldehídico | Estándar bromatológico (CAA Art. 592) y degradación fenólica.            | Vainilla dulce, balsámico, calidez aromática.            |

---

### C. Conectividad en el Grafo (_Food Pairing_)

La inclusión de este vector de compuestos genera enlaces inmediatos con:

- **Frutos secos (`hazelnut`, `peanut`, `walnut`, `pecan`):** Vía `acetylpyrazine`, `methylpyrazine` y `maltol`.
- **Lácteos grasos (`butter`, `cream`, `mascarpone`):** Vía `diacetyl`, `delta_decalactone`, `gamma_decalactone` y `acetoin`.
- **Derivados de tostado (`coffee`, `chocolate`):** Vía pirazinas, `maltol` y `furaneol`.
- **Frutas dulces (`banana`, `apple`):** Vía `vanillin` y furanonas.
