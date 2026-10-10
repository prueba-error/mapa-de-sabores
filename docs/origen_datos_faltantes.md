# Origen y Justificación Fisicoquímica de Datos Faltantes

Este documento consolida la investigación bromatológica y el sustento cromatográfico (GC-MS / GC-O) utilizado para parametrizar matrices e ingredientes que no contaban con cobertura adecuada o desagregada en los catálogos primarios (*FlavorDB* y *Ahn et al.*). Cada sección detalla la cinética química, la selección de compuestos volátiles clave y su conectividad resultante en el grafo de sabores.

---

## 1. Taxonomía Fisicoquímica de Cortes Vacunos

### 1.1 Fundamento Biomecánico y Cinético de la Diferenciación

En la ciencia de los alimentos, el flavor cárnico no es estático ni uniforme: depende de la interacción entre tres matrices precursoras primarias:

1. **Aminoácidos libres y azúcares reductores** en la fase acuosa sarcoplasmática (reactivos hidrosolubles de Maillard).
2. **Lípidos intramusculares e intermusculares** (triglicéridos y fosfolípidos de membrana propensos a termodegradación oxidativa).
3. **Fracción proteica estructural y conectiva** (proporción de colágeno perimisial/epimisial y mioglobina sarcoplasmática).

El método de cocción actúa como el selector cinético fundamental: el calor seco a alta temperatura ($>140\,^\circ\text{C}$) activa la pirólisis y la condensación de Maillard en superficie; el calor húmedo prolongado ($80-95\,^\circ\text{C}$) hidroliza el colágeno a gelatina y promueve degradaciones hidrotérmicas de aminoácidos azufrados.

---

### 1.2 Desglose Teórico y Origen de Datos por Perfil

#### A. Corte Vacuno Magro / Steak (`beef_lean_steak`)

- **Matriz anatómica representativa:** Lomo (*psoas major*), Cuadril (*gluteus medius*), Nalga (*semimembranosus*).
- **Parámetros fisicoquímicos:**
  - Grasa intramuscular baja ($\le 3-5\%$).
  - Alta proporción de mioglobina y hierro hémico libre.
  - Colágeno bajo o soluble, apto para cocción rápida de calor radiante o conducción directa (*sear*, *grill*).
- **Origen y justificación de los compuestos volátiles (GC-MS):**
  - **`methylpyrazine` y `acetylpyrazine`:** Formados por reacción de Maillard superficial (degradación de Strecker entre dicarbonilos y aminoácidos libres). Proveen la nota tostada a costra crocante sellada.
  - **`methional`:** Formado por degradación de Strecker específica de la L-metionina. Aporta el descriptor central de "carne cocida" (*cooked meat / potato-like*).
  - **`thiophene`:** Derivado heterocíclico azufrado originado de la interacción de cisteína y azúcares a alta temperatura; clave en el aroma umami cárnico.
  - **`guaiacol` y `4vg` (4-vinilguayacol):** Fenoles volátiles derivados de la pirólisis térmica proteico-lipídica y componentes de humo en parrilla; responsables del fondo ahumado y rostizado.
  - **`hexanal`:** Presente en niveles basales controlados proveniente de la termoxidación mínima de fosfolípidos de membrana celular.

---

#### B. Corte Vacuno Graso (`beef_fatty_cut`)

- **Matriz anatómica representativa:** Asado de tira / Costillar, Vacío, Ojo de bife (*longissimus thoracis* con marmoleo), Entraña.
- **Parámetros fisicoquímicos:**
  - Alto contenido de grasa intramuscular e intermuscular ($>12-25\%$).
  - Cinética bifásica: tostado superficial de Maillard en combinación con pirólisis continua de triglicéridos fundidos sobre las brasas/fuente de calor.
- **Origen y justificación de los compuestos volátiles (GC-MS):**
  - **`octanal` y `nonanal`:** Aldehídos alifáticos saturados lineales generados por termoxidación de ácidos grasos monoinsaturados (principalmente ácido oleico, el más abundante en la grasa bovina). Otorgan el descriptor graso, untuoso y animal dulce característico del asado.
  - **`hexanal` (concentración elevada):** Derivado de la descomposición térmica del ácido linoleico ($\omega\text{-6}$); aporta notas de grasa cocida.
  - **`gamma_decalactone`:** Lactona formada por la ciclación térmica de hidroxiácidos presentes en la grasa intramuscular; imparte notas mantecosas y cerosas de fondo.
  - **`diacetyl`:** Dicetona asociada al perfil mantecoso de la grasa fundida.
  - **`guaiacol` / `4vg` / `thiophene`:** Amplificados por el goteo de grasa sobre la fuente calórica que se vaporiza y redeposita sobre la carne en forma de aerosoles fenólicos aromáticos.

---

#### C. Corte Vacuno Rico en Colágeno / Estofado (`beef_braised_collagen`)

- **Matriz anatómica representativa:** Roast beef / Aguja, Osobuco / Garrón (*extensor carpi radialis*), Tapa de asado.
- **Parámetros fisicoquímicos:**
  - Alto contenido de tejido conectivo (colágeno tipo I y III, $>1.5-2.5\%\, \text{peso húmedo}$).
  - Cocción prolongada en medio acuoso ($>1.5-3\,\text{horas}$). Al superarse los $65-70\,^\circ\text{C}$ de manera sostenida, las hélices triples de tropocolágeno se desnaturalizan e hidrolizan irreversiblemente en cadenas de gelatina soluble.
- **Origen y justificación de los compuestos volátiles (GC-MS):**
  - **`dimethyl_sulfide` (DMS) y `dimethyl_trisulfide` (DMTS):** Sulfuros volátiles hidrosolubles de umbral olfativo ultra-bajo, originados por la degradación hidrotérmica continua de aminoácidos azufrados (metionina y cisteína). Son los marcadores indiscutibles de caldos concentrados, estofados y carne cocida por hervor.
  - **`methional`:** Dominante en medio acuoso; aroma terroso y a carne de olla.
  - **`thiophene`:** Se conserva como marcador umami cárnico termoestable.
  - **Atenuación de fenoles y pirazinas superiores:** Al no alcanzarse temperaturas de pirólisis superficial ($>140\,^\circ\text{C}$) debido a la presencia de agua líquida ($T \approx 100\,^\circ\text{C}$ máx.), los compuestos de costra sellada (`guaiacol`, `acetylpyrazine`) decrecen significativamente o son reemplazados por el perfil azufrado-aldehídico de cocción lenta.

---

### 1.3 Conexiones Resultantes en el Grafo de Sabores

- **`beef_fatty_cut`** adquiere aristas directas con matrices oleosas y lácteas maduras (`butter`, `ghee`, `cheddar`, `avocado`) debido a la tríada lipídica `octanal` + `nonanal` + `gamma_decalactone`.
- **`beef_lean_steak`** enlaza con especias y productos de tueste alto (`coffee`, `black_pepper`, `tofu`, `sesame_oil`) gracias a las pirazinas y fenoles de sellado (`4vg`, `guaiacol`, `acetylpyrazine`).
- **`beef_braised_collagen`** comparte vecindad topológica con alliums cocidos, caldos y hongos (`onion`, `garlic`, `shiitake`, `beef_stock`, `dashi`) por la saturación de puentes disulfuro y sulfuros volátiles (`dimethyl_sulfide`, `dimethyl_trisulfide`, `methional`).

---

## 2. Dulce de Leche: Perfil Fisicoquímico y Ontología

### 2.1 Matriz y Cinética de Reacción

El dulce de leche es un concentrado lácteo elaborado a partir de leche fluida y sacarosa sometidas a concentración térmica a presión atmosférica, con el agregado de bicarbonato de sodio ($\text{NaHCO}_3$):

- **Catálisis alcalina de Maillard:** La leche cruda posee un pH natural de $\sim 6.6$. La evaporación concentra las sales minerales (precipitando fosfato de calcio y liberando protones $\text{H}^+$), lo que descendería el pH e inhibiría el pardeamiento no enzimático. La adición de bicarbonato amortigua el sistema en un rango de **pH 6.8 a 7.2**, desprotonando los grupos amino libres ($\varepsilon-\text{NH}_2$ de la **L-lisina** en las caseínas) para maximizar la velocidad de condensación con la **lactosa** (azúcar reductor).

- **Caramelización concurrente:** Por encima de los $100^\circ\text{C}$ sostenidos, la sacarosa sufre hidrólisis parcial (glucosa + fructosa) y deshidratación térmica directa, generando furanos y piranonas en paralelo a las rutas de Amadori.
- **Ciclación lipídica:** La hidrólisis moderada de los triglicéridos de la grasa butirosa provee hidroxiácidos que ciclan térmicamente hacia lactonas.

---

### 2.2 Justificación de Compuestos Volátiles (Datos GC-MS / GC-O)

Cada compuesto asignado proviene del aislamiento cromatográfico validado en matrices lácteas caramelizadas y literatura bromatológica regional (INTA / CONICET / *Journal of Dairy Science*):

| Compuesto | Familia Química | Vía Metabólica / Térmica | Descriptor Sensorial en la Matriz |
| :--- | :--- | :--- | :--- |
| **`maltol`** | Piranona | Degradación de disacáridos y reordenamiento de Amadori. | Algodón de azúcar, caramelo cocido, nota dulce profunda. |
| **`furaneol`** | Furanona | Deshidratación y ciclación de intermediarios de Maillard. | Toffee, azúcar tostado, dulzor frutado cocido. |
| **`furfural`** | Furano | Deshidratación térmica de hexosas/pentosas. | Pan tostado, almendrado, corteza horneada. |
| **`delta_decalactone`** | Lactona | Ciclación intramolecular de $\delta$-hidroxiácidos de la grasa butirosa. | Manteca cocida, lácteo cremoso, fondo untuoso. |
| **`gamma_decalactone`** | Lactona | Ciclación intramolecular de $\gamma$-hidroxiácidos lipídicos. | Frutado dulce, lácteo aterciopelado. |
| **`diacetyl`** | Dicetona | Termodegradación de precursores lácteos y citratos. | Manteca fresca, untuosidad grasa. |
| **`acetoin`** | Hidroxicetona | Reducción de diacetilo y piruvato durante el calentamiento. | Lácteo suave, cremosidad redondeada. |
| **`acetylpyrazine`** | Pirazina | Reacción de Strecker (dicarbonilos + aminoácidos lácteos). | Pochoclo/cereal tostado, avellana tostada. |
| **`methylpyrazine`** | Pirazina | Condensación de Strecker por calor prolongado en paila. | Fondo de nuez, corteza crujiente tostada. |
| **`vanillin`** | Fenol aldehídico | Estándar bromatológico (CAA Art. 592) y degradación fenólica. | Vainilla dulce, balsámico, calidez aromática. |

---

### 2.3 Conectividad en el Grafo (*Food Pairing*)

La inclusión de este vector de compuestos genera enlaces inmediatos con:

- **Frutos secos (`hazelnut`, `peanut`, `walnut`, `pecan`):** Vía `acetylpyrazine`, `methylpyrazine` y `maltol`.
- **Lácteos grasos (`butter`, `cream`, `mascarpone`):** Vía `diacetyl`, `delta_decalactone`, `gamma_decalactone` y `acetoin`.
- **Derivados de tostado (`coffee`, `chocolate`):** Vía pirazinas, `maltol` y `furaneol`.
- **Frutas dulces (`banana`, `apple`):** Vía `vanillin` y furanonas.

---

## 3. Salsa de Ostras: Perfil Fisicoquímico y Ontología

### 3.1 Matriz y Cinética de Reacción

La salsa de ostras (*oyster sauce*) es un condimento viscoso y concentrado originario de la gastronomía cantonesa, producido a partir de la reducción prolongada del extracto acuoso de moluscos bivalvos (*Crassostrea gigas* / *Saccostrea glomerata*), sal, azúcar (sacarosa) y almidones espesantes:

- **Hidrólisis de péptidos sarcoplasmáticos y umami sinérgico:** Durante la ebullición prolongada del caldo de ostras, las proteínas musculares del molusco sufren desnaturalización e hidrólisis parcial, liberando elevadas concentraciones de ácido glutámico libre, glicina y nucleótidos $5'$ (inosina monofosfato, IMP, y guanosina monofosfato, GMP). La interacción de glutamato con ribonucleótidos $5'$ actúa como un agonista alostérico sobre los receptores gustativos heterodiméricos T1R1/T1R3, multiplicando la percepción del sabor umami por un factor cinético de hasta $8\times$.

- **Condensación de Maillard y caramelización por concentración térmica:** La mezcla del caldo salino de ostras con sacarosa se somete a evaporación controlada a fuego lento ($100-110^\circ\text{C}$). La condensación entre azúcares reductores y aminoácidos libres desata la degradación de Strecker, generando pirazinas tostadas y furanonas, mientras que la pirólisis simultánea de azúcares libres produce piranonas caramelizadas (`maltol`) que redondean el perfil dulce-salado.

- **Degradación térmica de osmoprotectores marinos:** Los moluscos marinos sintetizan osmólitos intracelulares nitrogenados y azufrados para equilibrar la presión osmótica frente al agua de mar, principalmente óxido de trimetilamina (TMAO) y dimetilsulfoniopropionato (DMSP). El calentamiento sostenido hidroliza el DMSP en dimetilsulfuro (DMS) y reduce térmicamente el TMAO a trimetilamina (TMA), estableciendo la signatura aromática marina distintiva del producto.

---

### 3.2 Justificación de Compuestos Volátiles (Datos GC-MS / GC-O)

Cada compuesto asignado proviene del aislamiento cromatográfico en matrices de extracto de ostra fermentado/reducido, perfiles de Food Pairing de mariscos y bases de datos bromatológicas (FooDB `FOOD00780` / *Journal of Agricultural and Food Chemistry*):

| Compuesto | Familia Química | Vía Metabólica / Térmica | Descriptor Sensorial en la Matriz |
| :--- | :--- | :--- | :--- |
| **`dimethyl_sulfide`** | Sulfuro alifático | Termólisis hidrolítica de dimetilsulfoniopropionato (DMSP) del molusco. | Salino, brisa marina, repollo cocido dulce, fondo ostreícola. |
| **`trimethylamine`** | Amina alifática | Reducción térmica del óxido de trimetilamina (TMAO) muscular. | Pescado salado, marisco característico, nota marina punzante. |
| **`methional`** | Aldehído azufrado | Degradación de Strecker de la L-metionina con intermediarios dicarbonílicos. | Caldo concentrado, papa cocida, fondo cárnico/umami denso. |
| **`methylpyrazine`** | Pirazina | Condensación de Strecker de Maillard durante la reducción en caldera. | Tostado, fruto seco, salsa de soja tostada, costra sabrosa. |
| **`maltol`** | Piranona | Pirólisis y degradación térmica de sacarosa en presencia de sales. | Caramelo quemado, algodón de azúcar, dulzor profundo. |
| **`furfural`** | Furano | Deshidratación térmica ácida de pentosas y hexosas. | Pan horneado, corteza tostada, amaderado suave. |
| **`acetic_acid`** | Ácido carboxílico | Oxidación bacteriana basal y fermentación secundaria de azúcares. | Acidez punzante limpia, balance del perfil graso/denso. |

---

### 3.3 Conectividad en el Grafo (*Food Pairing*)

La parametrización de este vector químico establece aristas deterministas de alta afinidad con:

- **Mariscos y moluscos (`oyster`, `shrimp`, `scallop`, `squid`, `mackerel`):** Enlace directo a través de los marcadores marinos primarios `dimethyl_sulfide` y `trimethylamine`.
- **Proteínas cárnicas y aves (`beef`, `pork`, `chicken`):** Enlace potente vía `methional`, `methylpyrazine` y precursores Maillard cárnicos, modelando las combinaciones clásicas de la cocina de wok (*stir-fry*).
- **Alliums y crucíferas salteadas (`scallion`, `garlic`, `ginger`, `cabbage`, `broccoli`, `bok_choy`):** Sinergia mediante puentes de sulfuros alifáticos y pirazinas tostadas.
- **Salsas y hongos de perfil umami (`soy_sauce`, `shiitake`, `miso`, `dashi`):** Coincidencia topológica central en `methional`, `furfural` y `methylpyrazine`.

---

## 4. Proteína de Soja Texturizada: Perfil Fisicoquímico y Ontología

### 4.1 Matriz y Cinética de Reacción

La proteína de soja texturizada (PST / *textured soy protein / textured vegetable protein*) es un producto obtenido mediante la extrusión termoplástica continua de harina desgrasada de soja (*Glycine max*), caracterizada por un contenido proteico $\ge 50-70\%$ en base seca (dominado por las globulinas de almacenamiento **glicinina 11S** y **$\beta$-conglicinina 7S**):

- **Termocizallamiento y texturización proteica:** En el interior del cilindro extrusor, el material es sometido a gradientes de alta temperatura ($140-180^\circ\text{C}$), presiones hidrostáticas elevadas ($>20-40\,\text{bar}$) y alto cizallamiento mecánico. Estas condiciones desnaturalizan irreversiblemente las conformaciones globulares nativas de las proteínas, desenrollando las cadenas peptídicas. Al salir por la boquilla a presión atmosférica, la evaporación súbita del agua genera microalvéolos y alinea las cadenas macromoleculares, formándose nuevos enlaces cruzados de puentes disulfuro ($\text{S-S}$) intermoleculares y asociaciones hidrofóbicas que mimetizan la viscoelasticidad y resistencia a la mordida del tejido muscular animal.

- **Cinética oxidativa de la lipoxigenasa (LOX):** Durante la molienda del grano de soja previo a la extracción lipídica, la enzima endógena lipoxigenasa cataliza la hidroperoxidación de los ácidos grasos poliinsaturados residuales (ácidos linoleico y linolénico). La termodescomposición subsecuente de los 9- y 13-hidroperóxidos libera aldehídos saturados lineales, fundamentalmente **hexanal**, responsable de la nota "leguminosa / poroto verde" (*beany off-flavor*) característica de los derivados de soja.

- **Reacciones de Maillard en extrusión seca:** Los azúcares solubles residuales de la matriz de soja (sacarosa y oligosacáridos estaquiosa/rafinosa) reaccionan con los grupos amino libres ($\varepsilon-\text{NH}_2$ de lisina y arginina) a las temperaturas extremas del barril extrusor, generando pirazinas aromáticas tostadas y aldehídos aromáticos que otorgan su fondo de nuez y cereal.

---

### 4.2 Justificación de Compuestos Volátiles (Datos GC-MS / GC-O)

Los compuestos volátiles seleccionados corresponden a los aislados por microextracción en fase sólida (SPME) acoplada a GC-MS y olfatometría en harinas de soja extrudadas (FooDB `FDB014418` / *Food Chemistry* / *LWT - Food Science and Technology*):

| Compuesto | Familia Química | Vía Metabólica / Térmica | Descriptor Sensorial en la Matriz |
| :--- | :--- | :--- | :--- |
| **`hexanal`** | Aldehído alifático | Escisión térmica y oxidativa de hidroperóxidos del ácido linoleico por LOX. | Verde leguminoso, poroto de soja crudo, fondo herbal fresco. |
| **`1_octen_3_ol`** | Alcohol alifático | Termoclivaje oxidativo secundario de lípidos poliinsaturados. | Terroso, hongo fresco, vegetal cocido, humedad herbácea. |
| **`methional`** | Aldehído azufrado | Degradación de Strecker térmica a partir de L-metionina en la extrusión. | Caldo vegetal cárnico, papa hervida, nota salada profunda. |
| **`methylpyrazine`** | Pirazina | Reacción de Maillard térmica bajo alto cizallamiento ($>150^\circ\text{C}$). | Cereal tostado, nuez, grano inflado, corteza horneada. |
| **`benzaldehyde`** | Aldehído aromático | Degradación oxidativa de la L-fenilalanina proteica. | Almendra amarga, nuez sutil, fondo dulce aromático. |
| **`nonanal`** | Aldehído alifático | Autoxidación de ácidos grasos monoinsaturados (ácido oleico residual). | Graso ceroso, cuerpo untuoso, fondo cítrico-verde atenuado. |

---

### 4.3 Conectividad en el Grafo (*Food Pairing*)

La formulación de este perfil fisicoquímico ubica a la proteína de soja texturizada en una encrucijada estratégica dentro del grafo de sabores:

- **Derivados de legumbres y semillas (`tofu`, `soy_sauce`, `tempeh`, `edamame`, `peanut`):** Máxima afinidad y consonancia organoléptica natural vía `hexanal`, `methylpyrazine` y `benzaldehyde`.
- **Hongos y setas cultivadas (`shiitake`, `button_mushroom`, `portobello`):** Conexión clave mediante `1_octen_3_ol` (el alcohol aromático primario del reino fúngico), reproduciendo maridajes clásicos de sustitución cárnica vegetariana y salteados.
- **Bases cárnicas y sofritos para hidratación (`beef`, `chicken`, `onion`, `garlic`, `paprika`, `cumin`):** Coincidencia en `methional`, `methylpyrazine` y `nonanal`. Dado que la matriz esponjosa de la PST actúa como un secuestrador y transportador físico de aromas lipofílicos durante la cocción húmeda o estofado, estos enlaces reflejan su versatilidad gastronómica real.
