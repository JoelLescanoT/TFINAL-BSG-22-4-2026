'''
import re
from datetime import datetime, timedelta


# =========================
# UTILIDADES GENERALES
# =========================

def leer_pdf(path):
    """
    ⚠️ Placeholder:
    Aquí luego conectas con Document AI o PyMuPDF
    """
    try:
        with open(path, "rb") as f:
            return f.read().decode(errors="ignore")
    except:
        return ""


def extraer_numero_archivo(file_name):
    """
    Ej: 53972-6411-1.pdf → 53972
    """
    try:
        return int(file_name.split("-")[0])
    except:
        return 999999999


# =========================
# 1. IDENTIFICAR DOCUMENTO PRINCIPAL
# =========================

def es_documento_principal(texto):
    texto = texto.upper()

    patrones = [
        "INICIAR INVESTIGACIÓN",
        "APERTURAR INVESTIGACIÓN",
        "DISPOSICION N° UNO",
        "RESOLUCIÓN N° UNO",
        "DISPOSICIÓN DE APERTURA"
    ]

    return any(p in texto for p in patrones)


def obtener_documento_principal(files):

    files_sorted = sorted(files, key=lambda x: extraer_numero_archivo(x))

    for file in files_sorted:
        texto = leer_pdf(file)

        if es_documento_principal(texto):
            return file, texto

    # fallback → el menor código
    file = files_sorted[0]
    return file, leer_pdf(file)


# =========================
# 2. DETECTAR PRÓRROGAS
# =========================

def es_prorroga(texto):
    texto = texto.upper()
    return "PRORROGAR" in texto or "AMPLIAR" in texto


NUMEROS = {
    "QUINCE": 15,
    "TREINTA": 30,
    "CUARENTA": 40,
    "CUARENTA Y CINCO": 45,
    "SESENTA": 60
}


def extraer_dias(texto):

    texto = texto.upper()

    # 1. número directo
    match = re.search(r'(\d+)\s*D[IÍ]AS', texto)
    if match:
        return int(match.group(1))

    # 2. texto
    for palabra, valor in NUMEROS.items():
        if palabra in texto:
            return valor

    return 0


def obtener_prorrogas(files):

    prorrogas = []

    for file in files:
        texto = leer_pdf(file)

        if es_prorroga(texto):
            dias = extraer_dias(texto)

            prorrogas.append({
                "file": file,
                "dias": dias
            })

    return prorrogas


# =========================
# 3. EXTRACCIÓN DOCUMENTO PRINCIPAL
# =========================

def extraer_case_id(texto):
    match = re.search(r'CASO.*?(\d{4,}-\d{4}-\d+-\d+)', texto.upper())
    if match:
        return match.group(1)
    return None


def extraer_fecha(texto):
    # simplificado
    match = re.search(r'(\d{4})', texto)
    if match:
        return f"{match.group(1)}-01-01"
    return None


def extraer_plazo(texto):
    return extraer_dias(texto)


def extraer_tipo_investigacion(texto):

    texto = texto.upper()

    if "PREVENTIVO" in texto:
        return "PREVENCION_FAMILIA"
    elif "TUTELAR" in texto and "PENAL" in texto:
        return "FAMILIA_PENAL_TUTELAR"
    elif "TUTELAR" in texto:
        return "TUTELAR"
    else:
        return "FAMILIA_PENAL_TUTELAR"


def extraer_parte_investigada(texto):

    match = re.search(r'A FAVOR DEL (ADOLESCENTE|NIÑO)\s+([A-Z\s]+)', texto.upper())
    if match:
        return match.group(2).strip()

    match = re.search(r'CONTRA\s+([A-Z\s]+)', texto.upper())
    if match:
        return match.group(1).strip()

    return "NN"


def extraer_delito(texto):

    texto = texto.upper()

    if "VIDA" in texto:
        return "DELITO_VIDA_SALUD", "LESIONES"
    elif "HURTO" in texto:
        return "HURTO_AGRAVADO", "HURTO"
    elif "VIOLACIÓN" in texto:
        return "VIOLACION_SEXUAL", "VIOLACION"
    elif "DESPROTECCIÓN" in texto:
        return "DESPROTECCION_FAMILIAR", "DESPROTECCION"
    elif "CONTRAVENCION" in texto:
        return "CONTRAVENCION", "CONTRAVENCION"

    return "OTROS", "OTROS"


def extraer_fiscal(texto):

    match = re.search(r'FISCAL.*?:\s*([A-Z\s]+)', texto.upper())
    if match:
        return match.group(1).strip()

    return "NO_IDENTIFICADO"


# =========================
# 4. PROCESAMIENTO POR CASO
# =========================

def procesar_caso(case_id, files):

    principal_file, texto = obtener_documento_principal(files)

    plazo_inicial = extraer_plazo(texto)
    fecha_inicio = datetime.today()  # ⚠️ luego mejorar

    prorrogas = obtener_prorrogas(files)
    total_prorroga = sum(p["dias"] for p in prorrogas)

    plazo_total = plazo_inicial + total_prorroga

    fecha_vencimiento = fecha_inicio + timedelta(days=plazo_total)

    hoy = datetime.today()

    if hoy > fecha_vencimiento:
        estado = "VENCIDO"
    elif (fecha_vencimiento - hoy).days <= 5:
        estado = "POR_VENCER"
    else:
        estado = "VIGENTE"

    delito_categoria, delito_desc = extraer_delito(texto)

    return {
        "case_id": case_id,
        "plazo_inicial": plazo_inicial,
        "total_prorroga": total_prorroga,
        "plazo_total": plazo_total,
        "estado": estado,
        "delito_categoria": delito_categoria,
        "delito_descripcion": delito_desc,
        "fiscal": extraer_fiscal(texto)
    }


# =========================
# 5. RUN PRINCIPAL
# =========================

def run(casos):

    print("\n🧠 PROCESANDO SILVER LAYER...")

    resultados = []

    for case_id, files in casos.items():

        try:
            data = procesar_caso(case_id, files)
            resultados.append(data)

            print(f"✔ Procesado: {case_id}")

        except Exception as e:
            print(f"❌ Error en caso {case_id}: {e}")

    print(f"\n✅ Total casos procesados: {len(resultados)}")

    return resultados
'''

from collections import defaultdict
from datetime import datetime, timedelta


def agrupar_por_caso(doc_ai_data):

    casos = defaultdict(list)

    for item in doc_ai_data:
        casos[item["case_id"]].append(item)

    return casos


def detectar_principal(docs):

    # 1. por clasificación
    for d in docs:
        if d.get("doc_type") == "DOCUMENTO_PRINCIPAL":
            return d

    # 2. fallback: menor archivo
    return sorted(docs, key=lambda x: x["file_name"])[0]


def detectar_prorrogas(docs):

    prorrogas = []

    for d in docs:
        if d.get("doc_type") == "PRORROGA":
            dias = extraer_dias(d.get("extracted", {}))
            prorrogas.append(dias)

    return prorrogas


def extraer_dias(extracted):

    for v in extracted.values():
        if isinstance(v, str):
            if "30" in v:
                return 30
            if "45" in v:
                return 45
            if "60" in v:
                return 60

    return 0


def construir_registro(case_id, principal, prorrogas):

    extracted = principal.get("extracted", {})

    plazo_inicial = extraer_dias(extracted)
    total_prorroga = sum(prorrogas)
    plazo_total = plazo_inicial + total_prorroga

    hoy = datetime.today()
    fecha_inicio = hoy
    fecha_vencimiento = fecha_inicio + timedelta(days=plazo_total)

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
        "fiscal": extracted.get("fiscal", "NO_IDENTIFICADO")
    }


def run(doc_ai_data):

    print("\n🧠 PROCESANDO SILVER...")

    casos = agrupar_por_caso(doc_ai_data)

    resultados = []

    for case_id, docs in casos.items():

        try:
            principal = detectar_principal(docs)
            prorrogas = detectar_prorrogas(docs)

            registro = construir_registro(
                case_id,
                principal,
                prorrogas
            )

            resultados.append(registro)

            print(f"✔ Procesado: {case_id}")

        except Exception as e:
            print(f"❌ Error en {case_id}: {e}")

    print(f"\n✅ Total casos: {len(resultados)}")

    return resultados