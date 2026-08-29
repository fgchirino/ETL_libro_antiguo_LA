import argparse
import sys
import os
import json
from datetime import datetime

# Ajuste temporal del path para permitir importaciones absolutas desde la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.instituciones import CONFIG_INSTITUCIONES
from src.libreria.extractor_z3950 import ExtractorZ3950
from src.libreria.extractor_sru import ExtractorSRU

# Patrón Factory: Mapeo de strings de configuración a Clases reales
MAPEO_EXTRACTORES = {
    'Z3950': ExtractorZ3950,
    'SRU': ExtractorSRU
}

def cargar_manifiesto(ruta: str) -> dict:
    """Lee el historial de IDs extraídos; si no existe, devuelve un diccionario vacío."""
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_manifiesto(ruta: str, datos: dict):
    """Sobreescribe el JSON histórico con la lista actualizada de IDs."""
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL - Fase 1: Extracción Incremental")
    parser.add_argument(
        "--institucion", 
        type=str, 
        required=True, 
        help="Clave de la institución a ingestar (ej. bnmm, bne)"
    )
    
    args = parser.parse_args()
    institucion = args.institucion.lower()
    
    # 1. Validación de la configuración
    if institucion not in CONFIG_INSTITUCIONES:
        print(f"🛑 Error: La institución '{institucion}' no está definida en config/instituciones.py")
        sys.exit(1)
        
    config = CONFIG_INSTITUCIONES[institucion]
    tipo_extractor = config.get('tipo_extractor')
    
    if tipo_extractor not in MAPEO_EXTRACTORES:
        print(f"🛑 Error: Tipo de extractor '{tipo_extractor}' no soportado en la fábrica.")
        sys.exit(1)
        
    # 2. Definición de rutas jerárquicas y Timestamp
    ruta_base_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    ruta_base_data = os.path.join(ruta_base_proyecto, 'data')
    ruta_raw = os.path.join(ruta_base_data, 'raw')
    
    nombre_archivo_origen = config.get('archivo_origen')
    if not nombre_archivo_origen:
        print(f"🛑 Error: No se ha definido 'archivo_origen' para {institucion}.")
        sys.exit(1)
        
    ruta_fuente = os.path.join(ruta_raw, nombre_archivo_origen)
    ruta_manifiesto = os.path.join(ruta_base_data, 'historial_descargas.json')
    
    # Generación de la ruta de salida inmutable (Delta)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = config.get('parametros_busqueda', {}).get('extension_salida', '.dat')
    ruta_destino = os.path.join(ruta_raw, f"registros_{institucion}_{timestamp}{ext}")
    
    print(f"🚀 Iniciando proceso de ingesta para: {institucion.upper()}")
    
    # 3. Instanciación dinámica del motor de extracción
    clase_extractor = MAPEO_EXTRACTORES[tipo_extractor]
    extractor = clase_extractor(config)
    
    # 4. Extracción de IDs fuente
    print(f"🔎 Analizando archivo fuente: {ruta_fuente}...")
    ids_esperados = extractor.extraer_ids(ruta_fuente)
    
    if not ids_esperados:
        print("⚠️ No se encontraron IDs válidos en el archivo fuente. Abortando.")
        sys.exit(0)
        
    # 5. Lógica Incremental
    manifiesto = cargar_manifiesto(ruta_manifiesto)
    ids_historicos = set(manifiesto.get(institucion, []))
    ids_nuevos = ids_esperados - ids_historicos
    
    print(f"📊 Estadísticas de extracción:")
    print(f"   - IDs totales en origen: {len(ids_esperados)}")
    print(f"   - IDs históricos (ya descargados): {len(ids_historicos)}")
    print(f"   - IDs NUEVOS a procesar: {len(ids_nuevos)}")
    
    if not ids_nuevos:
        print("✅ Todo al día. No hay registros nuevos para descargar.")
        sys.exit(0)
        
    # 6. Descarga de registros
    print(f"📡 Conectando al servidor {tipo_extractor} y descargando lote incremental...")
    exito = extractor.descargar_registros(ids_nuevos, ruta_destino)
    
    # 7. Actualización persistente del manifiesto
    if exito:
        # Unión de conjuntos y conversión a lista para serializar a JSON
        manifiesto[institucion] = list(ids_historicos.union(ids_nuevos))
        guardar_manifiesto(ruta_manifiesto, manifiesto)
        print(f"🎉 Descarga completada. Registros guardados en: {ruta_destino}")
        print(f"📝 Manifiesto incremental actualizado en: {ruta_manifiesto}")
    else:
        print("🛑 Ocurrió un error durante la descarga remota.")
        sys.exit(1)

if __name__ == "__main__":
    main()