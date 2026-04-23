'''
from dotenv import load_dotenv
import os

from src.extract import extract_data
from src.utils.file_converter import convert_to_pdf
from src.load import bronze
from src.load import silver


def build_cases_from_folders(base_path):
    """
    Construye dict de casos leyendo carpetas:
    { case_id: [pdf_paths] }
    """
    casos = {}

    if not os.path.exists(base_path):
        print(f"❌ Ruta no existe: {base_path}")
        return casos

    for case_folder in os.listdir(base_path):
        case_path = os.path.join(base_path, case_folder)

        if os.path.isdir(case_path):

            # filtro básico (ej: 1-2026)
            if "-" not in case_folder:
                continue

            pdfs = []

            for file in os.listdir(case_path):
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(case_path, file)
                    pdfs.append(full_path)

            if pdfs:
                casos[case_folder] = pdfs

    return casos


def run():

    # 🔹 Cargar variables de entorno
    load_dotenv()

    print("\n===== INICIO PIPELINE =====\n")

    # =========================
    # 1. EXTRACT (SQL Server → DOC/DOCX)
    # =========================
    print("1. EXTRACT...")
    documents = extract_data.run()

    print(f"Total documentos extraídos: {len(documents)}")

    if not documents:
        print("⚠️ No se encontraron documentos. Fin del pipeline.")
        return

    # =========================
    # 2. CONVERSIÓN A PDF
    # =========================
    print("\n2. CONVERSIÓN A PDF...")

    pdf_files = []

    for doc in documents:
        try:
            pdf = convert_to_pdf(doc)

            if pdf:
                pdf_files.append(pdf)

        except Exception as e:
            print(f"❌ Error convirtiendo {doc}: {e}")

    print(f"Total PDFs generados: {len(pdf_files)}")

    if not pdf_files:
        print("⚠️ No se generaron PDFs. Fin del pipeline.")
        return

    # =========================
    # 3. ORGANIZACIÓN POR CASOS (DESDE CARPETAS)
    # =========================
    print("\n3. ORGANIZANDO POR CASOS DESDE CARPETAS...")

    BASE_PATH = "data/pdf"  # 👈 ajusta si cambia

    casos = build_cases_from_folders(BASE_PATH)

    print(f"📂 Casos detectados: {len(casos)}")

    if not casos:
        print("⚠️ No se detectaron casos en carpetas. Fin del pipeline.")
        return

    for case_id in list(casos.keys())[:5]:
        print(f"✔ Caso: {case_id} ({len(casos[case_id])} archivos)")

    # =========================
    # 4. VALIDACIÓN LOCAL
    # =========================
    print("\n📂 Validando archivos generados...")

    for pdf in pdf_files[:5]:
        print(f"✔ PDF generado: {pdf}")

    # =========================
    # 5. LOAD BRONZE (GCS)
    # =========================
    print("\n4. LOAD BRONZE...")

    bronze_data = bronze.run(casos)

    print(f"☁️ Archivos subidos a Bronze: {len(bronze_data)}")

    if not bronze_data:
        print("⚠️ No se subieron archivos a Bronze.")
        return

    # =========================
    # 6. SILVER (PROCESAMIENTO)
    # =========================
    print("\n5. SILVER...")

    silver_data = silver.run(casos)

    print(f"📊 Registros Silver: {len(silver_data)}")

    if not silver_data:
        print("⚠️ No se generaron datos Silver.")
        return

    # =========================
    # FUTURAS ETAPAS
    # =========================

    """
    # 7. LOAD GOLD (BigQuery)
    from src.load import gold
    print("\n6. LOAD GOLD...")
    gold.run(silver_data)

    # 8. REPORTE FINAL
    print("\n7. REPORTE FINAL:")
    print(silver_data)
    """

    print("\n===== PIPELINE COMPLETO HASTA SILVER =====\n")


if __name__ == "__main__":
    run()



'''

from dotenv import load_dotenv
import os

from src.extract import extract_data
from src.utils.file_converter import convert_to_pdf
from src.load import bronze
from src.transform import document_ai
from src.load import silver


def build_cases_from_folders(base_path):

    casos = {}

    if not os.path.exists(base_path):
        print(f"❌ Ruta no existe: {base_path}")
        return casos

    for case_folder in os.listdir(base_path):

        case_path = os.path.join(base_path, case_folder)

        if os.path.isdir(case_path) and "-" in case_folder:

            pdfs = [
                os.path.join(case_path, f)
                for f in os.listdir(case_path)
                if f.lower().endswith(".pdf")
            ]

            if pdfs:
                casos[case_folder] = pdfs

    return casos


def run():

    load_dotenv()

    print("\n===== INICIO PIPELINE =====\n")

    # =========================
    # 1. EXTRACT
    # =========================
    print("1. EXTRACT...")
    documents = extract_data.run()

    if not documents:
        print("⚠️ Sin documentos")
        return

    # =========================
    # 2. CONVERT
    # =========================
    print("\n2. PDF...")
    pdf_files = []

    for d in documents:
        pdf = convert_to_pdf(d)
        if pdf:
            pdf_files.append(pdf)

    if not pdf_files:
        print("⚠️ No se generaron PDFs")
        return

    # =========================
    # 3. BUILD CASES
    # =========================
    print("\n3. CASOS...")
    casos = build_cases_from_folders("data/pdf")

    if not casos:
        print("⚠️ No hay casos")
        return

    print(f"📂 Casos detectados: {len(casos)}")

    # =========================
    # 4. BRONZE
    # =========================
    print("\n4. BRONZE...")
    bronze_data = bronze.run(casos)

    if not bronze_data:
        print("⚠️ Bronze vacío")
        return

    # =========================
    # 5. DOCUMENT AI
    # =========================
    print("\n5. DOCUMENT AI...")

    doc_ai_data = document_ai.run(
        bronze_data,
        classifier_id=os.getenv("DOCAI_CLASSIFIER_ID"),
        extractor_id=os.getenv("DOCAI_EXTRACTOR_ID")
    )

    # =========================
    # 6. SILVER
    # =========================
    print("\n6. SILVER...")

    silver_data = silver.run(doc_ai_data)

    print(f"\n📊 Casos finales: {len(silver_data)}")

    print("\n===== PIPELINE COMPLETO =====\n")


if __name__ == "__main__":
    run()