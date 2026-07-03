from gettext import install

import pandas as pd
# keep pandera alias for exceptions and helpers
import pandera as pa
from pandera import Column, DataFrameSchema, Check
# Note: avoid reassigning `pa` alias; use `pandera` as `pa` only once
import os
import logging
from datetime import datetime

os.makedirs("logs",exist_ok=True)
os.makedirs("data/validados",exist_ok=True)
os.makedirs("data/error",exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/validacion.log"),
        logging.StreamHandler()
    ]
)


#definiremos el esquema de validacion de la unica tabla que trabajaremos 
schema_ventas=DataFrameSchema({
    "id_pedido":Column(float,Check.greater_than(0)),#los id de los pedidos deben ser mayores a 0
    "fecha_pedido":Column(str,Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),#las fechas deben estar en formato yyyy-mm-dd
    "rut_cliente":Column(str,Check.str_matches(r"^\d{6,8}-[0-9kK]$")),#como debe  ser el formato de rut 
    "nombre_cliente":Column(str,Check.str_length(1,100)),#como debe ser el nombre del cliente, entre 1 y 100 caracteres
    "region":Column(str,Check.str_length(1,100),nullable=True),
    "producto":Column(str,Check.str_length(1,100)),
    "categoria":Column(str,Check.str_length(1,100)),
    "cantidad":Column(float,Check.greater_than(0)),
    "precio_unitario":Column(float,Check.greater_than(0)),
    "descuento_pct":Column(float,Check.in_range(0,100)),
    "fecha_despacho":Column(str,Check.str_matches(r"^\d{4}-\d{2}-\d{2}$"),nullable=True),
    "estado_pedido":Column(str,Check.isin(["pendiente","despachado","entregado","cancelado"])),
})

ESQUEMA={#creamos un diccionario con el nombre de la tabla y el esquema de validacion
    "ventas_datamart":schema_ventas
}

def validar(nombre,schema):#funcion que recibe el nombre de la tabla y el esquema de validacion
    ruta= f"data/procesado/{nombre}_clean.csv"
    if not os.path.exists(ruta):
        logging.error(f"Ruta no encontrada para el archivo {nombre}: {ruta}")
        return
    df = pd.read_csv(ruta, dtype={#realizamos la lectura del archivo csv y definimos el tipo de dato de cada columna
        'fecha_pedido': str, 'fecha_despacho': str, 'rut_cliente': str,
        'nombre_cliente': str, 'region': str, 'producto': str,
        'categoria': str, 'estado_pedido': str,
        'precio_unitario': float,
    })
    logging.info(f"=== Validando: {nombre} ({len(df)} filas) ===")#registramos en el log la cantidad de filas que tiene el archivo a validar

    validos   = []#metemos los registros validos en una lista
    invalidos = []#metemos los registros invalidos en otra lista

    # Validar fila por fila para separar válidos de inválidos
    for i, row in df.iterrows():#creamos un bucle que recorra cada fila del dataframe y la valide con el esquema de validacion
        fila = pd.DataFrame([row])#creamos un dataframe con la fila actual para poder validarla con el esquema de validacion
        fila['fecha_despacho'] = fila['fecha_despacho'].astype(object)#cambiamos el tipo de dato de la columna fecha_despacho a object para poder validarla con el esquema de validacion
        try:
            schema.validate(fila, lazy=True)
            validos.append(row)
        except pa.errors.SchemaErrors as e:
            row["error_validacion"] = str(e.failure_cases["failure_case"].values)
            invalidos.append(row)

    df_validos   = pd.DataFrame(validos)
    df_invalidos = pd.DataFrame(invalidos)

    df_validos.to_csv(f"data/validados/{nombre}_validados.csv",  index=False)
    df_invalidos.to_csv(f"data/error/{nombre}_error.csv",      index=False)

    logging.info(f"Válidos:   {len(df_validos)}")#registramos en el log la cantidad de registros validos
    logging.info(f"Inválidos: {len(df_invalidos)}")#registramos en el log la cantidad de registros invalidos<
if __name__ == "__main__":
    logging.info("====== ETAPA 3: VALIDACIÓN ======")
    inicio = datetime.now()
    for nombre, schema in ESQUEMA.items():
        validar(nombre, schema)
    logging.info(f"Tiempo: {datetime.now() - inicio}")
    logging.info("====== FIN ETAPA 3 ======")

def ejecutar_validacion():
    logging.info("====== ETAPA 3: VALIDACIÓN ======")
    inicio = datetime.now()
    for nombre, schema in ESQUEMA.items():
        validar(nombre, schema)
    logging.info(f"Tiempo: {datetime.now() - inicio}")
    logging.info("====== FIN ETAPA 3 ======")
