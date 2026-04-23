import os
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USER')};"
        f"PWD={os.getenv('SQL_PASSWORD')}"
    )


def parse_case(case_str):
    num, year = case_str.split("-")
    return int(num), int(year)


def run():

    cases = [
        "1-2026","2-2026","5-2026","6-2026","11-2026",
        "15-2026","17-2026","22-2026","33-2026","34-2026",
        "38-2026","42-2026","40-2026","41-2026","44-2026",
        "46-2026","47-2026","49-2026","50-2026"
    ]

    conn = get_connection()
    cursor = conn.cursor()

    saved_files = []

    for case in cases:
        numcaso, anio = parse_case(case)

        print(f"\n🔍 Procesando caso: {case}")

        case_dir = f"data/raw/{case}"
        os.makedirs(case_dir, exist_ok=True)

        query = f"""
        SELECT 
            N.DESPACHO,
            N.COD_NUM_DOC,
            N.NUMDOC,
            L.DOCUMENTO,
            L.EXT_DOC_CASO,
            N.TIPO_DOCUMENTO
        FROM CASO C
        INNER JOIN NUMERODOC N 
            ON C.CODDESPACHO = N.DESPACHO 
            AND C.CODNUMDOC = N.COD_NUM_DOC
        INNER JOIN LEGADOCCASO L 
            ON L.DESPACHO = N.DESPACHO 
            AND L.COD_NUM_DOC = N.COD_NUM_DOC
        WHERE 
            C.NUMCASO = {numcaso}
            AND C.AÑOCASO = {anio}
            AND N.TIPO_DOCUMENTO IN (2, 64111)
        ORDER BY 
            CASE 
                WHEN N.TIPO_DOCUMENTO = 2 THEN 1
                WHEN N.TIPO_DOCUMENTO = 64111 THEN 2
                ELSE 3
            END
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:

            despacho = row.DESPACHO
            cod_doc = row.COD_NUM_DOC
            numdoc = row.NUMDOC
            file_data = row.DOCUMENTO
            ext = row.EXT_DOC_CASO.strip() if row.EXT_DOC_CASO else "docx"

            file_name = f"{cod_doc}-{despacho}-{numdoc}.{ext}"
            file_path = os.path.join(case_dir, file_name)

            try:
                with open(file_path, "wb") as f:
                    f.write(file_data)

                print(f"✔ Guardado: {file_path}")
                saved_files.append(file_path)

            except Exception as e:
                print(f"❌ Error guardando archivo: {e}")

    cursor.close()
    conn.close()

    return saved_files