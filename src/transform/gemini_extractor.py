import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

_model = None


def get_model():
    global _model

    if _model is None:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _model = GenerativeModel("gemini-1.5-flash")

    return _model


def build_prompt(texto):
    return f"""
Extrae información legal del siguiente documento.

Devuelve SOLO JSON válido con esta estructura:

{{
  "case_id": "",
  "fiscal": "",
  "delito": "",
  "plazo_dias": 0,
  "tipo_investigacion": ""
}}

Reglas:
- plazo_dias debe ser número
- si no encuentras algo, deja vacío

DOCUMENTO:
\"\"\"
{texto[:12000]}
\"\"\"
"""


def extract_with_gemini(texto):

    model = get_model()
    prompt = build_prompt(texto)

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)

    except Exception as e:
        return {
            "error": str(e),
            "raw": getattr(response, "text", "")
        }