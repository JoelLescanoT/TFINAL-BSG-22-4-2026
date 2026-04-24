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

model = GenerativeModel("gemini-1.5-flash")


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

    # descargar temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        blob.download_to_filename(tmp.name)

        text = ""

        try:
            with pdfplumber.open(tmp.name) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"⚠️ Error leyendo PDF: {e}")

    return text[:15000]  # límite seguro para Gemini


# ======================
# GEMINI
# ======================
def call_gemini(text):

    prompt = f"""
Eres un asistente legal experto en fiscalía.

Analiza el documento y devuelve SOLO un JSON válido con esta estructura:

{{
    "plazo_dias": number,
    "es_prorroga": boolean,
    "dias_prorroga": number,
    "fiscal": string,
    "delito": string
}}

Reglas:
- Si no encuentras un campo → null
- No expliques nada
- Solo devuelve JSON limpio

DOCUMENTO:
{text}
"""

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except Exception:
        print("⚠️ Gemini devolvió texto no JSON")
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