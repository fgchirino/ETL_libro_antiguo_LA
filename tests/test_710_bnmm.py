import os
import subprocess
import re
from pymarc import MARCReader
from config.instituciones import CONFIG_INSTITUCIONES

def contar_registros_exactos():
    termino_busqueda = "Librería del Colegio de la Compañía de Jesús de Buenos Aires"
    # Búsqueda amplia por palabra clave para maximizar la captura inicial
    consulta_pqf = f'@attr 1=1016 "{termino_busqueda}"'
    archivo_salida = "data/raw/test_jesuitas_bnmm_completo.mrc"
    
    config_bnmm = CONFIG_INSTITUCIONES['bnmm']
    host = config_bnmm['parametros_red']['host']
    credenciales = config_bnmm['parametros_red'].get('credenciales', '')
    formato = config_bnmm['parametros_busqueda'].get('formato_salida', 'usmarc')
    
    comando_base = ["yaz-client", host]
    if credenciales:
        comando_base.extend(credenciales.split(' '))

    # Fase 1: Averiguar el número total de hits
    print(f"Fase 1: Consultando volumen total para '{termino_busqueda}'...")
    comando_conteo = f"find {consulta_pqf}\nquit\n"
    
    try:
        resultado_conteo = subprocess.run(
            comando_base,
            input=comando_conteo.encode('utf-8'),
            capture_output=True,
            check=True
        )
        salida_texto = resultado_conteo.stdout.decode('utf-8', errors='ignore')
        
        total_hits = 0
        for linea in salida_texto.split('\n'):
            if 'Number of hits' in linea:
                match = re.search(r'Number of hits:\s*(\d+)', linea)
                if match:
                    total_hits = int(match.group(1))
                    break
                    
        print(f"  -> Hits reportados por el servidor: {total_hits}")
        
        if total_hits == 0:
            print("No se encontraron registros en el servidor.")
            return

    except subprocess.CalledProcessError as e:
        print(f"🛑 Error al consultar hits: {e.stderr.decode('utf-8', errors='ignore')}")
        return

    # Fase 2: Descarga total
    print(f"\nFase 2: Descargando los {total_hits} registros...")
    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)

    comando_descarga = (
        f"format {formato}\n"
        f"set_marcdump {archivo_salida}\n"
        f"find {consulta_pqf}\n"
        f"show 1+{total_hits}\n"
        f"quit\n"
    )
    
    try:
        subprocess.run(
            comando_base,
            input=comando_descarga.encode('utf-8'),
            capture_output=True,
            check=True
        )
        print("  -> Descarga completada.")
    except subprocess.CalledProcessError as e:
        print(f"🛑 Error en la descarga: {e.stderr.decode('utf-8', errors='ignore')}")
        return

    # Fase 3: Conteo estricto con PyMARC
    print("\nFase 3: Validando coincidencia exacta en el subcampo 710$a...")
    registros_totales = 0
    registros_coincidentes = 0

    with open(archivo_salida, 'rb') as f:
        reader = MARCReader(f)
        for record in reader:
            if record is None:
                continue
            
            registros_totales += 1
            campos_710 = record.get_fields('710')
            
            es_coincidencia_exacta = False
            for campo in campos_710:
                subcampo_a = campo.get_subfields('a')
                if subcampo_a and termino_busqueda in subcampo_a:
                    es_coincidencia_exacta = True
                    break
                    
            if es_coincidencia_exacta:
                registros_coincidentes += 1

    print("\n--- Resultados Finales ---")
    print(f"Registros analizados localmente: {registros_totales}")
    print(f"Registros con coincidencia EXACTA en 710$a: {registros_coincidentes}")

if __name__ == "__main__":
    contar_registros_exactos()