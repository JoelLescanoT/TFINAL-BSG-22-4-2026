import os
import subprocess

SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


def convert_to_pdf(input_path, output_base_dir="data/pdf"):
    try:
        # RUTAS ABSOLUTAS (CLAVE 🔥)
        input_path = os.path.abspath(input_path)

        case_folder = os.path.basename(os.path.dirname(input_path))
        output_dir = os.path.abspath(os.path.join(output_base_dir, case_folder))

        os.makedirs(output_dir, exist_ok=True)

        # Ejecutar LibreOffice
        result = subprocess.run([
            SOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ], capture_output=True, text=True)

        # DEBUG (muy importante)
        if result.returncode != 0:
            print(f"❌ LibreOffice error: {result.stderr}")
            return None

        # Nombre esperado
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        pdf_path = os.path.join(output_dir, base_name + ".pdf")

        # VALIDACIÓN REAL
        if not os.path.exists(pdf_path):
            print(f"⚠ LibreOffice NO generó archivo en: {pdf_path}")
            print("Salida LibreOffice:", result.stdout)
            return None

        print(f"✔ Convertido: {input_path} → {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"❌ Error convirtiendo {input_path}: {e}")
        return None