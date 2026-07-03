import re

import pandas as pd 
import os 
import shutil
import logging 
from datetime import datetime 
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")


os.makedirs('logs',exist_ok=True)
os.makedirs('data/procesado',exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/limpieza.log"),
        logging.StreamHandler()
    ]

)
def unificar_fecha(fecha):#una funcion que recibe una fecha y la unifica a formato yyyy-mm-dd
    fecha = str(fecha).strip()#recibimos la fecha y la convertimos a string y le quitamos espacios en blanco
    if re.match(r'^\d{4}-\d{2}-\d{2}$', fecha):#si la fecha ya esta en formato yyyy-mm-dd, la devolvemos tal cual
        return fecha#returnamos la fecha tal cual1
    if re.match(r'^\d{2}[-/]\d{2}[-/]\d{4}$', fecha):#si la fecha esta en formato dd-mm-yyyy o dd/mm/yyyy, la convertimos a formato yyyy-mm-dd
        sep = '-' if '-' in fecha else '/'#logica para determinar el separador de la fecha
        d, m, a = fecha.split(sep)#convertimos la fecha a formato yyyy-mm-dd
        return f"{a}-{m}-{d}"#returnamos la fecha en formato yyyy-mm-dd
    return None#si la fecha no cumple con ningun formato, devolvemos None

def normalizar_rut(rut):
    limpio = re.sub(r'[.\s]', '', str(rut).strip())#tomamos un rut y le quitamos puntos
    if '-' in limpio:#si el rut tiene un guion, lo separamos en cuerpo y dv(signo verificador)
        cuerpo, dv = limpio.split('-')
    else:
        cuerpo, dv = limpio[:-1], limpio[-1]#ssi no tiene gion tomamops el ultimo numero que sera el dv
    return f"{cuerpo}-{dv}"

def limpieza_datos(df):

    logging.info(f"comenzando la limpiesa de datos")
    antes=len(df)
    #boramos duplicados
    df =df.drop_duplicates()

    #correguimos la cantidad 
    df = df[df['cantidad'] > 0]#eliminamos los productos con cantidad menor o igual a 0

    #correguir decuneto menor a 100
    df = df[df['descuento_pct'] <= 100]#eliminamos los productos con descuento mayor a 100

    #quitar signos al precio 
    df['precio_unitario'] = pd.to_numeric(
    df['precio_unitario']
      .astype(str)
      .str.replace(r'\$', '', regex=True)
      .str.replace(r'\.(?=\d{3}\b)', '', regex=True),  # solo puntos de miles
        errors='coerce'
    )

    #correguimos el formato del rut
    df['rut_cliente'] = df['rut_cliente'].apply(normalizar_rut)

    #normalizar nombres categorias y quitar mayusculas 
    df['categoria']=df['categoria'].str.strip().str.lower()#quitamos espacio en blanco y pasamos a minusculas

    #monbres pasar a minusculas , la primera en mayuscula 
    df['nombre_cliente'] = df['nombre_cliente'].str.lower().str.title().str.strip()

    #region en blanco 

    df['region'] = df['region'].fillna(f"Region no registrada")

    #correguir fechas a formato yyyy-mm-dd y cambiar a tipo fecha
    df['fecha_pedido'] = pd.to_datetime(df['fecha_pedido'].apply(unificar_fecha)).dt.strftime('%Y-%m-%d')
    df['fecha_despacho'] = pd.to_datetime(df['fecha_despacho'].apply(
        lambda x: unificar_fecha(x) if pd.notna(x) else None
    )).dt.strftime('%Y-%m-%d')

    #correguir logica de megocio 
    
    sin_despacho = df[#creamos un dataframe con los pedidos que estan entregados pero no tienen fecha de despacho
        (df['estado_pedido'] == 'entregado') & df['fecha_despacho'].isna()#condicion para filtrar los pedidos entregados sin fecha de despacho
    ]
    if len(sin_despacho):#chequeamos si hay pedidos entregados sin fecha de despacho
        logging.warning(f"Pedidos 'entregado' sin fecha_despacho: {len(sin_despacho)}")#si hay pedidos entregados sin fecha de despacho, lo registramos en el log

    df['fecha_pedido'] = pd.to_datetime(
        df['fecha_pedido'].apply(unificar_fecha)
    ).dt.strftime('%Y-%m-%d')

    logging.info(f"Limpieza finalizada: {antes} → {len(df)} filas")
    return df
def ejecutar_limpieza():
    logging.info("====== ETAPA 2: LIMPIEZA ======")
    inicio = datetime.now()

    funciones = {
        "ventas_datamart": limpieza_datos

    }

    for nombre, funcion in funciones.items():
        ruta = f"data/raw/{nombre}.csv"
        if not os.path.exists(ruta):
            logging.error(f"No existe: {ruta}")
            continue
        df = pd.read_csv(ruta)
        df_limpio = funcion(df)
        df_limpio.to_csv(f"data/procesado/{nombre}_clean.csv", index=False)
        logging.info(f"Guardado: data/procesado/{nombre}_clean.csv")

    logging.info(f"Tiempo: {datetime.now() - inicio}")
    logging.info("====== FIN ETAPA 2 ======")

if __name__ == "__main__":
    ejecutar_limpieza()