# 📊 Pipeline de Procesamiento de Documentos Fiscales con Vertex AI (Gemini)

## 🧠 Descripción

Este proyecto implementa un pipeline de datos para procesar documentos PDF provenientes de fiscalía, extraer información relevante mediante IA generativa (Gemini) y estructurarla en formato JSON.

El objetivo es automatizar la interpretación de documentos legales, identificando datos clave como:

* Plazos procesales
* Prórrogas
* Fiscal asignado
* Delito
* (En mejora: número de caso, partes involucradas)

---

## 🏗️ Arquitectura del Proyecto

Pipeline basado en arquitectura tipo **Medallion (Bronze → Silver → Gold)**:

```
SQL Server
   ↓
Extracción (Python)
   ↓
Google Cloud Storage (Bronze)
   ↓
Vertex AI - Gemini (Silver)
   ↓
JSON estructurado
   ↓
(Futuro: BigQuery / Gold)
```

---

## ⚙️ Tecnologías Utilizadas

* Python 3.11+
* Google Cloud Platform (GCP)

  * Vertex AI (Gemini)
  * Cloud Storage
* SQL Server
* pdfplumber
* Vertex AI SDK

---

## 📁 Estructura del Proyecto

```
src/
 ├── extract/        # Extracción desde SQL Server
 ├── load/           # Carga a GCS (Bronze, Silver, Gold)
 ├── transform/      # Limpieza y procesamiento con Gemini
 ├── pipeline/       # Orquestación del flujo
data/
 ├── raw/            # PDFs locales
 ├── data_contract/  # Esquemas JSON
tests/
notebooks/
```

---

## 🔄 Flujo del Pipeline

### 🟤 Bronze Layer

* Extracción de PDFs desde SQL Server
* Almacenamiento en Google Cloud Storage

### ⚪ Silver Layer

* Lectura de PDFs desde GCS
* Extracción de texto con `pdfplumber`
* Procesamiento con **Gemini 2.5 Flash**
* Generación de JSON estructurado

Ejemplo de salida:

```json
{
  "plazo_dias": 60,
  "es_prorroga": false,
  "dias_prorroga": null,
  "fiscal": "J. Lezcano",
  "delito": "Lesiones Culposas"
}
```

### 🟡 Gold Layer (en desarrollo)

* Almacenamiento estructurado (BigQuery)
* Análisis y explotación de datos

---

## 🤖 Uso de IA (Gemini)

Modelo utilizado:

```
gemini-2.5-flash
```

Funciones principales:

* Interpretación de documentos legales
* Extracción de entidades clave
* Generación de JSON estructurado

---

## 🚀 Cómo ejecutar el proyecto

### 1. Clonar repositorio

```
git clone https://github.com/JoelLescanoT/TFINAL-BSG-22-4-2026.git
cd TFINAL-BSG-22-4-2026
```

### 2. Crear entorno virtual

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```
set GCP_PROJECT_ID=tu_proyecto
set GCP_LOCATION=us-central1
```

### 5. Ejecutar pipeline

```
python -m src.pipeline.main
```

---

## 💰 Costos estimados

El pipeline utiliza un modelo **serverless (pago por uso)**.

| Servicio           | Costo estimado  |
| ------------------ | --------------- |
| Vertex AI (Gemini) | ~$0.02 USD      |
| Cloud Storage      | ~$0.002 USD     |
| **Total**          | **< $0.05 USD** |

Esto permite escalar el sistema sin inversión inicial significativa.

---

## ⚠️ Consideraciones

* El modelo puede devolver texto no estructurado → se maneja con validación JSON
* PDFs escaneados pueden afectar la extracción
* Se limita el texto enviado a Gemini (~15k caracteres)
* No subir credenciales (`gcp-key.json`) al repositorio
* No subir `.venv` ni carpeta `data/`

---

## 🔮 Mejoras Futuras

* Implementación de capa Gold (BigQuery)
* Mejora del prompt (mayor precisión)
* Extracción de nuevos campos:

  * número de caso
  * parte investigada
  * parte agraviada
* Integración con OCR para PDFs escaneados
* Métricas de calidad del modelo

---

## 👨‍💻 Autor

**Joel Lescano**

---

## 📌 Estado del Proyecto

🚧 MVP funcional con integración real de Vertex AI
