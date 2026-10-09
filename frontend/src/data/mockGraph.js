/**
 * Mock Data para el Spike de Renderizado del Grafo de Sabores 2D.
 * Representa un subgrafo representativo de ingredientes clave y sus relaciones
 * con scores y categorías según la taxonomía oficial de Mapa de Sabores.
 */

export const MOCK_GRAPH_DATA = {
  nodes: [
    { id: 1, name: "Tomate", category: "Verduras", color: "#2A9D8F", val: 14 },
    { id: 2, name: "Albahaca", category: "Hierbas", color: "#457B9D", val: 12 },
    { id: 3, name: "Ajo", category: "Alliums", color: "#C0392B", val: 15 },
    { id: 4, name: "Queso Parmesano", category: "Lácteos", color: "#F1C40F", val: 13 },
    { id: 5, name: "Aceite de Oliva", category: "Aceites", color: "#DAA520", val: 11 },
    { id: 6, name: "Carne Vacuna", category: "Carnes", color: "#E74C3C", val: 16 },
    { id: 7, name: "Panceta", category: "Carnes", color: "#E74C3C", val: 13 },
    { id: 8, name: "Manzana", category: "Frutas", color: "#E63946", val: 12 },
    { id: 9, name: "Canela", category: "Especias", color: "#E67E22", val: 10 },
    { id: 10, name: "Limón", category: "Cítricos", color: "#F9A825", val: 14 },
    { id: 11, name: "Salmón", category: "Pescados", color: "#3498DB", val: 13 },
    { id: 12, name: "Eneldo", category: "Hierbas", color: "#457B9D", val: 9 },
    { id: 13, name: "Café", category: "Fermentados", color: "#8E44AD", val: 11 },
    { id: 14, name: "Chocolate", category: "Fermentados", color: "#8E44AD", val: 13 },
    { id: 15, name: "Nuez", category: "Frutos Secos", color: "#A0522D", val: 10 },
    { id: 16, name: "Hongo Shiitake", category: "Hongos", color: "#7F8C8D", val: 11 },
    { id: 17, name: "Salsa de Soja", category: "Fermentados", color: "#8E44AD", val: 12 },
    { id: 18, name: "Jengibre", category: "Especias", color: "#E67E22", val: 11 },
    { id: 19, name: "Queso Azul", category: "Lácteos", color: "#F1C40F", val: 12 },
    { id: 20, name: "Pera", category: "Frutas", color: "#E63946", val: 10 },
    { id: 21, name: "Dulce de Leche", category: "Endulzantes", color: "#FFB6C1", val: 10 },
    { id: 22, name: "Pescado Blanco", category: "Pescados", color: "#3498DB", val: 11 }
  ],
  links: [
    // Alta afinidad (> 0.75: verde)
    { source: 1, target: 2, affinity_score: 0.94, rationale: "Tomate y Albahaca comparten linalool y geraniol." },
    { source: 1, target: 3, affinity_score: 0.88, rationale: "Armonía aromática y sulfurosa mediterránea clásica." },
    { source: 2, target: 5, affinity_score: 0.82, rationale: "Extracción y dispersión lipofílica de terpenos." },
    { source: 4, target: 1, affinity_score: 0.91, rationale: "Sinergia de glutamato libre y ácido cítrico/málico." },
    { source: 6, target: 7, affinity_score: 0.85, rationale: "Puente aromático cárnico de pirazinas y tiofenos." },
    { source: 8, target: 9, affinity_score: 0.89, rationale: "Cinamaldehído y ésteres frutales complementarios." },
    { source: 11, target: 10, affinity_score: 0.86, rationale: "El citral y limoneno realzan los lípidos marinos." },
    { source: 11, target: 12, affinity_score: 0.84, rationale: "Carvona y terpenos que armonizan con notas marinas." },
    { source: 13, target: 14, affinity_score: 0.95, rationale: "Núcleo idéntico de pirazinas tostadas y vainillina." },
    { source: 14, target: 15, affinity_score: 0.79, rationale: "Afinidad de pirazinas y notas grasas amaderadas." },
    { source: 16, target: 17, affinity_score: 0.92, rationale: "Bomba de umami (1-octen-3-ol + fermentos de soja)." },
    { source: 17, target: 18, affinity_score: 0.81, rationale: "Zingerona y metilpirazinas en balance dulce-salado." },
    { source: 19, target: 20, affinity_score: 0.82, rationale: "Contraste de acidez/salado con azúcar y ésteres frutales." },

    // Afinidad moderada (0.45 - 0.75: amarillo)
    { source: 6, target: 16, affinity_score: 0.68, rationale: "Puente terroso de hongos potencian el sabor a carne." },
    { source: 6, target: 3, affinity_score: 0.72, rationale: "Compuestos azufrados y pirazinas doradas al fuego." },
    { source: 10, target: 8, affinity_score: 0.58, rationale: "Realce ácido de notas frutales y malic acid." },
    { source: 4, target: 15, affinity_score: 0.62, rationale: "Lactonas y notas a nuez madura compartidas." },
    { source: 3, target: 18, affinity_score: 0.65, rationale: "Base aromática asiática picante y sulfurada." },

    // Discordantes / antagónicos (< 0.45: rojo punteado)
    { source: 21, target: 22, affinity_score: 0.12, rationale: "Contraste disonante extremo entre lácteo dulce y pescado." },
    { source: 14, target: 22, affinity_score: 0.18, rationale: "Grasas marinas incompatibles con amargor de cacao." },
    { source: 1, target: 21, affinity_score: 0.22, rationale: "Acidez y umami chocan con caramelo lácteo denso." }
  ]
};
