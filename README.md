# AutoGCS

Automatización de descarga y gestión de archivos desde Google Cloud Storage (GCS) usando `gsutil`, orientado a entornos Windows con archivos `.csv` y `.gz`.

## 📌 Funcionalidad

- Descarga bases diarias o cierres mensuales desde GCS.
- Verifica si los archivos ya existen localmente y si son iguales.
- Descomprime `.gz` automáticamente.
- Realiza backups si existe una versión anterior.
- Agrupa bases por mes o tipo (`DIARIOS`, `CIERRES`) en carpetas estructuradas.
- Registra logs en consola y archivo `.log`.
- Documenta cada acción en un archivo CSV (`Documentacion_CierresActualizaciones.csv`).

## 🧰 Requisitos

- Google Cloud SDK instalado (incluye `gsutil`) https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe?hl=es-419
- Python 3.9 o superior https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe
- `colorama` para los logs de colores:
  ```PowerShell
  pip install colorama
