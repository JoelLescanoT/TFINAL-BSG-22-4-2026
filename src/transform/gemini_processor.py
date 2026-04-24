import os
import json
import google.generativeai as genai

# =========================
# CONFIG
# =========================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

genai.configure()  # usa credenciales automáticamente

MODEL = "gemini-2.5-flash"


# =========================
# PROMPT INTELIGENTE
# =========================

def build_prompt(texto):
    return f"""
Eres un asistente legal experto en fiscalía.

Analiza el siguiente documento y extrae la información en formato JSON:

Campos requeridos:
- tipo_documento
- plazo_dias
- es_prorroga (true/false)
- dias_prorroga
- delito
- fiscal
- parte_investigada

Reglas:
- Responde SOLO en JSON válido
- Si no encuentras un campo, usa null
- No inventes información

DOCUMENTO:
{texto[:15000]}
"""


# =========================
# PROCESAMIENTO
# =========================

def procesar_texto_con_gemini(texto):

    model = genai.GenerativeModel(MODEL)

    prompt = build_prompt(texto)

    response = model.generate_content(prompt)

    try:
        text = response.text.strip()

        # limpiar posible markdown ```json
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)
        return data

    except Exception as e:
        print("❌ Error parseando JSON Gemini:", e)
        return {}


# =========================
# RUN
# =========================

def run(bronze_data):

    print("\n🤖 PROCESANDO CON GEMINI...")

    resultados = []

    for item in bronze_data:

        try:
            texto = item.get("texto", "")

            if not texto:
                resultados.append({**item, "ia": {}})
                continue

            ia_data = procesar_texto_con_gemini(texto)

            resultados.append({
                **item,
                "ia": ia_data
            })

        except Exception as e:
            print(f"❌ Error Gemini: {e}")

    print(f"✅ Procesados con IA: {len(resultados)}")

    return resultados