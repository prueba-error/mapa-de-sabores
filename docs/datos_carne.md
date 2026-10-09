# Taxonomía Fisicoquímica de Cortes Vacunos: Justificación Teórica y Origen de Datos

---

## 1. Fundamento Biomecánico y Cinético de la Diferenciación

En la ciencia de los alimentos, el flavor cárnico no es estático ni uniforme: depende de la interacción entre tres matrices precursoras primarias:

1. **Aminoácidos libres y azúcares reductores** en la fase acuosa sarcoplasmática (reactivos hidrosolubles de Maillard).
2. **Lípidos intramusculares e intermusculares** (triglicéridos y fosfolípidos de membrana propensos a termodegradación oxidativa).
3. **Fracción proteica estructural y conectiva** (proporción de colágeno perimisial/epimisial y mioglobina sarcoplasmática).

El método de cocción actúa como el selector cinético fundamental: el calor seco a alta temperatura ($>140\,^\circ\text{C}$) activa la pirólisis y la condensación de Maillard en superficie; el calor húmedo prolongado ($80-95\,^\circ\text{C}$) hidroliza el colágeno a gelatina y promueve degradaciones hidrotérmicas de aminoácidos azufrados.

---

## 2. Desglose Teórico y Origen de Datos por Perfil

### A. Corte Vacuno Magro / Steak (`beef_lean_steak`)

- **Matriz anatómica representativa:** Lomo (_psoas major_), Cuadril (_gluteus medius_), Nalga (_semimembranosus_).
- **Parámetros fisicoquímicos:**
  - Grasa intramuscular baja ($\le 3-5\%$).
  - Alta proporción de mioglobina y hierro hémico libre.
  - Colágeno bajo o soluble, apto para cocción rápida de calor radiante o conducción directa (`sear`, `grill`).
- **Origen y justificación de los compuestos volátiles (GC-MS):**
  - **`methylpyrazine` y `acetylpyrazine`:** Formados por reacción de Maillard superficial (degradación de Strecker entre dicarbonilos y aminoácidos libres). Proveen la nota tostada a costra crocante sellada.
  - **`methional`:** Formado por degradación de Strecker específica de la L-metionina. Aporta el descriptor central de "carne cocida" (_cooked meat / potato-like_).
  - **`thiophene`:** Derivado heterocíclico azufrado originado de la interacción de cisteína y azúcares a alta temperatura; clave en el aroma umami cárnico.
  - **`guaiacol` y `4vg` (4-vinilguayacol):** Fenoles volátiles derivados de la pirólisis térmica proteico-lipídica y componentes de humo en parrilla; responsables del fondo ahumado y rostizado.
  - **`hexanal`:** Presente en niveles basales controlados proveniente de la termoxidación mínima de fosfolípidos de membrana celular.

---

### B. Corte Vacuno Graso (`beef_fatty_cut`)

- **Matriz anatómica representativa:** Asado de tira / Costillar, Vacío, Ojo de bife (_longissimus thoracis_ con marmoleo), Entraña.
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

### C. Corte Vacuno Rico en Colágeno / Estofado (`beef_braised_collagen`)

- **Matriz anatómica representativa:** Roast beef / Aguja, Osobuco / Garrón (_extensor carpi radialis_), Tapa de asado.
- **Parámetros fisicoquímicos:**
  - Alto contenido de tejido conectivo (colágeno tipo I y III, $>1.5-2.5\%\, \text{peso húmedo}$).
  - Cocción prolongada en medio acuoso ($>1.5-3\,\text{horas}$). Al superarse los $65-70\,^\circ\text{C}$ de manera sostenida, las hélices triples de tropocolágeno se desnaturalizan e hidrolizan irreversiblemente en cadenas de gelatina soluble.
- **Origen y justificación de los compuestos volátiles (GC-MS):**
  - **`dimethyl_sulfide` (DMS) y `dimethyl_trisulfide` (DMTS):** Sulfuros volátiles hidrosolubles de umbral olfativo ultra-bajo, originados por la degradación hidrotérmica continua de aminoácidos azufrados (metionina y cisteína). Son los marcadores indiscutibles de caldos concentrados, estofados y carne cocida por hervor.
  - **`methional`:** Dominante en medio acuoso; aroma terroso y a carne de olla.
  - **`thiophene`:** Se conserva como marcador umami cárnico termoestable.
  - **Atenuación de fenoles y pirazinas superiores:** Al no alcanzarse temperaturas de pirólisis superficial ($>140\,^\circ\text{C}$) debido a la presencia de agua líquida ($T \approx 100\,^\circ\text{C}$ máx.), los compuestos de costra sellada (`guaiacol`, `acetylpyrazine`) decrecen significativamente o son reemplazados por el perfil azufrado-aldehídico de cocción lenta.

---

## 3. Conexiones Resultantes en el Grafo de Sabores

- **`beef_fatty_cut`** adquiere aristas directas con matrices oleosas y lácteas maduras (`butter`, `ghee`, `cheddar`, `avocado`) debido a la tríada lipídica `octanal` + `nonanal` + `gamma_decalactone`.
- **`beef_lean_steak`** enlaza con especias y productos de tueste alto (`coffee`, `black_pepper`, `tofu`, `sesame_oil`) gracias a las pirazinas y fenoles de sellado (`4vg`, `guaiacol`, `acetylpyrazine`).
- **`beef_braised_collagen`** comparte vecindad topológica con alliums cocidos, caldos y hongos (`onion`, `garlic`, `shiitake`, `beef_stock`, `dashi`) por la saturación de puentes disulfuro y sulfuros volátiles (`dimethyl_sulfide`, `dimethyl_trisulfide`, `methional`).
