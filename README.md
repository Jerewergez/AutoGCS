<!-- Logo del equipo -->
<p align="center">
  <img width="600" src="https://github.com/user-attachments/assets/902f4638-7937-43d1-97ee-1f1dd6a32c56" alt="AutoGCS Team Logo" />
</p>

# AutoGCS

Automatización de descarga y gestión de archivos desde Google Cloud Storage (GCS) usando `gsutil`, orientado a entornos Windows con archivos `.csv` y `.gz`.

---

## 📌 Funcionalidad

- Descarga bases **diarias** o **cierres mensuales** desde GCS.
- Verifica si los archivos ya existen localmente y si son iguales.
- Descomprime `.gz` automáticamente.
- Realiza backups si existe una versión anterior.
- Agrupa bases por mes o tipo (`DIARIOS`, `CIERRES`) en carpetas estructuradas.
- Registra logs en consola y archivo `.log`.
- Documenta cada acción en un archivo CSV:  
  `Documentacion_CierresActualizaciones.csv`

---

## 🧰 Requisitos

- [Google Cloud SDK (gsutil)](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe?hl=es-419)
- [Python 3.9 o superior](https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe)
- `colorama` para logs con color:

```powershell
pip install colorama


##  📁 Estructura esperada
```Estructura
D:\
│
├── Bases Crudas\
│   └── [Categorías: RETENCIÓN, FCR, etc.]\
│       └── [Subcarpetas por tipo o mes]
│
└── Backup Bases Crudas\
    ├── Logs\
    │   ├── CierresActualizaciones.log
    │   └── Documentacion_CierresActualizaciones.csv
    └── Temp\
```
## 🚀 Ejecución del script

Desde PowerShell:

```PowerShell

python actualizacion_bases.py

Seleccionar una de las siguientes opciones:

Descargar bases diarias (DIARIOS)

Descargar cierres de un mes específico (CIERRES)
```

🔐 Configuración de entorno: gsutil

Para que el script detecte gsutil automáticamente, asegurate de:

Instalar Google Cloud SDK desde: https://cloud.google.com/sdk/docs/install

Agregar gsutil al PATH del sistema:

Instrucciones para Windows:
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin", [EnvironmentVariableTarget]::Machine)


Luego reiniciar PowerShell o el sistema para que se reconozca el cambio.

Verificá con:

gsutil version

🗓️ Automatización con Tareas Programadas

Abrí “Tareas Programadas” en Windows.

Crear una nueva tarea con:

Acción: Ejecutar python

Argumentos: ruta completa del script (ej: D:\AutoGCS\actualizacion_bases.py)

Inicio en: directorio del script

Activá opción “Ejecutar con privilegios más altos”.

Podés programar diariamente o mensual según el tipo de base.

🧾 Registro y trazabilidad

Cada acción se documenta en:

Logs\CierresActualizaciones.log: registro completo con timestamp y colores.

Logs\Documentacion_CierresActualizaciones.csv: lista de archivos procesados y estado (Actualizado, Sin cambios, No disponible, etc.).

🧪 Estado del proyecto

✔️ Funcional para Windows
✔️ Compatible con GCS
✔️ Modular para escalar nuevas bases
✔️ Trazabilidad completa

