import pandas as pd
import sqlalchemy
import logging
import os
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/carga.log"),
        logging.StreamHandler()
    ]
)

engine = sqlalchemy.create_engine(
    "mysql+mysqlconnector://admin:Forta165@localhost/examen"
)

def crear_tablas():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS ventas_datamart (
                id_pedido        FLOAT         PRIMARY KEY,
                fecha_pedido     DATE,
                rut_cliente      VARCHAR(15),
                nombre_cliente   VARCHAR(100),
                region           VARCHAR(100),
                producto         VARCHAR(100),
                categoria        VARCHAR(50),
                cantidad         FLOAT,
                precio_unitario  DECIMAL(10,2),
                descuento_pct    FLOAT,
                estado_pedido    VARCHAR(30),
                fecha_despacho   DATE
            )
        """))
        logging.info("Tablas creadas correctamente")

def limpiar_tablas():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE ventas_datamart"))
        logging.info("Tablas limpiadas correctamente")

TABLAS = [
    ("ventas_datamart", "data/validados/ventas_datamart_validados.csv"),
]

def cargar_tabla(nombre, ruta):
    if not os.path.exists(ruta):
        logging.error(f"No existe: {ruta}")
        return

    df = pd.read_csv(ruta, dtype={
        'rut_cliente': str, 'nombre_cliente': str, 'region': str,
        'producto': str, 'categoria': str, 'estado_pedido': str,
        'fecha_pedido': str, 'fecha_despacho': str,
        'precio_unitario': float,
    })

    # convertir fechas
    for col in ['fecha_pedido', 'fecha_despacho']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].where(df[col].notna(), other=None)

    # eliminar duplicados por PK
    antes = len(df)
    df = df.drop_duplicates(subset=['id_pedido'], keep='first')
    logging.info(f"Duplicados eliminados: {antes - len(df)}")

    logging.info(f"Cargando {nombre}: {len(df)} filas")

    with engine.begin() as conn:
        try:
            df.to_sql(nombre, conn, if_exists="append", index=False)
            logging.info(f"✓ Commit exitoso: {nombre}")
        except Exception as e:
            logging.error(f"✗ Rollback en {nombre}: {e}")
            raise

def verificar():
    logging.info("=== Verificación SQL ===")
    with engine.connect() as conn:
        total = conn.execute(
            sqlalchemy.text("SELECT COUNT(*) FROM ventas_datamart")
        ).scalar()
        logging.info(f"ventas_datamart: {total} registros cargados")

        df_check = pd.read_sql(sqlalchemy.text("""
            SELECT id_pedido, nombre_cliente, producto, precio_unitario, estado_pedido
            FROM ventas_datamart
            LIMIT 5
        """), conn)
        logging.info(f"Muestra:\n{df_check.to_string()}")

def ejecutar_carga():
    logging.info("====== ETAPA 4: CARGA ======")
    inicio = datetime.now()
    crear_tablas()
    limpiar_tablas()
    for nombre, ruta in TABLAS:
        cargar_tabla(nombre, ruta)
    verificar()
    logging.info(f"Tiempo total: {datetime.now() - inicio}")
    logging.info("====== FIN ETAPA 4 ======")

if __name__ == "__main__":
    ejecutar_carga()