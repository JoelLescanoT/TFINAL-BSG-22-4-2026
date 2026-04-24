import vertexai
from vertexai.generative_models import GenerativeModel

print("Iniciando test...")

PROJECT_ID = "plazos-despacho-fiscal"
LOCATION = "us-central1"

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("Inicialización OK")

    model = GenerativeModel("gemini-2.5-flash")

    print("Modelo cargado")

    response = model.generate_content("Responde solo OK")

    print("Vertex AI FUNCIONANDO")
    print("Respuesta:", response.text)

except Exception as e:
    print("Vertex AI NO FUNCIONA")
    print("Error:", e)