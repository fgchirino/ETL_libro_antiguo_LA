import urllib.parse
from typing import Set
import requests
import xml.etree.ElementTree as ET

from src.libreria.extractor_base import ExtractorBase

class ExtractorSRU(ExtractorBase):
    """
    Implementación concreta del ExtractorBase para el protocolo SRU/HTTP.
    Utiliza consultas RESTful para interactuar con sistemas bibliotecarios modernos.
    """
    
    def __init__(self, config_institucion: dict):
        super().__init__(config_institucion)
        # Headers de cortesía para evitar bloqueos por parte del servidor
        self.headers = {
            'User-Agent': 'Bot-Extraccion-Academica/1.0 (Proyecto Investigacion LOD)'
        }
        
    def extraer_ids(self, ruta_fuente: str) -> Set[str]:
        ids_extraidos = set()
        estrategia = self.config.get('estrategia_extraccion', 'directa')
        
        try:
            with open(ruta_fuente, 'r', encoding='utf-8') as f:
                if estrategia == 'regex':
                    import re
                    patron_regex = self.config.get('parseo_entrada', {}).get('regex_id')
                    if not patron_regex:
                        print("🛑 Error: Estrategia 'regex' definida pero no hay patrón en la configuración.")
                        return ids_extraidos
                        
                    patron = re.compile(patron_regex)
                    for linea in f:
                        coincidencias = patron.findall(linea)
                        for coincidencia in coincidencias:
                            ids_extraidos.add(coincidencia)
                            
                elif estrategia == 'directa':
                    for linea in f:
                        id_limpio = linea.strip()
                        if id_limpio:
                            ids_extraidos.add(id_limpio)
                            
                else:
                    print(f"🛑 Error: Estrategia de extracción '{estrategia}' no soportada.")
                    
        except FileNotFoundError:
            print(f"🛑 Error: Archivo fuente '{ruta_fuente}' no encontrado.")
            
        return ids_extraidos

    def descargar_registros(self, ids: Set[str], ruta_destino: str) -> bool:
        if not ids:
            print("⚠️ Advertencia: No hay IDs para descargar.")
            return True

        host = self.config['parametros_red']['host']
        params_busqueda = self.config['parametros_busqueda']
        version = params_busqueda.get('version', '1.2')
        schema = params_busqueda.get('recordSchema', 'marcxml')
        indice = params_busqueda.get('indice_busqueda', 'alma.mms_id')

        try:
            with open(ruta_destino, 'w', encoding='utf-8') as f_out:
                # 1. Escribir cabecera estándar XML y contenedor MARCXML
                f_out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f_out.write('<collection xmlns="http://www.loc.gov/MARC21/slim">\n')

                # 2. Iterar e inyectar registros dinámicamente
                total = len(ids)
                print(f"  -> Iniciando descarga SRU de {total} registros...")
                
                for i, doc_id in enumerate(ids, 1):
                    cql_query = f'{indice}="{doc_id}"'
                    cql_encoded = urllib.parse.quote(cql_query)
                    
                    url = f"{host}?operation=searchRetrieve&version={version}&query={cql_encoded}&recordSchema={schema}&maximumRecords=1"
                    
                    try:
                        res = requests.get(url, headers=self.headers, timeout=15)
                        if res.status_code == 200:
                            # Parseo estructural nativo
                            try:
                                root = ET.fromstring(res.text)
                                registro_extraido = False
                                
                                # Buscamos el nodo recordData (ignorando prefijos de namespace de SRU)
                                for elem in root.iter():
                                    if elem.tag.endswith('recordData'):
                                        # El verdadero registro MARCXML es el hijo de recordData
                                        if len(elem) > 0:
                                            marc_record = elem[0]
                                            xml_raw = ET.tostring(marc_record, encoding='unicode')
                                            f_out.write(xml_raw + '\n')
                                            registro_extraido = True
                                        break # Solo necesitamos uno
                                
                                if registro_extraido:
                                    print(f"     ✅ [{i}/{total}] ID {doc_id} procesado.", end='\r')
                                else:
                                    print(f"\n     ⚠️ [{i}/{total}] ID {doc_id}: Descargado, pero <recordData> está vacío o no se encontró.")
                            
                            except ET.ParseError as pe:
                                print(f"\n     🛑 [{i}/{total}] ID {doc_id}: La API devolvió un XML corrupto ({pe}).")
                                
                        else:
                            print(f"\n     🛑 [{i}/{total}] ID {doc_id}: Error HTTP {res.status_code}.")
                            
                    except requests.RequestException as e:
                        print(f"\n     🛑 [{i}/{total}] ID {doc_id}: Fallo de conexión ({e}).")

                # 3. Cerrar colección XML
                f_out.write('</collection>\n')
                print("\n  -> Descarga SRU finalizada con éxito.")
            return True

        except Exception as e:
            print(f"🛑 Error crítico escribiendo el archivo {ruta_destino}: {e}")
            return False