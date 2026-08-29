import os
import pandas as pd

# Rutas asumiendo ejecución desde la raíz del proyecto
DIR_RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/raw'))

ARCHIVOS_A_NORMALIZAR = [
    'materialidad_huellas.tsv',
    'materialidad_items.tsv',
    'tabla_puente.tsv'
]

def normalizar_id_sistema(val):
    if pd.isna(val):
        return val
        
    val_str = str(val).strip()
    if not val_str:
        return val
    
    # Bypass si ya está normalizado
    if val_str.startswith('bnmm_'):
        return val_str
        
    # Aplicar regla: 9 dígitos + prefijo
    if val_str.isdigit():
        return f"bnmm_{val_str.zfill(9)}"
        
    return val_str

def main():
    print("--- INICIANDO NORMALIZACIÓN DE LLAVES LEGACY ---")
    
    for nombre_archivo in ARCHIVOS_A_NORMALIZAR:
        ruta = os.path.join(DIR_RAW, nombre_archivo)
        
        if not os.path.exists(ruta):
            print(f"⚠️ Omitiendo {nombre_archivo}: No encontrado en {DIR_RAW}")
            continue
            
        print(f"🔄 Procesando: {nombre_archivo}...")
        
        # dtype=str previene que Pandas asuma que son floats/ints y rompa ceros existentes
        df = pd.read_csv(ruta, sep='\t', dtype={'No. de sistema': str})
        
        if 'No. de sistema' in df.columns:
            # Aplicar transformación
            df['No. de sistema'] = df['No. de sistema'].apply(normalizar_id_sistema)
            
            # Sobrescribir el archivo
            df.to_csv(ruta, sep='\t', index=False, encoding='utf-8')
            print(f"   ✅ Columna 'No. de sistema' normalizada y guardada.")
        else:
            print(f"   🛑 Error: La columna 'No. de sistema' no existe en este TSV.")

if __name__ == '__main__':
    main()