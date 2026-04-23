from dotenv import load_dotenv
import os

load_dotenv()

print("PROJECT:", os.getenv("GCP_PROJECT_ID"))
print("LOCATION:", os.getenv("GCP_LOCATION"))
print("CLASSIFIER:", os.getenv("DOCAI_CLASSIFIER_ID"))
print("EXTRACTOR:", os.getenv("DOCAI_EXTRACTOR_ID"))

from google.auth import default

def run():

    load_dotenv()

    # 🔍 DEBUG CREDENCIALES
    creds, project = default()
    print("👉 Usando credenciales:", getattr(creds, "service_account_email", "USER"))

    print("\n===== INICIO PIPELINE =====\n")