'''
from google.cloud import storage
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_BRONZE")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_gcs_client():
    if not CREDENTIALS_PATH:
        raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS no definido")

    return storage.Client.from_service_account_json(CREDENTIALS_PATH)


def upload_file(client, bucket_name, source_file, destination_blob):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    blob.upload_from_filename(source_file)

    print(f"☁️ Subido: {source_file} → gs://{bucket_name}/{destination_blob}")

    return f"gs://{bucket_name}/{destination_blob}"


def build_destination_path(case_id, file_name):
    today = datetime.now().strftime("%Y-%m-%d")

    return f"bronze/fiscal_cases/case_id={case_id}/date={today}/{file_name}"


def run(casos):
    """
    casos: dict → {case_id: [file_paths]}
    """

    print("📤 Subiendo archivos a GCS (Bronze)...")

    if not BUCKET_NAME:
        raise ValueError("❌ GCS_BUCKET_BRONZE no definido en .env")

    client = get_gcs_client()

    gcs_paths = []

    for case_id, files in casos.items():
        for file_path in files:
            try:
                if not os.path.exists(file_path):
                    print(f"⚠️ No existe: {file_path}")
                    continue

                file_name = os.path.basename(file_path)

                destination = build_destination_path(case_id, file_name)

                gcs_uri = upload_file(
                    client,
                    BUCKET_NAME,
                    file_path,
                    destination
                )

                gcs_paths.append({
                    "case_id": case_id,
                    "file_name": file_name,
                    "gcs_uri": gcs_uri,
                    "upload_date": datetime.now().isoformat(),
                    "layer": "bronze"
                })

            except Exception as e:
                print(f"❌ Error subiendo {file_path}: {e}")

    print(f"✅ Total archivos subidos: {len(gcs_paths)}")

    return gcs_paths
'''


from google.cloud import storage
import os
from datetime import datetime

BUCKET_NAME = os.getenv("GCS_BUCKET_BRONZE")


def upload_file(client, bucket_name, source_file, destination_blob):

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    # 🚀 Evita subir duplicados
    if blob.exists():
        print(f"⚠️ Ya existe, se omite: gs://{bucket_name}/{destination_blob}")
        return f"gs://{bucket_name}/{destination_blob}"

    blob.upload_from_filename(source_file)

    print(f"☁️ Subido: {source_file} → gs://{bucket_name}/{destination_blob}")

    return f"gs://{bucket_name}/{destination_blob}"


def run(casos):

    print("📤 Subiendo archivos a GCS (Bronze)...")

    if not BUCKET_NAME:
        raise ValueError("❌ BUCKET_NAME no está definido en el .env")

    client = storage.Client()

    gcs_paths = []

    today = datetime.today().strftime("%Y-%m-%d")

    for case_id, files in casos.items():

        if not files:
            continue

        for file_path in files:

            try:
                if not os.path.exists(file_path):
                    print(f"❌ No existe archivo: {file_path}")
                    continue

                file_name = os.path.basename(file_path)

                # 🧠 Estructura tipo Data Lake (perfecta para BigQuery luego)
                destination = (
                    f"bronze/fiscal_cases/"
                    f"case_id={case_id}/"
                    f"date={today}/"
                    f"{file_name}"
                )

                gcs_uri = upload_file(
                    client,
                    BUCKET_NAME,
                    file_path,
                    destination
                )

                gcs_paths.append({
                    "case_id": case_id,
                    "file_name": file_name,
                    "gcs_uri": gcs_uri,
                    "load_date": today
                })

            except Exception as e:
                print(f"❌ Error procesando {file_path}: {e}")

    print(f"✅ Total archivos procesados: {len(gcs_paths)}")

    return gcs_paths