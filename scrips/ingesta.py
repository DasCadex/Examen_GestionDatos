import shutil

import pandas as pd 
import os
import logging 
from datetime import datetime



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/ingesta.log"),
        logging.StreamHandler()
    ]

)

#archivos que vamos a usa

ARCHIVOS={
    "ventas_datamart":          "data/raw/ventas_datamart.csv",
}


def ingetar_datos(nombre_archivo, ruta):
    logging.info(F"Comenzado la ingesta del archivo{nombre_archivo}")

    if not os.path.exists(ruta):
        logging.error(f"el archiuvo {nombre_archivo}no fue encontrado en la ruta {ruta}")
        return None 
    
    #creamod el data frame 
    df=pd.read_csv(ruta)
    logging.info(f"cargando archivo:{ruta}")

    logging.info(f"shape: {df.shape}filas y con  {df.shape[1]} columnas")

    logging.info(f"lista de columnas: {df.columns}")#con esto podemos ver las columnas que tiene el archivo

    logging.info(f"tipo de datos :{df.dtypes.to_string()}")#con esto podemos ver el tipo de datos que tiene cada columna
    logging.info(f"Valores nulos por columna:\n{df.isnull().sum().to_string()}")
    logging.info(f"Duplicados: {df.duplicated().sum()}")


    #respaldo de los datos
    respaldo=(f"data/respaldo/{nombre_archivo}.csv")
    shutil.copy(ruta, respaldo)#shutil es una libreria que nos permite copiar archivos de un lugar a otro
    logging.info(f"repaldo guardado en: {respaldo}")

    return df 

def ejecucion_ingesta():
    logging.info("======== Etapa 1: Iniciando la ingesta de datos=========")
    inicio = datetime.now()

    datasets={}
    datasets = {}#definimos un diccionario vacio para guardar los data frames de cada dataset que se ingesten
    for nombre, ruta in ARCHIVOS.items():#
        df = ingetar_datos(nombre, ruta)#
        if df is not None:
            datasets[nombre] = df

    logging.info(f"Tablas ingestadas: {list(datasets.keys())}")
    logging.info(f"Tiempo total: {datetime.now() - inicio}")
    logging.info("====== FIN ETAPA 1: INGESTA ======")

if __name__ == "__main__":
    ejecucion_ingesta()