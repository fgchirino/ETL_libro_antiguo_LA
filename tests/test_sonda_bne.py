import os
import xml.etree.ElementTree as ET
import re

archivo = "data/raw/registros_bne_20260823_204105.xml"

def analizar_xml(ruta):
    print(f"🔍 INICIANDO SONDA EN: {os.path.basename(ruta)}\n")
    
    if not os.path.exists(ruta):
        print("🛑 El archivo no existe en la ruta indicada.")
        return

    with open(ruta, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
        
    print(f"📊 ESTADÍSTICAS CRUDAS:")
    print(f"  - Total de líneas: {len(lineas)}")
    
    xml_decl = sum(1 for line in lineas if '<?xml' in line)
    print(f"  - Declaraciones <?xml ... ?>: {xml_decl} (Debería ser 1)")
    
    aperturas = sum(1 for line in lineas if '<record' in line)
    cierres = sum(1 for line in lineas if '</record>' in line)
    print(f"  - Etiquetas de apertura <record...>: {aperturas}")
    print(f"  - Etiquetas de cierre </record>: {cierres}")
    
    if aperturas != cierres:
        print(f"  ⚠️ ALERTA: Desajuste matemático de etiquetas. Faltan/Sobran {abs(aperturas - cierres)}.")
    
    print("\n🛠️ INTENTO DE PARSEO ESTRICTO:")
    try:
        tree = ET.parse(ruta)
        print("  ✅ Parseo exitoso. El XML está bien formado.")
    except ET.ParseError as e:
        print(f"  🛑 Fallo crítico de estructura: {e}")
        
        # Extraer el número de línea del error para mostrar el contexto
        match = re.search(r'line (\d+)', str(e))
        if match:
            num_linea = int(match.group(1))
            print(f"\n🔬 RADIOGRAFÍA DEL ERROR (Línea {num_linea}):")
            inicio = max(0, num_linea - 6)
            fin = min(len(lineas), num_linea + 5)
            
            for i in range(inicio, fin):
                prefijo = " ❌ >> " if i + 1 == num_linea else "      "
                print(f"{prefijo}{i+1}: {lineas[i].rstrip()}")

if __name__ == "__main__":
    analizar_xml(archivo)