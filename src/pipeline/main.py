from dotenv import load_dotenv
import os

from src.extract import extract_data
from src.utils.file_converter import convert_to_pdf
from src.load import bronze
from src.load import silver


def build_cases_from_folders(base_path):

    casos = {}

    if not os.path.exists(base_path):
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

    print("\n===== PIPELINE =====\n")

    # =========================
    # 1. EXTRACT
    # =========================
    documents = extract_data.run()
    if not documents:
        return

    # =========================
    # 2. CONVERT
    # =========================
    pdf_files = [convert_to_pdf(d) for d in documents if convert_to_pdf(d)]
    if not pdf_files:
        return

    # =========================
    # 3. CASOS
    # =========================
    casos = build_cases_from_folders("data/pdf")
    if not casos:
        return

    # =========================
    # 4. BRONZE
    # =========================
    bronze_data = bronze.run(casos)

    # =========================
    # 5. SILVER (GEMINI REAL)
    # =========================
    silver_data = silver.run(bronze_data)

    print(f"\n📊 Casos finales: {len(silver_data)}")

    print("\n===== FIN =====\n")


if __name__ == "__main__":
    run()