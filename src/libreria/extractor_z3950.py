import subprocess
import re
from typing import Set
from src.libreria.extractor_base import ExtractorBase

class ExtractorZ3950(ExtractorBase):
    """
    Implementación concreta del ExtractorBase para el protocolo Z39.50.
    Utiliza el cliente CLI yaz-client para interactuar con los servidores.
    """
    
    def __init__(self, config_institucion: dict):
        super().__init__(config_institucion)
        
    def extraer_ids(self, ruta_fuente: str) -> Set[str]:
        ids_extraidos = set()
        estrategia = self.config.get('estrategia_extraccion', 'directa')
        
        try:
            with open(ruta_fuente, 'r', encoding='utf-8') as f:
                if estrategia == 'regex':
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
            return True
            
        host = self.config['parametros_red']['host']
        credenciales = self.config['parametros_red'].get('credenciales', '')
        formato = self.config['parametros_busqueda'].get('formato_salida', 'usmarc')
        atributo = self.config['parametros_busqueda'].get('atributo_id', '12')
        
        comandos = f"format {formato}\nset_marcdump {ruta_destino}\n"
        for doc_id in ids:
            comandos += f"find @attr 1={atributo} {doc_id}\nshow 1\n"
        comandos += "quit\n"
        
        comando_cli = ["yaz-client", host]
        if credenciales:
            partes_cred = credenciales.split(' ')
            comando_cli.extend(partes_cred)
            
        try:
            subprocess.run(
                comando_cli,
                input=comandos.encode('utf-8'),
                capture_output=True,
                check=True
            )
            return True
        except FileNotFoundError:
            print("🛑 Error: No se encontró el binario 'yaz-client'.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"🛑 Error de ejecución en yaz-client. Salida:\n{e.stderr.decode('utf-8', errors='ignore')}")
            return False

    def obtener_cantidad_hits(self, consulta_pqf: str) -> int:
        """
        Ejecuta una consulta libre para averiguar la cantidad de registros coincidentes (hits)
        sin descargar los registros, ideal para dimensionar volcados masivos.
        """
        host = self.config['parametros_red']['host']
        credenciales = self.config['parametros_red'].get('credenciales', '')
        
        comando_base = ["yaz-client", host]
        if credenciales:
            comando_base.extend(credenciales.split(' '))

        comando_conteo = f"find {consulta_pqf}\nquit\n"
        
        try:
            resultado = subprocess.run(
                comando_base,
                input=comando_conteo.encode('utf-8'),
                capture_output=True,
                check=True
            )
            salida_texto = resultado.stdout.decode('utf-8', errors='ignore')
            
            for linea in salida_texto.split('\n'):
                if 'Number of hits' in linea:
                    match = re.search(r'Number of hits:\s*(\d+)', linea)
                    if match:
                        return int(match.group(1))
            return 0
            
        except FileNotFoundError:
            print("🛑 Error: No se encontró el binario 'yaz-client'.")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"🛑 Error al consultar hits: {e.stderr.decode('utf-8', errors='ignore')}")
            return 0

    def descargar_por_consulta(self, consulta_pqf: str, ruta_destino: str, cantidad: int) -> bool:
        """
        Descarga un bloque de registros utilizando una consulta PQF estructurada.
        Requiere el número exacto de registros a extraer para optimizar el comando 'show'.
        """
        if cantidad <= 0:
            print("⚠️ Advertencia: La cantidad de registros a descargar es 0.")
            return False

        host = self.config['parametros_red']['host']
        credenciales = self.config['parametros_red'].get('credenciales', '')
        formato = self.config['parametros_busqueda'].get('formato_salida', 'usmarc')
        
        comandos = (
            f"format {formato}\n"
            f"set_marcdump {ruta_destino}\n"
            f"find {consulta_pqf}\n"
            f"show 1+{cantidad}\n"
            f"quit\n"
        )
        
        comando_cli = ["yaz-client", host]
        if credenciales:
            comando_cli.extend(credenciales.split(' '))
            
        try:
            subprocess.run(
                comando_cli,
                input=comandos.encode('utf-8'),
                capture_output=True,
                check=True
            )
            return True
        except FileNotFoundError:
            print("🛑 Error: No se encontró el binario 'yaz-client'.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"🛑 Error en la descarga por consulta. Salida:\n{e.stderr.decode('utf-8', errors='ignore')}")
            return False