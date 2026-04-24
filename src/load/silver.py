from datetime import datetime, timedelta
from src.transform import gemini


# ======================
# PROCESAMIENTO DE CASO
# ======================
def procesar_caso(case_id, items):

    plazo_inicial = 0
    total_prorroga = 0
    fiscal = None
    delito = None

    for item in items:

        ia = item.get("ia", {})

        if not ia:
            continue

        # documento principal
        if not ia.get("es_prorroga"):
            plazo_inicial = ia.get("plazo_dias") or plazo_inicial

        # prórrogas
        if ia.get("es_prorroga"):
            total_prorroga += ia.get("dias_prorroga") or 0

        if not fiscal:
            fiscal = ia.get("fiscal")

        if not delito:
            delito = ia.get("delito")

    plazo_total = plazo_inicial + total_prorroga

    fecha_inicio = datetime.today()
    fecha_vencimiento = fecha_inicio + timedelta(days=plazo_total)

    hoy = datetime.today()

    if hoy > fecha_vencimiento:
        estado = "VENCIDO"
    elif (fecha_vencimiento - hoy).days <= 5:
        estado = "POR_VENCER"
    else:
        estado = "VIGENTE"

    return {
        "case_id": case_id,
        "plazo_inicial": plazo_inicial,
        "total_prorroga": total_prorroga,
        "plazo_total": plazo_total,
        "estado": estado,
        "delito": delito,
        "fiscal": fiscal
    }


# ======================
# SILVER PIPELINE
# ======================
def run(gcs_data):

    print("\n🧠 PROCESANDO SILVER (GEMINI REAL)...")

    documentos = []

    # 1. Procesar cada documento con Gemini
    for item in gcs_data:

        try:
            case_id = item["case_id"]
            gcs_uri = item["gcs_uri"]
            file_name = item["file_name"]

            ia = gemini.process_document(gcs_uri)

            documentos.append({
                "case_id": case_id,
                "file_name": file_name,
                "gcs_uri": gcs_uri,
                "ia": ia
            })

            print(f"✔ Procesado: {file_name}")

        except Exception as e:
            print(f"❌ Error documento: {e}")

    # 2. Agrupar por caso
    casos = {}

    for doc in documentos:
        case_id = doc["case_id"]
        casos.setdefault(case_id, []).append(doc)

    # 3. Procesar casos
    resultados = []

    for case_id, items in casos.items():
        try:
            data = procesar_caso(case_id, items)
            resultados.append(data)
            print(f"✔ Caso procesado: {case_id}")
        except Exception as e:
            print(f"❌ Error en caso {case_id}: {e}")

    print(f"\n✅ Total casos: {len(resultados)}")

    return resultados