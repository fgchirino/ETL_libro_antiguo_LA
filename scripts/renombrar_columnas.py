import os
import pandas as pd

# Rutas exactas según tu árbol
DIR_RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/raw'))

ARCHIVOS_A_PROCESAR = [
    'materialidad_huellas.tsv',
    'materialidad_items.tsv',
    'tabla_puente.tsv'
]

def main():
    print("--- INICIANDO RENOMBRAMIENTO DE LLAVES AL ESTÁNDAR RELACIONAL ---")
    
    for nombre_archivo in ARCHIVOS_A_PROCESAR:
        ruta = os.path.join(DIR_RAW, nombre_archivo)
        
        if not os.path.exists(ruta):
            print(f"⚠️ Omitiendo {nombre_archivo}: No encontrado.")
            continue
            
        print(f"🔄 Procesando: {nombre_archivo}...")
        
        # Leer todo como string para no alterar nada del contenido
        df = pd.read_csv(ruta, sep='\t', dtype=str)
        
        renombres = {}
        if 'No. de sistema' in df.columns:
            renombres['No. de sistema'] = 'ID_Manifestacion'
        if 'No. inventario' in df.columns:
            renombres['No. inventario'] = 'ID_Item'
        if 'Inventario' in df.columns:
            renombres['Inventario'] = 'ID_Item'
            
        if renombres:
            df.rename(columns=renombres, inplace=True)
            df.to_csv(ruta, sep='\t', index=False, encoding='utf-8')
            print(f"   ✅ Columnas renombradas exitosamente: {renombres}")
        else:
            print("   ℹ️ No requirió cambios.")

if __name__ == '__main__':
    main()