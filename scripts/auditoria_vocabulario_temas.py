import os
import json
import pandas as pd
from collections import defaultdict
import re

# Rutas
DIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
RUTA_CONCEPTOS = os.path.join(DIR_BASE, 'procesada', 'conceptos.json')
RUTA_AUTORIDADES = os.path.join(DIR_BASE, 'procesada', 'autoridades.json')
RUTA_SALIDA = os.path.join(DIR_BASE, 'interim', 'auditoria_vocabulario.tsv')

ETIQUETAS_IGNORADAS = ['655']

def limpiar_termino(texto):
    if not texto: return ""
    t = str(texto).strip().upper()
    return re.sub(r'[.,;/\\]+$', '', t).strip()

def main():
    print("--- INICIANDO AUDITORÍA DE VOCABULARIO (BLINDADA Y LISTA BLANCA) ---")
    
    datos_agrupados = defaultdict(int)
    
    def registrar_termino(termino, etiqueta, subcampo_str, clasificacion, frecuencia):
        t_limpio = limpiar_termino(termino)
        if t_limpio:
            llave = (t_limpio, etiqueta, subcampo_str, clasificacion)
            datos_agrupados[llave] += frecuencia

    def procesar_grafo(ruta_json, es_autoridad=False):
        if not os.path.exists(ruta_json):
            print(f"⚠️ Omitiendo: No se encontró {ruta_json}")
            return

        with open(ruta_json, 'r', encoding='utf-8') as f:
            grafo = json.load(f)

        nodos_procesados = 0
        for id_nodo, nodo in grafo.items():
            etiqueta = str(nodo.get('etiqueta_origen', ''))
            
            if etiqueta in ETIQUETAS_IGNORADAS: continue
            if es_autoridad and not etiqueta.startswith('6'): continue 

            subcampos = nodo.get('subcampos', {})
            frec_nodo = nodo.get('frecuencia', 1)
            terminos_extraidos = 0
            
            # --- HEURÍSTICA INTELIGENTE DE EXTRACCIÓN ---

            # REGLA 1: Personas e Instituciones (Unificar identidad)
            if etiqueta in ['600', '610', '611']:
                partes_nombre = []
                for sub in ['a', 'b', 'c', 'd', 'q']:
                    if sub in subcampos:
                        val = subcampos[sub]
                        # Soporte para listas por si el split ocurre aquí
                        if isinstance(val, list):
                            partes_nombre.extend([str(v).strip() for v in val])
                        else:
                            partes_nombre.append(str(val).strip())
                
                if partes_nombre:
                    nombre_completo = " ".join(partes_nombre)
                    registrar_termino(nombre_completo, etiqueta, "a-d,q", "Persona/Institucion", frec_nodo)
                    terminos_extraidos += 1
                    
            # REGLA 2: Obras y Títulos Uniformes explícitos
            if etiqueta == '630' and 'a' in subcampos:
                val = subcampos['a']
                valores = val if isinstance(val, list) else [val]
                for v in valores:
                    registrar_termino(v, etiqueta, "a", "Obra/Titulo", frec_nodo)
                    terminos_extraidos += 1

            # REGLA 3: Lista Blanca estricta (Escudo antimedata)
            subcampos_auditar = ['a', 'v', 'x', 'y', 'z', 't', 'p']
            
            for codigo, valor_o_lista in subcampos.items():
                if codigo not in subcampos_auditar:
                    continue # Ignora por completo $2, $0, $e, $4, etc.
                
                # Evitar doble procesamiento de lo que ya hicieron las reglas 1 y 2
                if etiqueta in ['600', '610', '611'] and codigo == 'a': continue
                if etiqueta == '630' and codigo == 'a': continue

                # Iterar ya sea sobre string único o lista fragmentada
                valores = valor_o_lista if isinstance(valor_o_lista, list) else [valor_o_lista]
                
                for valor in valores:
                    clasificacion = "Desconocido"
                    if codigo == 'v':
                        clasificacion = "Forma/Genero"
                    elif codigo == 'z' or (etiqueta == '651' and codigo == 'a'):
                        clasificacion = "Geografico"
                    elif codigo == 'y' or (etiqueta == '648' and codigo == 'a'):
                        clasificacion = "Cronologico"
                    elif codigo == 'x' or (etiqueta == '650' and codigo == 'a'):
                        clasificacion = "Topico"
                    elif codigo in ['t', 'p']:
                        clasificacion = "Obra/Titulo"
                    elif codigo == 'a': 
                        clasificacion = "Topico_Otro"

                    registrar_termino(valor, etiqueta, codigo, clasificacion, frec_nodo)
                    terminos_extraidos += 1
            
            if terminos_extraidos > 0:
                nodos_procesados += 1
                
        print(f"✅ {os.path.basename(ruta_json)} procesado ({nodos_procesados} nodos válidos).")

    procesar_grafo(RUTA_CONCEPTOS, es_autoridad=False)
    procesar_grafo(RUTA_AUTORIDADES, es_autoridad=True)

    if not datos_agrupados:
        print("🛑 Error: No hay datos para exportar.")
        return

    # Aplanar y estructurar para Pandas
    filas = []
    for llave, frec in datos_agrupados.items():
        filas.append({
            'Termino_Limpio': llave[0],
            'Frecuencia': frec,
            'Etiqueta_Origen': llave[1],
            'Subcampo': llave[2],
            'Clasificacion': llave[3]
        })
        
    df_out = pd.DataFrame(filas)
    df_out = df_out.sort_values(by=['Clasificacion', 'Frecuencia', 'Termino_Limpio'], ascending=[True, False, True])

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df_out.to_csv(RUTA_SALIDA, sep='\t', index=False, encoding='utf-8')
    
    print("-" * 60)
    print(f"📊 Total de cadenas semánticas únicas: {len(df_out)}")
    print(f"📄 Archivo exportado: {RUTA_SALIDA}")

if __name__ == '__main__':
    main()