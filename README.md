# Examen — Gestión de Datos

Este proyecto contiene un pipeline sencillo para procesar el archivo de ventas y dejar los datos listos para cargar en una base de datos. Está diseñado para ser transparente y fácil de entender: copia de seguridad, limpieza, validación y carga.

Resumen rápido: desde la carpeta del proyecto ejecuta `python main.py`. El pipeline realizará las 4 etapas en ese orden: ingesta → limpieza → validación → carga.

## 1) Cómo ejecutar el pipeline

- Requisitos: Python 3.10+ y las dependencias en `requirements.txt`.

Instala dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta el pipeline (desde la raíz del repo):

```bash
python main.py
```

Qué hace cada etapa:
- Etapa 1 — Ingesta (`scrips/ingesta.py`): lee `data/raw/ventas_datamart.csv`, muestra información inicial y guarda una copia en `data/respaldo/`.
- Etapa 2 — Limpieza (`scrips/limpieza.py`): normaliza formatos (fechas, RUT, nombres), limpia precios y aplica reglas de negocio; guarda `data/procesado/ventas_datamart_clean.csv`.
- Etapa 3 — Validación (`scrips/validacion.py`): aplica un esquema con `pandera`, separando registros válidos en `data/validados/` y los inválidos en `data/error/`.
- Etapa 4 — Carga (`scrips/cargaBD.py`): crea la tabla si es necesario y carga los registros validados en la base de datos.

## 2) Base de datos elegida

- Actualmente el pipeline está configurado para usar MySQL vía SQLAlchemy y `mysql-connector-python`.
- Cadena de conexión por defecto (en `scrips/cargaBD.py`):

```
mysql+mysqlconnector://admin:Forta165@localhost/examen
```

Importante: esas credenciales están en el código solo para evaluación. Antes de usar en producción cambia a variables de entorno (por ejemplo `DATABASE_URL`) o usa un gestor de secretos.

## 3) Decisiones técnicas y por qué

- Separación por etapas para facilitar la depuración y el reprocesado.
- Limpieza:
  - Eliminamos duplicados y filas con `cantidad <= 0` o `descuento_pct > 100` porque violan reglas de negocio.
  - `precio_unitario` se normaliza quitando símbolos y separadores de miles antes de convertir a numérico.
  - `rut_cliente` se estandariza eliminando puntos/espacios y forzando el formato `cuerpo-dv`.
  - Fechas se unifican a `YYYY-MM-DD` usando `unificar_fecha`.
- Validación:
  - Usamos `pandera` para expresar las reglas (tipos, rangos y patrones) de forma legible y reproducible.
- Carga:
  - La implementación actual trunca y recarga la tabla por simplicidad. Si necesitas carga incremental, lo adaptamos.

## 4) Problemas comunes detectados en los datos

- Duplicados por `id_pedido` (se eliminan conservando la primera ocurrencia).
- Fechas en formatos mixtos o faltantes (se unifican o quedan como nulas).
- `cantidad` <= 0 o `descuento_pct` > 100 (filtrados en limpieza).
- Precios con símbolos o separadores de miles (se limpian antes de convertir).
- RUTs con distintos formatos (puntos, espacios, guiones) — se normalizan; las filas que no cumplan el patrón serán inválidas.
- `estado_pedido` fuera del conjunto permitido → marcadas como inválidas.

## Buenas prácticas

- No dejar credenciales en el código: usar variables de entorno.
- Añadir tests y ejemplos de entrada para facilitar validaciones automáticas.


