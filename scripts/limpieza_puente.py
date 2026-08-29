import os
import pandas as pd
import re

# Rutas
ruta_bne_xml = "data/raw/registros_bne_20260819_190415.xml"
ruta_puente = "data/raw/Tabla_Puente.tsv"

def mapear_oclc_bne_robusto(xml_path):
    mapa = {}
    if not os.path.exists(xml_path):
        print(f"🛑 No se encontró {xml_path}")
        return mapa

    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Dividimos el documento en bloques usando la etiqueta record (ignora todo lo demás)
    records = re.split(r'<[^>]*:?record[^>]*>', content)
    
    for record in records:
        # Extraer el 001
        match_001 = re.search(r'<[^>]*:?controlfield[^>]*tag="001"[^>]*>\s*(.*?)\s*</[^>]*:?controlfield>', record)
        if not match_001:
            continue
            
        id_bne = match_001.group(1).strip()
        id_bne_limpio = "bne_" + id_bne
        
        # Extraer todos los 035 usando re.DOTALL (por si hay saltos de línea)
        campos_035 = re.findall(r'<[^>]*:?datafield[^>]*tag="035"[^>]*>(.*?)</[^>]*:?datafield>', record, re.DOTALL)
        
        for campo in campos_035:
            # Buscar el subcampo "a" dentro del 035
            match_a = re.search(r'<[^>]*:?subfield[^>]*code="a"[^>]*>\s*(.*?)\s*</[^>]*:?subfield>', campo)
            if match_a:
                val = match_a.group(1).strip()
                if val.startswith('(OCoLC)'):
                    mapa[val] = id_bne_limpio
                    
    return mapa

def limpiar_tabla():
    print("🧹 Iniciando limpieza de Tabla Puente...")
    mapa = mapear_oclc_bne_robusto(ruta_bne_xml)
    print(f"🔍 Se encontraron {len(mapa)} equivalencias OCLC -> BNE en el XML mediante Regex.")
    
    if len(mapa) == 0:
        print("⚠️ No se extrajeron mapeos. Revisa la ruta del archivo XML.")
        return

    try:
        df = pd.read_csv(ruta_puente, sep='\t', dtype=str)
    except FileNotFoundError:
        print(f"🛑 No se encontró {ruta_puente}")
        return
    
    def normalizar(val):
        if pd.isna(val): return val
        val = val.strip()
        # 1. Si es OCLC y está en el XML, lo traduce a BNE
        if val in mapa:
            return mapa[val]
        # 2. Si es numérico (BNMM), le aplica el zfill(9) y el prefijo
        elif val.isnumeric():
            return 'bnmm_' + val.zfill(9)
        # 3. Si no cumple, lo deja como está
        return val

    if 'ID_Manifestacion' in df.columns:
        df['ID_Manifestacion'] = df['ID_Manifestacion'].apply(normalizar)
        df.to_csv(ruta_puente, sep='\t', index=False, encoding='utf-8')
        print("✅ Tabla_Puente.tsv ha sido actualizada permanentemente con las nuevas llaves relacionales.")
    else:
        print("🛑 Error: No se encontró la columna 'ID_Manifestacion' en la Tabla Puente.")

if __name__ == "__main__":
    limpiar_tabla()