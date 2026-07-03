import logging
import os
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/main.log"),
        logging.StreamHandler()
    ]
)

from scrips.ingesta    import ejecucion_ingesta
from scrips.limpieza   import ejecutar_limpieza
from scrips.validacion import ejecutar_validacion
from scrips.cargaBD    import ejecutar_carga

if __name__ == "__main__":
    logging.info("========================================")
    logging.info("   INICIO DEL PIPELINE DE DATOS")
    logging.info("========================================")
    inicio = datetime.now()

    try:
        logging.info(">>> ETAPA 1: INGESTA")
        ejecucion_ingesta()

        logging.info(">>> ETAPA 2: LIMPIEZA")
        ejecutar_limpieza()

        logging.info(">>> ETAPA 3: VALIDACIÓN")
        ejecutar_validacion()

        logging.info(">>> ETAPA 4: CARGA")
        ejecutar_carga()

        logging.info("========================================")
        logging.info(f"   PIPELINE COMPLETADO EN {datetime.now() - inicio}")
        logging.info("========================================")

    except Exception as e:
        logging.error(f"PIPELINE INTERRUMPIDO: {e}")
        raise