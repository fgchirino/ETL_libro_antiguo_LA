import re
import pandas as pd
from pymarc import MARCReader, MARCWriter

def parsear_pie_imprenta(cadena: str):
    """
    Desensambla la cadena de pie de imprenta (ISBD) en sus tres componentes.
    Espera formatos similares a: "Lugar : Editorial, Año" o variaciones con corchetes.
    """
    if pd.isna(cadena) or not isinstance(cadena, str):
        return pd.Series({"lugar_publicacion": None, "editorial": None, "anio_publicacion": None})

    # Limpieza inicial de corchetes comunes en catalogación
    cadena_limpia = cadena.replace('[', '').replace(']', '').strip()
    
    lugar = None
    editorial = None
    anio = None

    # Extracción del año (buscamos 4 dígitos consecutivos al final o cerca del final)
    match_anio = re.search(r'(\d{4})', cadena_limpia)
    if match_anio:
        anio = match_anio.group(1)

    # Separación de lugar y editorial por los dos puntos ISBD
    partes = cadena_limpia.split(':')
    if len(partes) >= 2:
        lugar = partes[0].strip()
        # La editorial es lo que sigue a los dos puntos, quitando la coma y el año
        resto = partes[1].split(',')[0].strip()
        editorial = resto
    else:
        # Fallback si no hay estructura ISBD clara
        lugar = cadena_limpia

    return pd.Series({
        "lugar_publicacion": lugar,
        "editorial": editorial,
        "anio_publicacion": anio
    })

def filtrar_mrc_por_condicion(ruta_entrada: str, ruta_salida: str, etiqueta: str, subcampo: str, valor_exacto: str) -> int:
    """
    Filtra un archivo MARC binario (.mrc), iterándolo y escribiendo en un nuevo archivo
    únicamente los registros que cumplan con una coincidencia exacta en el campo/subcampo indicado.
    
    Retorna la cantidad de registros que superaron el filtro y fueron escritos.
    """
    registros_retenidos = 0
    
    with open(ruta_entrada, 'rb') as f_in, open(ruta_salida, 'wb') as f_out:
        lector = MARCReader(f_in)
        escritor = MARCWriter(f_out)
        
        for registro in lector:
            if registro is None:
                continue
            
            es_coincidencia = False
            campos = registro.get_fields(etiqueta)
            
            for campo in campos:
                # Caso A: Es un campo de control (ej. 001) que no tiene subcampos
                if campo.is_control_field():
                    if campo.data.strip() == valor_exacto:
                        es_coincidencia = True
                        break
                # Caso B: Es un campo de datos estándar
                else:
                    valores_subcampo = campo.get_subfields(subcampo)
                    # Comparamos quitando espacios residuales en los extremos
                    if valores_subcampo and valor_exacto in [v.strip() for v in valores_subcampo]:
                        es_coincidencia = True
                        break
                        
            if es_coincidencia:
                escritor.write(registro)
                registros_retenidos += 1
                
    return registros_retenidos