"""Matriz de Incompatibilidad Conocida (~50 pares antagónicos culinarios).

Utilizada como regla de validación estricta y filtro de seguridad en el pipeline
de generación para detectar alucinaciones del LLM y derivar a la cola de curación.
(SPEC.md Sección 2.1.2 y 2.2).
"""

ANTAGONISTIC_PAIRS: set[tuple[str, str]] = {
    # Pescados / Mariscos con lácteos pesados o dulces
    ("Pescado Blanco", "Dulce de Leche"),
    ("Atún", "Chocolate"),
    ("Salmón", "Vainilla"),
    ("Merluza", "Miel"),
    ("Camarones", "Nutella"),
    ("Pulpo", "Caramelo"),
    ("Sardinas", "Frutilla"),
    ("Anchoas", "Plátano"),
    ("Bacalao", "Chocolate Blanco"),
    ("Mejillones", "Canela"),
    # Carnes rojas con sabores incompatibles
    ("Carne Vacuna", "Menta Piperita"),
    ("Cordero", "Malvaviscos"),
    ("Cerdo", "Goma de Mascar"),
    ("Hígado", "Algodón de Azúcar"),
    ("Morcilla", "Helado de Frutilla"),
    ("Chorizo", "Crema Pastelera"),
    # Cítricos / Ácidos extremos con lácteos fermentados
    ("Limón", "Queso Roquefort"),
    ("Pomelo", "Leche Condensada"),
    ("Vinagre", "Leche Tibia"),
    # Frutas frescas con ingredientes sulfurosos o pungentes
    ("Sandía", "Ajo"),
    ("Melón", "Cebolla Cruda"),
    ("Uvas", "Cebolla de Verdeo"),
    ("Banana", "Pescado Frito"),
    ("Manzana", "Mostaza de Dijón Fuerte"),
    ("Naranja", "Wasabi"),
    ("Pera", "Comino Concentrado"),
    ("Kiwi", "Morcilla"),
    ("Durazno", "Hígado de Pollo"),
    ("Ciruela", "Ajo Negro"),
    # Dulces tradicionales con condimentos o grasas disonantes
    ("Chocolate Amargo", "Sopa de Pescado"),
    ("Vainilla", "Grasa de Cerdo"),
    ("Miel", "Sardinas en Aceite"),
    ("Dulce de Batata", "Pimienta de Cayena Pura"),
    ("Flan", "Pesto Genovés"),
    ("Tiramisú", "Chucrut"),
    ("Helado de Vainilla", "Chorizo Colorado"),
    ("Merengue", "Vinagre Balsámico Puro"),
    # Especias y hierbas en combinaciones agresivas
    ("Orégano", "Algodón de Azúcar"),
    ("Romero", "Frutillas con Crema"),
    ("Clavo de Olor", "Sandía Fresca"),
    ("Comino", "Helado de Menta"),
    ("Canela", "Atún al Natural"),
    ("Nuez Moscada", "Sushi de Salmón"),
    # Verduras y legumbres con repostería
    ("Brócoli", "Crema Chantilly"),
    ("Coliflor", "Mermelada de Damasco"),
    ("Espinaca", "Dulce de Membrillo"),
    ("Berenjena", "Azúcar Impalpable"),
    ("Pepino", "Chocolate Caliente"),
    ("Lentejas", "Helado de Frutilla"),
    ("Garbanzos", "Crema Pastelera"),
}


def is_antagonistic(ingredient_a: str, ingredient_b: str) -> bool:
    """Verifica de forma insensible a mayúsculas si el par está en la matriz de antagónicos."""
    a, b = ingredient_a.strip().lower(), ingredient_b.strip().lower()
    for ant_a, ant_b in ANTAGONISTIC_PAIRS:
        norm_a, norm_b = ant_a.strip().lower(), ant_b.strip().lower()
        if (a == norm_a and b == norm_b) or (a == norm_b and b == norm_a):
            return True
    return False
