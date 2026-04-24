import vertexai
from vertexai.generative_models import GenerativeModel

from dotenv import load_dotenv
import os
from google.oauth2 import service_account

# cargar .env
load_dotenv()

# verificar
print("CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# crear credenciales explícitas
credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

# inicializar Vertex AI
vertexai.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_LOCATION"),
    credentials=credentials
)

# modelo (ajústalo si falla)
model = GenerativeModel("gemini-1.5-flash-001")

# prueba
response = model.generate_content("Hola, responde OK")

print(response.text)