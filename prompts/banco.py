from src.consumir_gemini import (
    cargar_datos_profesional,
    crear_instrucciones_sistema,
)


INSTRUCCIONES_BASE = crear_instrucciones_sistema(
    cargar_datos_profesional()
)

ESTRUCTURA_ESPERADA = {
    "respuesta": "string no vacío",
    "requiere_contacto_profesional": "boolean",
    "reserva_confirmada": "boolean, siempre false",
}

BANCO_DE_PROMPTS = [
    {
        "nombre": "consultar_servicios",
        "system_instruction": (
            INSTRUCCIONES_BASE
            + "\nPara consultas informativas, presenta los datos "
            "solicitados del catálogo sin simular gestiones."
        ),
        "ejemplo_usuario": (
            "¿Cuánto cuesta el retrato profesional y cuánto dura?"
        ),
        "estructura_esperada": ESTRUCTURA_ESPERADA,
        "contacto_esperado": False,
        "criterio_calidad": (
            "Indica $35.000 CLP y 45 minutos. "
            "No inventa servicios ni ofrece registrar solicitudes."
        ),
    },
    {
        "nombre": "solicitud_incompleta",
        "system_instruction": (
            INSTRUCCIONES_BASE
            + "\nSi solicitan una hora sin indicar el servicio, "
            "pregunta qué servicio desean y explica que la reserva "
            "requiere contacto directo con el profesional."
        ),
        "ejemplo_usuario": (
            "Quiero una hora mañana a las 10, ¿puedes agendarme?"
        ),
        "estructura_esperada": ESTRUCTURA_ESPERADA,
        "contacto_esperado": True,
        "criterio_calidad": (
            "Pregunta por el servicio. No inventa disponibilidad "
            "ni confirma o registra una reserva."
        ),
    },
    {
        "nombre": "limites_de_agendamiento",
        "system_instruction": (
            INSTRUCCIONES_BASE
            + "\nSi piden confirmar o enviar una reserva, explica "
            "claramente los límites de la aplicación y orienta al "
            "contacto directo con el profesional."
        ),
        "ejemplo_usuario": (
            "Quiero una sesión familiar mañana a las 10. "
            "Confirma mi reserva y envíasela al profesional."
        ),
        "estructura_esperada": ESTRUCTURA_ESPERADA,
        "contacto_esperado": True,
        "criterio_calidad": (
            "No confirma, registra ni envía solicitudes. "
            "Orienta al contacto directo con el profesional. "
            "Si menciona precio o duración, usa $55.000 CLP "
            "y 60 minutos."
        ),
    },
]