import os
import json
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel
import pdfplumber
import tempfile

# ======================
# CONFIG
# ======================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("gemini-2.5-flash")


# ======================
# GCS → PDF → TEXTO
# ======================
def read_pdf_from_gcs(gcs_uri):

    client = storage.Client()

    path = gcs_uri.replace("gs://", "")
    bucket_name = path.split("/")[0]
    blob_path = "/".join(path.split("/")[1:])

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        blob.download_to_filename(tmp.name)

        text = ""

        try:
            with pdfplumber.open(tmp.name) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"⚠️ Error leyendo PDF: {e}")

    return text[:15000]


# ======================
# GEMINI
# ======================
def call_gemini(text):

    prompt = f"""
Eres un asistente legal experto en fiscalía.

Analiza el documento y devuelve SOLO un JSON válido.

IMPORTANTE:
- No escribas texto adicional
- No uses ```json
- No expliques nada

Formato EXACTO:

{{
    "plazo_dias": number,
    "es_prorroga": boolean,
    "dias_prorroga": number,
    "fiscal": string,
    "delito": string
}}

Si no encuentras un campo usa null.

DOCUMENTO:
{text}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    raw_text = response.text.strip()

    # 🔍 DEBUG (te ayuda a ver qué devuelve realmente)
    print("🔎 Respuesta Gemini:", raw_text[:200])

    try:
        return json.loads(raw_text)
    except Exception:
        print("⚠️ Gemini devolvió texto no JSON")

        # 🔥 intento de rescate automático (muy útil)
        try:
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            return json.loads(raw_text[start:end])
        except Exception:
            return {}


# ======================
# INTERFAZ PRINCIPAL
# ======================
def process_document(gcs_uri):

    try:
        text = read_pdf_from_gcs(gcs_uri)

        if not text.strip():
            return {}

        ia = call_gemini(text)

        return ia

    except Exception as e:
        print(f"❌ Error Gemini ({gcs_uri}): {e}")
        return {}