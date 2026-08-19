import argparse
import logging
from pathlib import Path
import pandas as pd
from pymarc import MARCReader

# Importación absoluta de la configuración
from config.mapeo import MAPEO_MARC

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extraer_valor_campo(registro, reglas):
    """
    Extrae y concatena la información de un registro MARC basándose en las reglas de mapeo.
    """
    valores_extraidos = []
    etiquetas = reglas.get("etiquetas", [])
    subcampos_req = reglas.get("subcampos", [])

    for etiqueta in etiquetas:
        # Extraer campos que coincidan con la etiqueta
        campos = registro.get_fields(etiqueta)
        
        for campo in campos:
            # Caso 1: Campos de control (ej. 001) que no tienen subcampos
            if campo.is_control_field():
                valores_extraidos.append(campo.data.strip())
                continue
            
            # Caso 2: Campos de datos (ej. 245, 260) que utilizan subcampos
            textos_subcampos = []
            for codigo_subcampo in subcampos_req:
                valores = campo.get_subfields(codigo_subcampo)
                if valores:
                    # Agrupamos todos los valores de un mismo subcampo (por si se repiten)
                    textos_subcampos.extend([v.strip() for v in valores])
            
            if textos_subcampos:
                valores_extraidos.append(" ".join(textos_subcampos))

    # Si hay múltiples valores (ej. varios autores en 700), los unimos con un separador claro
    if valores_extraidos:
        return " | ".join(valores_extraidos)
    return None

def ejecutar_transformacion(ruta_entrada: Path, ruta_salida: Path):
    """
    Lee un archivo MRC binario y lo transforma en un archivo tabular TSV.
    """
    if not ruta_entrada.exists():
        logging.error(f"El archivo fuente no existe: {ruta_entrada}")
        return

    datos_tabulares = []
    registros_procesados = 0

    logging.info(f"Iniciando extracción desde {ruta_entrada}...")

    with open(ruta_entrada, 'rb') as f:
        lector = MARCReader(f)
        for registro in lector:
            if registro is None:
                continue
            
            fila_actual = {}
            for columna, reglas in MAPEO_MARC.items():
                fila_actual[columna] = extraer_valor_campo(registro, reglas)
            
            datos_tabulares.append(fila_actual)
            registros_procesados += 1

    logging.info(f"Extracción completada. {registros_procesados} registros procesados.")

    # Convertir a DataFrame y exportar
    df = pd.DataFrame(datos_tabulares)
    
    # Crear el directorio de salida si no existe
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Exportando datos a {ruta_salida}...")
    # Se utiliza delimitador tabular y se evita indexar las filas
    df.to_csv(ruta_salida, sep='\t', index=False, encoding='utf-8')
    logging.info("Transformación finalizada exitosamente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transformación de datos MARC a formato tabular (TSV).")
    parser.add_argument(
        '--input', 
        type=str, 
        required=True, 
        help="Ruta al archivo .mrc de entrada (ej: data/raw/registros_bnmm.mrc)"
    )
    parser.add_argument(
        '--output', 
        type=str, 
        required=True, 
        help="Ruta al archivo .tsv de salida (ej: data/interim/registros_bnmm.tsv)"
    )
    
    args = parser.parse_args()
    
    ruta_in = Path(args.input)
    ruta_out = Path(args.output)
    
    ejecutar_transformacion(ruta_in, ruta_out)