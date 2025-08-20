# -- coding: utf-8 --
"""
actualizacion_bases.py

Automatiza la descarga de archivos desde Google Cloud Storage (gsutil),
descomprime .gz si es necesario, registra logs en consola y archivo,
y documenta cada acción en un CSV. Ahora incluye renombrado de archivos
con prefijo "DIARIOS_" para las descargas diarias.
"""

import subprocess
import shutil
import gzip
import logging
import csv
import sys
from pathlib import Path
from datetime import datetime
from colorama import init as colorama_init, Fore, Style
import re

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================

# Rutas de trabajo
BASE_DIR = Path(r"D:\Bases Crudas")
BACKUP_DIR = Path(r"D:\Backup Bases Crudas")
TEMP_DIR = BACKUP_DIR / "Temp"
LOG_FILE = BACKUP_DIR / "Logs" / "CierresActualizaciones.log"
DOC_CSV = BACKUP_DIR / "Logs" / "Documentacion_CierresActualizaciones.csv"

# Diccionario meses (para cierres mensuales)
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Lista de archivos base a procesar (solo cambiará la carpeta origen/destino según tipo de descarga)
FILES_CONFIG = [
    # Archivos de RETENCIÓN
    { "url": "gs://teco_reporting_konecta/CIERRES/ATENDIDAS_BAJAS_45D_000000000000.csv",
      "dest": BASE_DIR /"02 - RETENCIÓN" / "BAJA_45D" },
    { "url": "gs://teco_reporting_konecta/CIERRES/RETENCION_FAN_000000000000.csv",
      "dest": BASE_DIR / "02 - RETENCIÓN" / "RETENCION_FAN" },
    { "url": "gs://teco_reporting_konecta/CIERRES/CABLE_MODEM_SOLICITUDES_BAJAS_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "02 - RETENCIÓN" / "BAJAS_CABLE MODEM"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/SIEBEL_MOVIL_RETENCION_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "02 - RETENCIÓN" / "SIEBEL"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/CABLE_MODEM_RETENCIONES_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "02 - RETENCIÓN" / "RETENCION_CM" },
    { "url": "gs://teco_reporting_konecta/CIERRES/INTERACCIONES_OPEN_MESACTUAL.csv",
      "dest": BASE_DIR / "02 - RETENCIÓN" / "INTERACCIONES_OPEN" },
    # Archivos de FCR
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_SOPORTE_7D_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "SOPORTE_7D" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_SOPORTE_DIGITAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "SOPORTE_DIGITAL" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_ONBOARDING_DIGITAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "ONBOARDING_DIGITAL" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_OMNICANAL_7D_SMB_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "OMNICANAL_7D_SMB_CUIT" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_OMNICANAL_7D_SMB_ANI_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "OMNICANAL_7D_SMB" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_CARING_DIGITAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "CARING_DIGITAL" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_CARING_CONVERGENTE_7D_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "CARING_CONVERGENTE_7D" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_CARING_7D_MOVIL_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "CARING_7D_MOVIL" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_CARING_7D_CABLE_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "CARING_7D_CABLE" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_RETENCION_CROSS_7D_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "RETENCION_CROSS_7D" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_OMNICANAL_30D_SMB_ANI_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "OMNICANAL_30D_SMB" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_RETENCION_CROSS_30D_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "RETENCION_CROSS_30D" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FCR_OMNICANAL_MASIVO_30D_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "03 - FCR" / "OMNICANAL_30D_MASIVO" },
    # Archivos Genesys PIC 
    { "url": "gs://teco_reporting_konecta/CIERRES/GENESYS_PIC_IN_MESACTUAL_000000000000.csv.gz",
      "dest": BASE_DIR / "04 - PIC" / "GENESYS_PIC" },
    { "url": "gs://teco_reporting_konecta/CIERRES/TRANSFERENCIAS_PIC_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "04 - PIC" / "TRANSFERENCIAS_PIC" },
    { "url": "gs://teco_reporting_konecta/CIERRES/SE_CORTO_CALL_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "04 - PIC"/ "SE_CORTO_CALL"  },
    # Archivos de PRODUCTIVIDAD
    { "url": "gs://teco_reporting_konecta/CIERRES/PRODUCTIVIDAD_YOIZEN_DIARIA_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "05 - PRODUCTIVIDAD" / "YOIZEN_DIARIA"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/PRODUCTIVIDAD_TIEMPOS_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "05 - PRODUCTIVIDAD" / "PRODUCTIVIDAD_TIEMPOS"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/PRODUCTIVIDAD_YOIZEN_MESACTUAL_000000000000.csv.gz",
      "dest": BASE_DIR / "05 - PRODUCTIVIDAD" / "YOIZEN" },
    { "url": "gs://teco_reporting_konecta/CIERRES/DETALLE_CASOS_YOIZEN_MESACTUAL_000000000000.csv.gz",
     "dest": BASE_DIR /  "05 - PRODUCTIVIDAD" / "PRODUCTIVIDAD_CASOS"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/PRODUCTIVIDAD_YOIZEN_DIARIA_SMB_MESACTUAL_000000000000.csv",
     "dest": BASE_DIR /  "05 - PRODUCTIVIDAD" / "YOIZEN_DIARIA_SMB"  },
    # Archivos de SERVICIOS
    { "url": "gs://teco_reporting_konecta/CIERRES/SERVICES_FAN000000000000.csv.gz",
      "dest": BASE_DIR / "06 - SERVICE" / "SERVICES_FAN"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/OPEN_SERVICES_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "06 - SERVICE" / "OPEN_SERVICES"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/ICD_INCIDENTES_CON_ANOMALIAS_CITAS_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "06 - SERVICE" / "ICD_INCIDENTES_CON_ANOMALIAS_CITAS"  },
    # Archivos de ACTIVIDAD COMERCIAL
    { "url": "gs://teco_reporting_konecta/CIERRES/DEBITOS_AUTOMATICOS_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" / "DEBITOS_AUTOMATICOS" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FACTURA_UNIFICADA_GESTIONES_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" / "FACTURA_UNIFICADA_GESTIONES" },
    { "url": "gs://teco_reporting_konecta/CIERRES/PORTABILIDAD_MOVIL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" / "PORTABILIDAD_MOVIL" },
    { "url": "gs://teco_reporting_konecta/CIERRES/FIJO_ABONOS_VENTAS_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" / "FIJO_ABONOS"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/MOVIL_CAMBIO_PLAN_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" / "CAMBIO_PLAN_MOVIL"  },
    { "url": "gs://teco_reporting_konecta/CIERRES/ISLA_DEGRA_COBRABILIDAD_MESACTUAL_000000000000.csv",
      "dest": BASE_DIR / "07 - ACTIVIDAD COMERCIAL" /"ISLA_DEGRA_COBRABILIDAD"  }
]

# =========================================================
# 2. UTILIDADES Y SOPORTE
# =========================================================

def setup_directories():
    """Crea las carpetas necesarias y el CSV de documentación si no existe."""
    for p in (LOG_FILE.parent, DOC_CSV.parent, TEMP_DIR, BACKUP_DIR):
        p.mkdir(parents=True, exist_ok=True)
    if not DOC_CSV.exists():
        with DOC_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Timestamp", "FileName", "Action"])

def configure_logger():
    """Configura logger para salida en consola y archivo."""
    colorama_init()
    logger = logging.getLogger("ActualizacionBases")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt_console = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    fmt_file = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s", "%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt_console)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt_file)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

def document_action(filename: str, action: str):
    """Registra acción en CSV."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with DOC_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ts, filename, action])

def color_text(level: str, msg: str) -> str:
    """Colores en consola."""
    colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "WARNING": Fore.YELLOW, "ERROR": Fore.RED}
    return f"{colors.get(level, '')}{msg}{Style.RESET_ALL}"

def find_gsutil(logger: logging.Logger) -> str:
    """Busca gsutil en el PATH."""
    gsutil_path = shutil.which("gsutil")
    if not gsutil_path:
        logger.error(color_text("ERROR", "gsutil no encontrado."))
        sys.exit(1)
    return gsutil_path

def get_gsutil_file_info(gsutil_cmd: str, url: str, logger: logging.Logger):
    """Obtiene tamaño de archivo en GCS."""
    try:
        result = subprocess.run([gsutil_cmd, "ls", "-l", url], capture_output=True, check=True, text=True, encoding="utf-8")
        output_lines = result.stdout.strip().splitlines()
        target_line = next((line for line in output_lines if url in line and not line.strip().startswith("TOTAL:")), None)
        if not target_line:
            return None
        parts = target_line.strip().split()
        if len(parts) >= 3:
            return int(parts[0])
    except subprocess.CalledProcessError:
        return None
    return None

# =========================================================
# 3. PROCESAMIENTO DE ARCHIVOS
# =========================================================

def process_file(item: dict, logger: logging.Logger, gsutil_cmd: str, prefix: str = ""):
    """
    Descarga un archivo, lo descomprime si es necesario,
    renombra con prefijo opcional, respalda versión anterior
    y mueve a destino.
    """
    url = item["url"]
    dest_dir = item["dest"]
    orig_filename = Path(url).name

    # Quita extensión .gz para trabajar el nombre final
    final_filename_base = orig_filename.removesuffix('.gz')

    # Aplica prefijo si se definió y no existe aún
    if prefix and not final_filename_base.startswith(prefix):
        final_filename_base = f"{prefix}{final_filename_base}"

    temp_download_path = TEMP_DIR / orig_filename
    final_temp_path = TEMP_DIR / final_filename_base
    destination_path = dest_dir / final_filename_base

    try:
        logger.info(color_text("INFO", f"Procesando: {orig_filename}"))
        size_gs = get_gsutil_file_info(gsutil_cmd, url, logger)
        if size_gs is None:
            document_action(orig_filename, "No encontrado en GCS")
            return

        # Verifica si existe y es idéntico
        if destination_path.exists() and destination_path.stat().st_size == size_gs:
            logger.info(color_text("INFO", "Archivo ya actualizado."))
            document_action(orig_filename, "Sin cambios")
            return

        # Descarga desde GCS
        dest_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([gsutil_cmd, "cp", url, str(temp_download_path)], check=True)

        # Descompresión si es .gz
        if orig_filename.endswith(".gz"):
            with gzip.open(temp_download_path, "rb") as gz_in, open(final_temp_path, "wb") as out_f:
                shutil.copyfileobj(gz_in, out_f)
            temp_download_path.unlink()
        else:
            temp_download_path.rename(final_temp_path)

        # Backup versión anterior
        if destination_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"{destination_path.stem}_backup_{timestamp}{destination_path.suffix}"
            shutil.move(str(destination_path), str(backup_path))
            document_action(backup_path.name, "Backup creado")

        # Mueve nuevo archivo a destino
        final_temp_path.replace(destination_path)
        document_action(destination_path.name, "Actualizado correctamente")
        logger.info(color_text("SUCCESS", f"Guardado: {destination_path}"))

    except subprocess.CalledProcessError as e:
        document_action(orig_filename, f"Error gsutil: {e}")
    except Exception as e:
        document_action(orig_filename, f"Error: {e}")

# =========================================================
# 4. DESCARGAS DE CIERRE MENSUAL
# =========================================================

def check_gcs_file_exists(gsutil_cmd: str, url: str) -> bool:
    """Verifica si existe en GCS."""
    try:
        subprocess.run([gsutil_cmd, "-q", "ls", url], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def procesar_descarga_cierre_mensual(year: int, month_num: int, logger: logging.Logger, gsutil_cmd: str):
    """Descarga cierres para un mes y año específicos."""
    cierre_tag = f"CIERRE_{year}{month_num:02d}"
    month_name = MESES_ES[month_num]
    found_any_for_month = False

    for config in FILES_CONFIG:
        orig_filename = Path(config["url"]).name
        new_filename = orig_filename.replace("MESACTUAL", cierre_tag).replace("MESANTERIOR", cierre_tag)
        base_gcs_path = config["url"].rsplit('/', 1)[0]
        new_url = f"{base_gcs_path}/{new_filename}"
        new_dest = config["dest"] / f"{month_num:02d} - {month_name}"

        if check_gcs_file_exists(gsutil_cmd, new_url):
            found_any_for_month = True
            process_file({"url": new_url, "dest": new_dest}, logger, gsutil_cmd)

    if not found_any_for_month:
        logger.info(color_text("INFO", f"No hay cierres para {month_name} {year}"))

# =========================================================
# 5. LIMPIEZA Y MENÚ PRINCIPAL
# =========================================================

def cleanup(logger: logging.Logger):
    """Limpia carpeta temporal."""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        logger.info(color_text("INFO", "Temp limpiado."))

def main():
    setup_directories()
    logger = configure_logger()
    gsutil_command = find_gsutil(logger)

    while True:
        print("\n" + "="*60)
        print("1. Descargar bases DIARIAS")
        print("2. Descargar bases de CIERRE (mes/año)")
        print("3. Salir")
        print("="*60)
        choice = input("Opción: ").strip()

        if choice == '1':
            logger.info(color_text("INFO", "Descarga DIARIAS"))
            diarios_config = [{**item, "url": item["url"].replace("CIERRES", "DIARIOS")} for item in FILES_CONFIG]
            for item in diarios_config:
                process_file(item, logger, gsutil_command, prefix="DIARIOS_")
            break

        elif choice == '2':
            try:
                year = int(input("Año: ").strip())
                month = int(input("Mes (1-12): ").strip())
                if not (2020 < year < 2040 and 1 <= month <= 12):
                    print(color_text("ERROR", "Año o mes inválido."))
                else:
                    procesar_descarga_cierre_mensual(year, month, logger, gsutil_command)
                    break
            except ValueError:
                print(color_text("ERROR", "Formato inválido."))

        elif choice == '3':
            break

        else:
            print(color_text("ERROR", "Opción no válida."))

    cleanup(logger)
    logger.info(color_text("INFO", "=== FIN ==="))

if __name__ == "__main__":
    main()

