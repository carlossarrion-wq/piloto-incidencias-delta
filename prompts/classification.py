"""
Prompts para clasificación de incidencias
"""

CLASSIFICATION_SYSTEM_PROMPT = """Eres un experto en análisis de incidencias técnicas de sistemas IT.
Tu tarea es analizar incidencias y determinar su causa raíz basándote en el resumen y las notas proporcionadas.

Debes ser preciso, técnico y proporcionar razonamientos claros basados en patrones conocidos de fallos en sistemas IT."""

CLASSIFICATION_PROMPT = """Analiza la siguiente incidencia y determina su causa raíz más probable:

**Ticket ID:** {ticket_id}
**Resumen:** {resumen}
**Notas:** {notas}
**Fecha de Creación:** {fecha_creacion}

Basándote en la información proporcionada, identifica:

1. **Causa Raíz Principal**: La causa más probable del problema
2. **Nivel de Confianza**: Tu nivel de confianza en esta clasificación (0.0 a 1.0)
3. **Razonamiento**: Explicación técnica detallada de por qué identificaste esta causa
4. **Keywords Detectadas**: Palabras clave técnicas relevantes encontradas en la descripción
5. **Causas Alternativas**: Otras posibles causas ordenadas por probabilidad (máximo 3)

**Categorías de Causas Raíz Comunes:**
- Error de Configuración
- Problema de Red/Conectividad
- Fallo de Hardware
- Error de Software/Bug
- Problema de Rendimiento
- Error de Usuario
- Problema de Seguridad
- Fallo de Integración
- Problema de Datos/Base de Datos
- Timeout/Latencia
- Problema de Memoria/Recursos
- Error de Despliegue
- Otro (especificar)

Responde en formato JSON con la siguiente estructura:
{{
    "causa_raiz_predicha": "nombre de la causa",
    "confianza": 0.85,
    "razonamiento": "explicación detallada...",
    "keywords_detectadas": ["keyword1", "keyword2", "keyword3"],
    "causas_alternativas": [
        {{"causa": "causa alternativa 1", "probabilidad": 0.10}},
        {{"causa": "causa alternativa 2", "probabilidad": 0.05}}
    ]
}}

Sé específico y técnico en tu análisis."""
