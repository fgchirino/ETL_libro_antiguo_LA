import pymarc
from collections import Counter

# Usamos la ruta relativa asumiendo que ejecutas desde la raíz del proyecto
ruta_mrc = "data/raw/registros_bnmm.mrc"

longitudes = Counter()
ejemplos = {}
total_registros = 0
sin_001 = 0

print(f"🔍 Analizando: {ruta_mrc}")

try:
    with open(ruta_mrc, 'rb') as f:
        reader = pymarc.MARCReader(f)
        for record in reader:
            if record is None:
                continue
                
            total_registros += 1
            
            if '001' in record:
                id_001 = record['001'].data
                largo = len(id_001)
                longitudes[largo] += 1
                
                # Guardar un ejemplo de cada longitud encontrada
                if largo not in ejemplos:
                    ejemplos[largo] = id_001
            else:
                sin_001 += 1

    print("\n📊 RESULTADOS DEL DIAGNÓSTICO:")
    print(f"Total de registros analizados: {total_registros}")
    if sin_001 > 0:
        print(f"⚠️ Registros sin campo 001: {sin_001}")
        
    print("\nDistribución de longitudes del campo 001:")
    for largo, cantidad in sorted(longitudes.items()):
        print(f"  -> Longitud {largo}: {cantidad} registros (Ejemplo: '{ejemplos[largo]}')")

except FileNotFoundError:
    print(f"🛑 Error: No se encontró el archivo en la ruta {ruta_mrc}")
except Exception as e:
    print(f"🛑 Error inesperado: {e}")