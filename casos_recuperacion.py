"""Preguntas y fuentes esperadas para evaluar la recuperación del Bloque 27."""

# Estas referencias se definieron leyendo el corpus, antes de consultar Chroma.
# Cada ruta identifica el único fragmento de ese documento en el índice actual.
CASOS = [
    {
        "id": "01",
        "pregunta": "¿Cuánto sale una sesión de fotos para mi familia?",
        "fuentes_esperadas": ["docs/corpus/sesion-familiar.md"],
    },
    {
        "id": "02",
        "pregunta": "¿La sesión familiar es presencial y cuánto dura?",
        "fuentes_esperadas": ["docs/corpus/sesion-familiar.md"],
    },
    {
        "id": "03",
        "pregunta": "¿Cuánto cuesta un retrato profesional?",
        "fuentes_esperadas": ["docs/corpus/retrato-profesional.md"],
    },
    {
        "id": "04",
        "pregunta": "¿Con cuánto tiempo tengo que avisar si no puedo ir?",
        "fuentes_esperadas": ["docs/corpus/cancelaciones.md"],
    },
    {
        "id": "05",
        "pregunta": "¿Con quién debo gestionar una cancelación?",
        "fuentes_esperadas": ["docs/corpus/cancelaciones.md"],
    },
    {
        "id": "06",
        "pregunta": "¿Cómo se coordina el pago del servicio?",
        "fuentes_esperadas": ["docs/corpus/pagos.md"],
    },
    {
        "id": "07",
        "pregunta": "¿Qué tengo que hacer para que mi hora quede confirmada?",
        "fuentes_esperadas": ["docs/corpus/agendamiento.md"],
    },
    {
        "id": "08",
        "pregunta": "¿Puedes ver si hay disponibilidad el viernes y reservarme una hora?",
        "fuentes_esperadas": ["docs/corpus/agendamiento.md"],
    },
    {
        # Para responder la comparación hacen falta los dos servicios.
        "id": "09",
        "pregunta": "¿Cuál de los dos servicios es más barato y cuánto dura cada uno?",
        "fuentes_esperadas": [
            "docs/corpus/retrato-profesional.md",
            "docs/corpus/sesion-familiar.md",
        ],
    },
    {
        # Lista vacía: el corpus no contiene la dirección.
        # La exhaustividad no aplica y la abstención se comprueba aparte.
        "id": "10",
        "pregunta": "¿Cuál es la dirección exacta del estudio?",
        "fuentes_esperadas": [],
    },
]
