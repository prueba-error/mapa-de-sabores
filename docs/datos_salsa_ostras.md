# Salsa de Ostras: Perfil Fisicoquímico, Ontología y Justificación Teórica

---

## 1. Justificación Teórica y Origen Fisicoquímico

### A. Matriz y Cinética de Reacción

La salsa de ostras (*oyster sauce*) es un condimento viscoso y concentrado originario de la gastronomía cantonesa, producido a partir de la reducción prolongada del extracto acuoso de moluscos bivalvos (*Crassostrea gigas* / *Saccostrea glomerata*), sal, azúcar (sacarosa) y almidones espesantes:

- **Hidrólisis de péptidos sarcoplasmáticos y umami sinérgico:** Durante la ebullición prolongada del caldo de ostras, las proteínas musculares del molusco sufren desnaturalización e hidrólisis parcial, liberando elevadas concentraciones de ácido glutámico libre, glicina y nucleótidos $5'$ (inosina monofosfato, IMP, y guanosina monofosfato, GMP). La interacción de glutamato con ribonucleótidos $5'$ actúa como un agonista alostérico sobre los receptores gustativos heterodiméricos T1R1/T1R3, multiplicando la percepción del sabor umami por un factor cinético de hasta $8\times$.

- **Condensación de Maillard y caramelización por concentración térmica:** La mezcla del caldo salino de ostras con sacarosa se somete a evaporación controlada a fuego lento ($100-110^\circ\text{C}$). La condensación entre azúcares reductores y aminoácidos libres desata la degradación de Strecker, generando pirazinas tostadas y furanonas, mientras que la pirólisis simultánea de azúcares libres produce piranonas caramelizadas (`maltol`) que redondean el perfil dulce-salado.

- **Degradación térmica de osmoprotectores marinos:** Los moluscos marinos sintetizan osmólitos intracelulares nitrogenados y azufrados para equilibrar la presión osmótica frente al agua de mar, principalmente óxido de trimetilamina (TMAO) y dimetilsulfoniopropionato (DMSP). El calentamiento sostenido hidroliza el DMSP en dimetilsulfuro (DMS) y reduce térmicamente el TMAO a trimetilamina (TMA), estableciendo la signatura aromática marina distintiva del producto.

---

### B. Justificación de Compuestos Volátiles (Datos GC-MS / GC-O)

Cada compuesto asignado proviene del aislamiento cromatográfico en matrices de extracto de ostra fermentado/reducido, perfiles de Food Pairing de mariscos y bases de datos bromatológicas (FooDB `FOOD00780` / *Journal of Agricultural and Food Chemistry*):

| Compuesto              | Familia Química    | Vía Metabólica / Térmica                                                    | Descriptor Sensorial en la Matriz                             |
| :--------------------- | :----------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------ |
| **`dimethyl_sulfide`** | Sulfuro alifático  | Termólisis hidrolítica de dimetilsulfoniopropionato (DMSP) del molusco.     | Salino, brisa marina, repollo cocido dulce, fondo ostreícola. |
| **`trimethylamine`**   | Amina alifática    | Reducción térmica del óxido de trimetilamina (TMAO) muscular.               | Pescado salado, marisco característico, nota marina punzante. |
| **`methional`**        | Aldehído azufrado  | Degradación de Strecker de la L-metionina con intermediarios dicarbonílicos.| Caldo concentrado, papa cocida, fondo cárnico/umami denso.   |
| **`methylpyrazine`**   | Pirazina           | Condensación de Strecker de Maillard durante la reducción en caldera.      | Tostado, fruto seco, salsa de soja tostada, costra sabrosa.   |
| **`maltol`**           | Piranona           | Pirólisis y degradación térmica de sacarosa en presencia de sales.          | Caramelo quemado, algodón de azúcar, dulzor profundo.         |
| **`furfural`**         | Furano             | Deshidratación térmica ácida de pentosas y hexosas.                         | Pan horneado, corteza tostada, amaderado suave.               |
| **`acetic_acid`**      | Ácido carboxílico  | Oxidación bacteriana basal y fermentación secundaria de azúcares.           | Acidez punzante limpia, balance del perfil graso/denso.       |

---

### C. Conectividad en el Grafo (*Food Pairing*)

La parametrización de este vector químico establece aristas deterministas de alta afinidad con:

- **Mariscos y moluscos (`oyster`, `shrimp`, `scallop`, `squid`, `mackerel`):** Enlace directo a través de los marcadores marinos primarios `dimethyl_sulfide` y `trimethylamine`.
- **Proteínas cárnicas y aves (`beef`, `pork`, `chicken`):** Enlace potente vía `methional`, `methylpyrazine` y precursores Maillard cárnicos, modelando las combinaciones clásicas de la cocina de wok (*stir-fry*).
- **Alliums y crucíferas salteadas (`scallion`, `garlic`, `ginger`, `cabbage`, `broccoli`, `bok_choy`):** Sinergia mediante puentes de sulfuros alifáticos y pirazinas tostadas.
- **Salsas y hongos de perfil umami (`soy_sauce`, `shiitake`, `miso`, `dashi`):** Coincidencia topológica central en `methional`, `furfural` y `methylpyrazine`.
