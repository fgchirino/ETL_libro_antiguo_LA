import os
import re

DIR_RAW = "data/raw"

def estandarizar_nombre(filename):
    """Convierte a minúsculas y reemplaza espacios o guiones por guiones bajos."""
    name, ext = os.path.splitext(filename)
    # Convertir a minúsculas
    name = name.strip().lower()
    # Reemplazar espacios y guiones con guiones bajos
    name = re.sub(r'[\s\-]+', '_', name)
    # Limpiar guiones bajos múltiples
    name = re.sub(r'_+', '_', name)
    return f"{name}{ext.lower()}"

def main():
    print(f"🧹 Iniciando normalización de archivos en {DIR_RAW}...")
    if not os.path.exists(DIR_RAW):
        print(f"🛑 No se encontró el directorio {DIR_RAW}")
        return

    cambios = 0
    for filename in os.listdir(DIR_RAW):
        ruta_actual = os.path.join(DIR_RAW, filename)
        
        # Ignorar directorios, solo procesar archivos
        if os.path.isfile(ruta_actual):
            nuevo_nombre = estandarizar_nombre(filename)
            
            if filename != nuevo_nombre:
                ruta_nueva = os.path.join(DIR_RAW, nuevo_nombre)
                os.rename(ruta_actual, ruta_nueva)
                print(f"  -> Renombrado: {filename}  =>  {nuevo_nombre}")
                cambios += 1

    print(f"✅ Normalización completada. Se renombraron {cambios} archivos.")

if __name__ == "__main__":
    main()