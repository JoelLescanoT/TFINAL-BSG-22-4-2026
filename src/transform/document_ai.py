'''
import os
from google.cloud import documentai

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")  # ejemplo: "us" o "eu"
PROCESSOR_ID = os.getenv("DOCAI_PROCESSOR_ID")  # 👈 tu processor


def get_client():
    return documentai.DocumentProcessorServiceClient()


def build_name():
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"


def process_document(gcs_uri):
    """
    Procesa un documento desde GCS usando Document AI
    """
    client = get_client()
    name = build_name()

    input_config = documentai.ProcessRequest(
        name=name,
        raw_document=None,
        inline_document=None,
        gcs_document=documentai.GcsDocument(
            gcs_uri=gcs_uri,
            mime_type="application/pdf"
        )
    )

    result = client.process_document(request=input_config)

    return result.document


def extract_entities(document):
    """
    Convierte entidades de Document AI en dict
    """
    data = {}

    for entity in document.entities:
        key = entity.type_
        value = entity.mention_text

        data[key] = value

    return data


def run(bronze_data):
    """
    bronze_data:
    [
        {
            "case_id": "1-2026",
            "gcs_path": "gs://..."
        }
    ]
    """
    print("\n🤖 PROCESANDO DOCUMENT AI...")

    results = []

    for item in bronze_data:
        try:
            doc = process_document(item["gcs_path"])
            entities = extract_entities(doc)

            results.append({
                "case_id": item["case_id"],
                "entities": entities,
                "text": doc.text  # 🔥 clave para reglas
            })

        except Exception as e:
            print(f"❌ Error con {item['gcs_path']}: {e}")

    print(f"✅ Documentos procesados: {len(results)}")

    return results
'''
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
import os


# =========================
# CONFIG
# =========================

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us")


# =========================
# CORE: PROCESAR DOCUMENTO
# =========================

def process_document(gcs_uri, processor_id):
    """
    Procesa un documento desde GCS usando Document AI
    """

    # Cliente Document AI
    docai_client = documentai.DocumentProcessorServiceClient()

    # Nombre del processor
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{processor_id}"

    # =========================
    # DESCARGAR DESDE GCS
    # =========================

    storage_client = storage.Client()

    bucket_name = gcs_uri.split("/")[2]
    blob_path = "/".join(gcs_uri.split("/")[3:])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    content = blob.download_as_bytes()

    # =========================
    # REQUEST CORRECTO
    # =========================

    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(
            content=content,
            mime_type="application/pdf"
        )
    )

    result = docai_client.process_document(request=request)

    return result.document


# =========================
# CLASIFICACIÓN
# =========================

def classify_document(gcs_uri, processor_id):
    """
    Usa el classifier para determinar tipo de documento
    """

    doc = process_document(gcs_uri, processor_id)

    if doc.entities:
        return doc.entities[0].type_

    return "UNKNOWN"


# =========================
# EXTRACCIÓN
# =========================

def extract_entities(gcs_uri, processor_id):
    """
    Extrae entidades con el Custom Extractor
    """

    doc = process_document(gcs_uri, processor_id)

    data = {}

    for entity in doc.entities:
        data[entity.type_] = entity.mention_text

    return data


# =========================
# PIPELINE
# =========================

def run(bronze_data, classifier_id=None, extractor_id=None):

    print("\n🤖 PROCESANDO DOCUMENT AI...")

    resultados = []

    for item in bronze_data:

        gcs_uri = item["gcs_uri"]

        try:
            doc_type = None
            extracted = {}

            # -------------------------
            # 1. CLASIFICAR
            # -------------------------
            if classifier_id:
                doc_type = classify_document(gcs_uri, classifier_id)

            # -------------------------
            # 2. EXTRAER (solo si aplica)
            # -------------------------
            if extractor_id:
                extracted = extract_entities(gcs_uri, extractor_id)

            resultados.append({
                **item,
                "doc_type": doc_type,
                "extracted": extracted
            })

        except Exception as e:
            print(f"❌ Error Document AI ({gcs_uri}): {e}")

    print(f"✅ Documentos procesados: {len(resultados)}")

    return resultados