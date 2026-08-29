import os
import sys
import json
import glob
import re
import io
import pandas as pd
import pymarc
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.mapeo import MAPEO_MARC, MAPEO_AUTORIDADES, MAPEO_CONCEPTOS, MAPEO_LOD

DIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
DIR_RAW = os.path.join(DIR_BASE, 'raw')
DIR_INTERIM = os.path.join(DIR_BASE, 'interim')
DIR_PROCESADA = os.path.join(DIR_BASE, 'procesada')

# --- FUNCIONES UTILITARIAS ---

def cargar_json_memoria(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_json_memoria(ruta, datos):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def obtener_subcampos_dict(field, split_char=None):
    """Extrae subcampos y aplica división dinámica y agnóstica si está configurado."""
    sub_dict = {}
    subfields_raw = []
    
    if hasattr(field, 'subfields_as_dict'):
        dict_crudo = field.subfields_as_dict()
        for k, v in dict_crudo.items():
            if isinstance(v, list):
                for item in v:
                    subfields_raw.append((k, item))
            else:
                subfields_raw.append((k, v))
    else:
        try:
            for sf in field.subfields:
                subfields_raw.append((sf.code, sf.value))
        except AttributeError:
            for i in range(0, len(field.subfields), 2):
                subfields_raw.append((field.subfields[i], field.subfields[i+1]))
    
    for code, value in subfields_raw:
        # Fragmentación puramente Data-Driven
        if split_char and isinstance(value, str) and split_char in value:
            fragmentos = [p.strip() for p in value.split(split_char) if p.strip()]
        else:
            fragmentos = [value]
            
        for frag in fragmentos:
            if code in sub_dict:
                if isinstance(sub_dict[code], list):
                    sub_dict[code].append(frag)
                else:
                    sub_dict[code] = [sub_dict[code], frag]
            else:
                sub_dict[code] = frag
                
    return sub_dict

def construir_indice_inverso(grafo):
    return {nodo['cadena_limpia']: id_nodo for id_nodo, nodo in grafo.items()}

# --- NÚCLEO DE EXTRACCIÓN ONTOLÓGICA ---

def extraer_grafo_registro(record, institucion, grafos, indices):
    f001 = record['001'].data if '001' in record else None
    if not f001: return False
    
    id_manifestacion = f"{institucion}_{f001}"
    
    nodo_manif = {
        'ID_Manifestacion': id_manifestacion,
        'Fuente_Origen': institucion.upper(),
        'ID_Catalogo': f001,
        'autoridades_vinculadas': [],
        'conceptos_vinculados': []
    }
    
    etiquetas_relacionales = list(MAPEO_AUTORIDADES.keys()) + list(MAPEO_CONCEPTOS.keys())

    for col_name, config in MAPEO_MARC.items():
        if col_name == 'id_control': continue
        
        nodos_extraidos = []
        subcampos_req = config.get('subcampos', [])
        
        for etq in config.get('etiquetas', []):
            if etq in etiquetas_relacionales:
                continue

            for field in record.get_fields(etq):
                if field.is_control_field():
                    nodos_extraidos.append(field.data)
                else:
                    sub_dict = obtener_subcampos_dict(field)
                    if subcampos_req == ['*']:
                        nodos_extraidos.append({'etiqueta': etq, 'subcampos': sub_dict})
                    else:
                        filtrado = {k: v for k, v in sub_dict.items() if k in subcampos_req}
                        if filtrado:
                            nodos_extraidos.append({'etiqueta': etq, 'subcampos': filtrado})
                            
        if nodos_extraidos:
            nodo_manif[col_name] = nodos_extraidos

    for etq, reglas in MAPEO_LOD.items():
        for field in record.get_fields(etq):
            for sub_a in field.get_subfields('a'):
                for regla in reglas:
                    prefijo = regla['prefijo_origen']
                    if sub_a.startswith(prefijo):
                        id_limpio = sub_a.replace(prefijo, '').strip()
                        nodo_manif[regla['columna_destino']] = f"{regla['uri_base']}{id_limpio}"

    def procesar_entidad(diccionario_mapeo, target_grafo, prefijo_id, lista_vinculos, indice_inverso, es_autoridad=False):
        for etq, config in diccionario_mapeo.items():
            
            # Evaluación Data-Driven del archivo de configuración
            if isinstance(config, dict):
                tipo_entidad = config.get('entidad', 'Desconocido')
                split_char = config.get('split_caracter', None)
            else:
                tipo_entidad = config
                split_char = None

            for field in record.get_fields(etq):
                cadena = field.value()
                if not cadena: continue
                cadena = cadena.strip()
                
                if cadena in indice_inverso:
                    id_entidad = indice_inverso[cadena]
                    grafos[target_grafo][id_entidad]['frecuencia'] += 1
                else:
                    id_entidad = f"{prefijo_id}_{str(len(grafos[target_grafo]) + 1).zfill(5)}"
                    
                    # Extracción parametrizada
                    subcampos_procesados = obtener_subcampos_dict(field, split_char=split_char)
                    
                    nuevo_nodo = {
                        "cadena_limpia": cadena,
                        "tipo_entidad": tipo_entidad,
                        "etiqueta_origen": etq,
                        "subcampos": subcampos_procesados,
                        "frecuencia": 1
                    }
                    if es_autoridad: nuevo_nodo["sameAs"] = {"viaf": None, "wikidata": None}
                    
                    grafos[target_grafo][id_entidad] = nuevo_nodo
                    indice_inverso[cadena] = id_entidad

                if id_entidad not in nodo_manif[lista_vinculos]:
                    nodo_manif[lista_vinculos].append(id_entidad)

    procesar_entidad(MAPEO_AUTORIDADES, 'autoridades', 'aut', 'autoridades_vinculadas', indices['autoridades'], True)
    procesar_entidad(MAPEO_CONCEPTOS, 'conceptos', 'cnc', 'conceptos_vinculados', indices['conceptos'], False)

    grafos['manifestaciones'][id_manifestacion] = nodo_manif
    return True

# --- GENERADOR DE VISTA TABULAR (SUBPRODUCTO) ---

def generar_vista_tabular(dict_manifestaciones, ruta_salida):
    filas = []
    for id_manif, nodo in dict_manifestaciones.items():
        fila_plana = {'ID_Manifestacion': nodo.get('ID_Manifestacion'), 'Fuente_Origen': nodo.get('Fuente_Origen')}
        
        if 'uri_oclc' in nodo: fila_plana['uri_oclc'] = nodo['uri_oclc']
        if 'uri_bne' in nodo: fila_plana['uri_bne'] = nodo['uri_bne']
        
        for col_name in MAPEO_MARC.keys():
            if col_name == 'id_control': continue
            datos_nodo = nodo.get(col_name, [])
            valores_planos = []
            for item in datos_nodo:
                if isinstance(item, str):
                    valores_planos.append(item)
                elif isinstance(item, dict) and 'subcampos' in item:
                    sub_vals = []
                    for v in item['subcampos'].values():
                        if isinstance(v, list):
                            sub_vals.extend([str(x) for x in v])
                        else:
                            sub_vals.append(str(v))
                    valores_planos.append(" ".join(sub_vals).strip())
            
            if valores_planos: fila_plana[col_name] = " | ".join(valores_planos)

        if nodo.get('autoridades_vinculadas'):
            fila_plana['Autoridades_IDs'] = " | ".join(nodo['autoridades_vinculadas'])
        if nodo.get('conceptos_vinculados'):
            fila_plana['Conceptos_IDs'] = " | ".join(nodo['conceptos_vinculados'])
                
        filas.append(fila_plana)
        
    df = pd.DataFrame(filas)
    df.to_csv(ruta_salida, sep='\t', index=False, encoding='utf-8')
    return len(df)

# --- ORQUESTADOR PRINCIPAL ---

def procesar_archivos():
    print("\n--- INICIANDO TRANSFORMACIÓN ONTOLÓGICA (FASE 2) ---")
    
    ruta_manifiesto = os.path.join(DIR_INTERIM, 'estado_transformacion.json')
    estado = cargar_json_memoria(ruta_manifiesto)
    archivos_procesados = estado.get('archivos', [])
    
    grafos = {
        'manifestaciones': cargar_json_memoria(os.path.join(DIR_PROCESADA, 'manifestaciones.json')),
        'autoridades': cargar_json_memoria(os.path.join(DIR_PROCESADA, 'autoridades.json')),
        'conceptos': cargar_json_memoria(os.path.join(DIR_PROCESADA, 'conceptos.json'))
    }

    indices = {
        'autoridades': construir_indice_inverso(grafos['autoridades']),
        'conceptos': construir_indice_inverso(grafos['conceptos'])
    }
    
    archivos_crudos = glob.glob(os.path.join(DIR_RAW, '*.mrc')) + glob.glob(os.path.join(DIR_RAW, '*.xml'))
    archivos_pendientes = [f for f in archivos_crudos if os.path.basename(f) not in archivos_procesados]
    
    if not archivos_pendientes:
        print("✅ No hay archivos nuevos para procesar. Los grafos están al día.")
        return

    print(f"🔎 Procesando {len(archivos_pendientes)} archivos crudos (Deltas)...")
    
    for archivo in archivos_pendientes:
        nombre_base = os.path.basename(archivo)
        match_inst = re.search(r'^(?:registros_)?([a-zA-Z0-9]+)', nombre_base, re.IGNORECASE)
        institucion = match_inst.group(1).lower() if match_inst else 'desconocido'
        registros_procesados = 0
        
        try:
            if archivo.endswith('.mrc'):
                with open(archivo, 'rb') as f:
                    reader = pymarc.MARCReader(f)
                    for record in reader:
                        if record and extraer_grafo_registro(record, institucion, grafos, indices):
                            registros_procesados += 1
                            
            elif archivo.endswith('.xml'):
                tree = ET.parse(archivo)
                root = tree.getroot()
                for elem in root.iter():
                    if elem.tag.endswith('record'):
                        es_marc_real = any('leader' in child.tag or 'controlfield' in child.tag for child in elem)
                        if es_marc_real:
                            xml_raw = ET.tostring(elem, encoding='unicode')
                            xml_str = f'<?xml version="1.0" encoding="UTF-8"?><collection xmlns="http://www.loc.gov/MARC21/slim">{xml_raw}</collection>'
                            pymarc_records = pymarc.parse_xml_to_array(io.BytesIO(xml_str.encode('utf-8')))
                            for record in pymarc_records:
                                if record and extraer_grafo_registro(record, institucion, grafos, indices):
                                    registros_procesados += 1
                            
            archivos_procesados.append(nombre_base)
            print(f"  -> Transformado: {nombre_base} ({registros_procesados} manifiestos extraídos)")
            
        except Exception as e:
            print(f"🛑 Error procesando {nombre_base}: {e}")

    guardar_json_memoria(os.path.join(DIR_PROCESADA, 'manifestaciones.json'), grafos['manifestaciones'])
    guardar_json_memoria(os.path.join(DIR_PROCESADA, 'autoridades.json'), grafos['autoridades'])
    guardar_json_memoria(os.path.join(DIR_PROCESADA, 'conceptos.json'), grafos['conceptos'])
    
    ruta_tsv = os.path.join(DIR_PROCESADA, 'manifestaciones_analitica.tsv')
    generar_vista_tabular(grafos['manifestaciones'], ruta_tsv)
    guardar_json_memoria(ruta_manifiesto, {'archivos': archivos_procesados})
    
    print("\n🎉 Transformación completada exitosamente.")
    print(f"📚 Manifestaciones consolidadas: {len(grafos['manifestaciones'])}")
    print(f"👤 Autoridades aisladas: {len(grafos['autoridades'])}")
    print(f"🧠 Conceptos temáticos aislados: {len(grafos['conceptos'])}")

if __name__ == "__main__":
    procesar_archivos()