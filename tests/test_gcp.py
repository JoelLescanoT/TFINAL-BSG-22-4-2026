from google.cloud import storage
import os

def test_upload():
    # Cliente GCP
    client = storage.Client()

    bucket_name = "plazos-despacho-fiscal-bronze"
    bucket = client.bucket(bucket_name)

    # Ruta relativa correcta (sube un nivel desde /tests)
    source_file = os.path.join("..", "data", "raw", "test.txt")

    destination_blob = "test/test.txt"

    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(source_file)

    print("Archivo subido correctamente 🚀")


if __name__ == "__main__":
    test_upload()