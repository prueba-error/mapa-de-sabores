# Origen y Justificación Fisicoquímica de Datos Faltantes

Los perfiles de volátiles de las siguientes matrices complejas **no son datos medidos directamente por GC-MS/GC-O para estas preparaciones exactas**, sino **perfiles estimados** a partir de literatura publicada sobre matrices iguales o muy similares y rutas cinéticas de formación conocidas (Maillard, Strecker, oxidación lipídica, degradación de osmolitos). Sirven como aproximación razonable para la topología del grafo de *food pairing*, donde cada compuesto clave lleva un nivel de confianza explícito.

**Niveles de confianza**

- **Alta:** el compuesto aparece reportado en literatura revisada (GC-MS y/o GC-O) para esa matriz o una muy cercana.
- **Media:** la ruta de formación es sólida y consistente con la literatura general, pero no pude confirmar el compuesto en esa matriz específica.
- **Baja:** inferido, con evidencia parcial o contradictoria. Conviene darle poco peso en el grafo o excluirlo.

Las referencias entre corchetes (`[R1]`, `[R2]`…) remiten a la sección 5.

---

## 1. Taxonomía Fisicoquímica de Cortes Vacunos

### 1.1 Fundamento

El flavor cárnico depende de tres matrices precursoras:

1. **Aminoácidos libres y azúcares reductores** de la fase acuosa (precursores hidrosolubles de Maillard y Strecker).
2. **Lípidos** intramusculares e intermusculares (oxidación y generación de aldehídos y lactonas).
3. **Fracción proteica y conectiva** (colágeno, mioglobina).

El método de cocción selecciona las rutas: el calor seco a alta temperatura favorece Maillard superficial; el calor húmedo prolongado favorece la degradación de aminoácidos azufrados y la solubilización gradual del colágeno. La literatura de síntesis coincide en que los compuestos de Maillard/Strecker pesan más en el aroma cárnico que los de oxidación lipídica, y en que los compuestos azufrados tienen umbrales muy bajos, por lo que contribuyen de forma desproporcionada `[R1][R2]`.

Compuestos clave de carne vacuna/porcina cocida según una revisión de GC-MS: hexanal, octanal, nonanal, (E,E)-2,4-decadienal, methional, methanethiol, 2-furfurylthiol, 2-methyl-3-furanthiol, 3-mercapto-2-pentanone, furaneol, 1-penten-3-one y 2-pentylfuran `[R2]`.

> **Nota sobre el colágeno:** Con calor húmedo prolongado el colágeno se desnaturaliza, se contrae y se solubiliza de forma **gradual**; su transformación a gelatina depende del tiempo y de la temperatura.

### 1.2 Perfiles

#### A. Corte magro / steak (`beef_lean_steak`)

Matriz representativa: lomo, cuadril, nalga. Grasa intramuscular baja; cocción rápida por calor seco.

| Compuesto | Origen | Confianza | Nota |
| :--- | :--- | :---: | :--- |
| `methylpyrazine` | Maillard / Strecker en superficie | Alta | Las pirazinas son una clase principal en carne cocida (nota tostada) `[R1][R3]`. |
| `acetylpyrazine` | Maillard / Strecker | Media | Típica de productos tostados; no confirmada en este trabajo para carne vacuna. |
| `methional` | Strecker de la metionina | Alta | Entre los odorantes más intensos en GC-O de sabor de carne vacuna asada `[R2][R4]`. |
| `2_methyl_3_furanthiol` | Cisteína + azúcares / tiamina | Alta | Uno de los odorantes cárnicos más potentes `[R2][R4]`. Es un *furantiol*. |
| `2_furfurylthiol` | Cisteína + pentosas | Media | Listado entre los volátiles clave de carne `[R2]`. |
| `hexanal` | Oxidación del ácido linoleico | Alta | Presente en niveles basales `[R2]`. |
| `guaiacol` | **Humo de leña/carbón** (lignina) | Baja | **Condicional:** solo aplica si el corte se cocina a la parrilla con humo. No es intrínseco de la carne. |


#### B. Corte graso (`beef_fatty_cut`)

Matriz representativa: asado de tira, vacío, ojo de bife con marmoleo. Grasa alta y cocción con fusión de triglicéridos.

| Compuesto | Origen | Confianza | Nota |
| :--- | :--- | :---: | :--- |
| `octanal`, `nonanal` | Oxidación de ácidos grasos monoinsaturados (oleico) | Alta | Listados entre los volátiles clave `[R2]`. |
| `hexanal` | Oxidación del ácido linoleico | Alta | `[R2]` |
| `e_e_2_4_decadienal` | Oxidación de linoleico | Alta | Clave en grasa cocida `[R2]`. |
| `delta_decalactone` | Lactonización de hidroxiácidos | Alta | Aroma "lácteo dulce" en GC-O de sebo vacuno `[R6]`. |
| `gamma_dodecalactone` | Lactonización de hidroxiácidos | Alta | Presente en sebo de grasa intramuscular `[R5]`. |
| `gamma_decalactone` | Lactonización de hidroxiácidos | Media | Detectada en GC-O de carne Wagyu y correlacionada con el aroma dulce, pero a concentración baja y no dominante `[R6][R7]`. |
| `guaiacol` | Humo | Baja | Solo condicional, como en el corte magro. |


#### C. Corte rico en colágeno / estofado (`beef_braised_collagen`)

Matriz representativa: roast beef, osobuco/garrón, aguja. Cocción larga en medio acuoso.

| Compuesto | Origen | Confianza | Nota |
| :--- | :--- | :---: | :--- |
| `methional` | Strecker de la metionina | Alta | Dominante en carne hervida y caldos `[R4]`. |
| `2_methyl_3_furanthiol` | Cisteína + azúcares | Alta | Reportado en carne cocida en medio acuoso `[R2][R4]`. |
| `methanethiol` | Degradación de metionina/cisteína | Media | Listado entre los volátiles clave `[R2]`; se ha detectado mercaptano en carne cocida en agua `[R12]`. |
| `dimethyl_sulfide` | Degradación de metionina | Media | Ruta plausible; **no verificado** para estofado vacuno en esta revisión. |
| `dimethyl_trisulfide` | Degradación de azufrados | Media | Idem. Verificado en proteína vegetal hidrolizada `[R10]`, no en estofado. |
| `hexanal` | Oxidación lipídica | Media | Menor que en cocción seca. |


### 1.3 Efecto en el grafo

- `beef_fatty_cut`: se mantienen los enlaces con matrices oleosas y lácteas (`butter`, `ghee`, `cheddar`, `avocado`) vía lactonas y aldehídos, pero ahora apoyados en `delta_decalactone` y `gamma_dodecalactone` y no en `diacetyl`. Los enlaces que dependían **solo** de `diacetyl` hay que revisarlos.
- `beef_lean_steak`: se mantienen los enlaces vía pirazinas (`coffee`, etc.). Se **debilitan** los enlaces que dependían de `4vg`/`guaiacol` (por ejemplo `black_pepper`, `sesame_oil`, `tofu` según cada caso). Hay que recalcular, no asumir.
- `beef_braised_collagen`: se mantiene el vínculo con alliums, caldos y hongos vía azufrados y `methional`. Se agregan los furantioles.
- Los slugs nuevos (`2_methyl_3_furanthiol`, `2_furfurylthiol`, `e_e_2_4_decadienal`, `gamma_dodecalactone`, `methanethiol`) deben mapearse al catálogo del grafo; si no existen, hay que agregarlos o usar el equivalente más cercano.

---

## 2. Dulce de Leche

### 2.1 Matriz y cinética

Leche y sacarosa concentradas por calor a presión atmosférica, con bicarbonato de sodio. Las rutas dominantes son Maillard (lactosa + grupos ε-amino de la lisina de las caseínas), caramelización de azúcares y formación de lactonas desde la grasa láctea.

- La pérdida de lisina disponible durante la elaboración de dulce de leche está documentada en la literatura `[R9]`, lo que respalda el rol de la lisina en el pardeamiento.
- Los valores de pH citados en el original (leche ~6,6; sistema amortiguado a 6,8-7,2 con bicarbonato) son plausibles, pero **no los verifiqué contra una fuente**; tratarlos como orientativos.
- El 5-hidroximetilfurfural (HMF) es un indicador reconocido de la intensidad del tratamiento térmico en dulce de leche `[R9]`. Es un marcador de proceso, no necesariamente un nodo aromático.

### 2.2 Compuestos

Respaldo directo: patentes de aromas de dulce de leche que listan maltol, furaneol, furfural y HMF como componentes de sabor generados térmicamente `[R8]`. El resto es inferencia de rutas lácteas conocidas. Hay un estudio con GC-MS en siete marcas comerciales `[R9]`; **no pude acceder a su lista completa de volátiles**, así que lo ideal es contrastar cada compuesto con ese texto.

| Compuesto | Vía | Descriptor | Confianza |
| :--- | :--- | :--- | :---: |
| `maltol` | Degradación de azúcares / Amadori | Caramelo, algodón de azúcar | Alta `[R8]` |
| `furaneol` | Maillard / caramelización | Toffee, dulzor cocido | Alta `[R8]` |
| `furfural` | Deshidratación térmica de azúcares | Pan tostado, almendra | Alta `[R8]` |
| `delta_decalactone` | Lactonización de la grasa láctea | Manteca cocida, lácteo cremoso | Media |
| `gamma_decalactone` | Lactonización | Frutado dulce, lácteo | Media |
| `diacetyl` | Citratos / precursores lácteos | Manteca | Media |
| `acetoin` | Reducción de diacetilo | Lácteo suave | Media |
| `acetylpyrazine` | Strecker | Cereal tostado | Media |
| `methylpyrazine` | Strecker | Nuez, tostado | Media |
| `vanillin` | **Aromatizante agregado** | Vainilla | Baja como compuesto de proceso |

**Vainillina:** Se trata como **ingrediente agregado** de formulación (saborizante), no como un compuesto formado intrínsecamente durante el proceso de elaboración del dulce de leche. Los enlaces con `banana` y `apple` que dependían de ella son un artefacto de formulación y conviene bajarles el peso. La mención "CAA Art. 592" **no está verificada**; confirmar el artículo exacto antes de citarlo.

### 2.3 Conectividad esperable

Frutos secos y derivados de tostado (vía pirazinas, maltol, furaneol), lácteos grasos (vía lactonas, diacetilo, acetoína) y cacao/café (vía pirazinas y furanonas).

---

## 3. Salsa de Ostras

### 3.1 Matriz y cinética

La salsa de ostras comercial actual no es el producto tradicional de ostras hervidas. Se elabora a partir de **extracto de ostra, salmuera, potenciadores de umami como glutamato monosódico y colorante caramelo**, con conservante `[R11]`. El aroma proviene de extracto de ostra más reacciones de Maillard y caramelización durante la concentración térmica.

- **Umami:** la sinergia entre glutamato y 5'-ribonucleótidos (IMP, GMP) es real y es la base del efecto potenciador (Yamaguchi, 1967; citado de memoria, ver sección 5).
- **Osmolitos marinos (DMSP → DMS, TMAO → TMA):** son rutas reales en moluscos, pero **no deben tomarse como la firma aromática del producto terminado**. En las cuatro salsas analizadas por HS-SPME-GC-MS, la trimetilamina apareció en una sola y el dimetilsulfuro en dos `[R11]`.
- **Variabilidad:** el perfil cambia mucho entre marcas. El dimetilsulfuro apareció solo en dos de las cuatro, y los aldehídos de Strecker (2- y 3-metilbutanal) fueron muy abundantes en una sola; las otras dos estuvieron dominadas por pirazinas y furanos `[R11]`.

### 3.2 Compuestos

Fuente principal: Trang y Wang (2009), HS-SPME-GC-MS en cuatro salsas comerciales (75 compuestos identificados; dominan alcoholes, furanos, aldehídos y pirazinas) `[R11]`. Las áreas de pico son relativas y no equivalen a concentración. La columna "detección" indica en cuántas de las 4 marcas apareció.

| Compuesto | Detección | Descriptor | Confianza |
| :--- | :---: | :--- | :---: |
| `methylpyrazine` | 4/4 | Tostado, fruto seco | Alta |
| `2_5_dimethylpyrazine` | 4/4 | Tostado, cacao | Alta  |
| `furfural` | 2/4 | Pan tostado | Media-Alta |
| `acetic_acid` | 3/4 | Acidez | Media-Alta |
| `dimethyl_sulfide` | 2/4 | Marino, repollo dulce | Media |
| `dimethyl_disulfide` | 2/4 | Azufrado | Media  |
| `2_methylbutanal`, `3_methylbutanal` | 3/4 y 2/4 | Malta, Strecker | Media-Alta  |
| `methional` (3-(metiltio)propanal) | 1/4 | Papa cocida, caldo | Baja-Media |
| `trimethylamine` | 1/4 | Pescado | Baja |
| `thiophene` | 2/4 (trazas) | Azufrado | Baja |
| `maltol` | **0/4** | Caramelo | **No verificado** |

`maltol` no fue detectado en ninguna de las cuatro marcas. Esa ausencia **no prueba** que falte: la HS-SPME a 60 °C captura mal los compuestos polares como el maltol, y el producto lleva colorante caramelo. Se mantiene como hipótesis de bajo peso hasta contar con otra fuente. `trimethylamine` y `methional` bajan de confianza por aparecer en una sola marca. Se agregan las pirazinas y los aldehídos de Strecker, que son los dominantes en los datos.

Existen además estudios de volátiles en jugo e hidrolizados de ostra (más de 600 compuestos por HS-SPME-GC-MS en jugo enzimático) `[R13]`, pero describen la **materia prima**, no la salsa terminada.

### 3.3 Conectividad esperable

Pirazinas y aldehídos de Strecker explican el vínculo con carnes salteadas y soja/miso/shiitake. Los marcadores marinos (`dimethyl_sulfide`, `trimethylamine`) justifican el vínculo con mariscos, pero con **peso menor** que en el original.

---

## 4. Proteína de Soja Texturizada (PST)

### 4.1 Matriz y cinética

Extrusión de harina desgrasada de soja a alta temperatura, presión y cizallamiento. La nota "a poroto" (*beany*) proviene sobre todo de la oxidación de lípidos residuales; Maillard y Strecker aportan además compuestos tostados `[R10][R16]`.

- **Dato importante:** en PST el comportamiento de los volátiles es **irregular**. Un trabajo reciente con GC-MS/GC-O en productos de soja (55 volátiles en harina; 18 activos olfativamente) encontró que la PST extrudida mostraba niveles que subían y bajaban sin un patrón claro frente a harina, aislado y concentrado `[R17]`. En otros sistemas extrudidos, la extrusión reduce mucho el hexanal (un polvo de poroto comercial tenía unas 20 veces más hexanal que la muestra extrudida) `[R18]`. Por eso **no conviene asumir** que la PST es más rica en hexanal que otras formas de soja.
- Los volátiles quedan retenidos por interacción con la proteína y la matriz porosa `[R16]`.

### 4.2 Compuestos

| Compuesto | Descriptor | Confianza | Nota |
| :--- | :--- | :---: | :--- |
| `hexanal` | Verde, poroto | Alta | Marcador clásico de *beany* `[R10][R16][R19]`. |
| `2_pentylfuran` | Poroto, verde | Alta | Odorante principal en soja `[R10][R19]`. |
| `1_octen_3_ol` | Hongo, terroso | Media | Muy citado en soja y leguminosas; en el trabajo de GC-O la especie relevante fue la cetona `1_octen_3_one` `[R10]`. Considerar agregar la cetona. |
| `methional` | Caldo, papa cocida | Media | Ruta de Strecker plausible; en soja se reportan además `methanethiol` y `dimethyl_trisulfide` como odorantes azufrados `[R10]`. |
| `methylpyrazine` | Cereal tostado | Media | Maillard en extrusión. |
| `nonanal` | Graso, ceroso | Media | Oxidación de oleico residual. |
| `benzaldehyde` | Almendra amarga | Media-Baja | No lo confirmé en las fuentes revisadas. |

### 4.3 Conectividad esperable

Legumbres y derivados de soja (`tofu`, `soy_sauce`, `tempeh`, `edamame`) vía `hexanal` y `2_pentylfuran`; hongos vía `1_octen_3_ol`; bases cárnicas y sofritos vía `methional`, `methylpyrazine` y `nonanal`.

---

## 5. Referencias

### Verificadas durante esta revisión (leí el resumen o el texto)

- `[R1]` Mottram, D. S. (1998). *Flavour formation in meat and meat products: a review.* Food Chemistry, 62(4), 415-424.
- `[R2]` *Volatile organic compounds in beef and pork by gas chromatography-mass spectrometry: A review.* https://research.ucc.ie/en/publications/volatile-organic-compounds-in-beef-and-pork-by-gas-chromatography/
- `[R3]` *Formation and Analysis of Volatile and Odor Compounds in Meat: A Review.* Molecules 2022, 27, 6703. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9572956/
- `[R4]` *Identification of Characteristic Aroma-active Compounds from Burnt Beef Reaction Flavor Manufactured by Extrusion.* https://koreascience.kr/article/JAKO200603042165938.do
- `[R5]` Ueda, S. et al. (2022). *Production of Hydroxy Fatty Acids, Precursors of γ-Hexalactone, Contributes to the Characteristic Sweet Aroma of Beef.* Metabolites. https://pmc.ncbi.nlm.nih.gov/articles/PMC9028887
- `[R6]` Estudio de lactonas características en Japanese Black (GC-O, dilución isotópica). https://pmc.ncbi.nlm.nih.gov/articles/PMC8067244
- `[R7]` Estudio de odorantes del aroma Wagyu (γ-hexalactona, γ-decalactona, γ-undecalactona). Metabolites 2021, 11(1), 56. https://www.mdpi.com/2218-1989/11/1/56/html
- `[R8]` Patentes de aromas de dulce de leche (maltol, furaneol, furfural, HMF). US 7229657 / US 8137726, *Dulce de leche-flavored fat-based confection…*
- `[R9]` Gaze, L. V. et al. (2015). *Dulce de Leche, a typical product of Latin America: Characterisation by physicochemical, optical and instrumental methods.* (Revista a confirmar.) https://agris.fao.org/search/en/records/65de2a3eb766d82b18fc72c4. Sobre lisina y HMF: Malec, L. S. et al. (2005), *Loss of available lysine during processing of different dulce de leche formulations*, Int. J. Dairy Technol. 58, 164-168; y el trabajo sobre HMF como indicador térmico en dulce de leche, J. Dairy Res.
- `[R10]` Patente US 6426112, *Soy products having improved odor and flavor…* (odorantes del *beany*: hexanal, 1-octen-3-ona, 2-pentilpiridina, metanotiol, DMTS).
- `[R11]` Trang, N. H. D. y Wang, X. C. (2009). *Solid-phase micro-extraction combined with gas chromatography-mass spectrometry to determine volatile compounds in oyster sauce.* Asian J. Food Agro-Ind. 2(02), 189-202. https://thaiscience.info/Journals/Article/AFAI/10850128.pdf
- `[R12]` Tesis sobre compuestos volatilizados de carne vacuna cocida en agua o grasa (mercaptanos y carbonilos). https://d.lib.msu.edu/etd/12690/OBJ/download
- `[R13]` *Flavor improvement of enzymatic oyster juice by sequential heating…* https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13423985/
- `[R14]` Lexikon der Ernährung (Spektrum), *4-Vinylguajacol* (aroma clave del café).
- `[R15]` Fichas de 4-vinilguayacol (decarboxilación del ácido ferúlico; cerveza de trigo, vino, humo de madera). https://ymdb.ca/compounds/YMDB01624
- `[R16]` Deng, Z. et al. (2025). *Research Progress on Formation and Removal of Beany Flavor in Soy Protein-based Meat Alternatives.* https://www.spgykj.com/en/article/doi/10.13386/j.issn1002-0306.2025030102
- `[R17]` Chromatography Online (16/07/2026), *GC-MS and GC-O Tracks Soybean Off-Flavor Compounds.* https://www.chromatographyonline.com/view/gc-ms-gc-o-tracks-soybean-off-flavor-compounds
- `[R18]` Szczygiel, E. (2016). *Aroma chemistry and consumer acceptance of navy bean powder as prepared by commercial or extrusion processing.* Tesis, Michigan State University.
- `[R19]` Tesis sobre el perfil volátil de haba (*faba bean*) antes y después de extrusión de alta humedad (hexanal, 1-hexanol, 2-pentilfurano como compuestos de *beany*). https://helda.helsinki.fi/

### Citadas de memoria, **a confirmar antes de usar**

- Yamaguchi, S. (1967). The synergistic effect of monosodium glutamate and disodium 5'-ribonucleotides on taste intensity. *J. Food Sci.* 32, 473-478. (Origen del dato de sinergia glutamato-nucleótidos; la cifra "hasta 8×" varía según la fuente.)
- Hirai, Herz, Pokorny y Chang (1973), volátiles de carne vacuna hervida; y Gasser y Grosch (1988), compuestos con altos valores de aroma en carne vacuna cocida. Ambos aparecen en listas de referencias de trabajos que revisé, pero no leí su contenido.

### Identificadores de bases de datos

- **FooDB `FDB014418`** corresponde a *Corosin*, un triterpenoide de *Corchorus olitorius*. **No** es proteína de soja texturizada. La cita original era incorrecta y se eliminó.
- **FooDB `FOOD00780`** no pude verificarlo (el sitio bloqueó la consulta). Se eliminó hasta poder confirmarlo manualmente.

---
