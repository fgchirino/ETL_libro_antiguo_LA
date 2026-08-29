import os
import sys
import json
import re
from datetime import datetime
from collections import Counter
from itertools import combinations

import pandas as pd
import networkx as nx

# Añadir el root al path para importar configuración
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.analisis import (
    RANGO_ANIO_INICIO, RANGO_ANIO_FIN, 
    PALETA, NORMALIZACION_LUGARES, PREFIJOS_LUGARES,
    AGRUPACION_EDITORES, CLASES_PERMITIDAS, BLACKLIST_TEMATICA,
    ROLES_EDITORES_PERMITIDOS, SUBCAMPOS_TEMATICOS_PERMITIDOS,
    MIN_COOCURRENCIAS_RED, MAPEO_SUBCAMPOS_ONTOLOGIA, MAPEO_COLORES_ONTOLOGIA
)

from src.libreria.visualizador import (
    graficar_torta, graficar_barras_verticales, graficar_histograma, 
    graficar_heatmap, graficar_barras_horizontales, graficar_pareto, graficar_red_semantica
)

DIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
DIR_PROCESADA = os.path.join(DIR_BASE, 'procesada')
DIR_REPORTES = os.path.join(DIR_BASE, 'reportes')

os.makedirs(DIR_REPORTES, exist_ok=True)

# ==============================================================================
# HERRAMIENTAS AUXILIARES
# ==============================================================================

def obtener_top_estable(lista_elementos):
    """Ordenamiento determinista: Frecuencia Descendente -> Alfabético Ascendente."""
    conteo = Counter(lista_elementos)
    ordenado = sorted(conteo.items(), key=lambda x: (-x[1], x[0]))
    return pd.Series(dict(ordenado))

# ==============================================================================
# MOTOR DE EXTRACCIÓN (MODELO)
# ==============================================================================

def cargar_grafos():
    with open(os.path.join(DIR_PROCESADA, 'manifestaciones.json'), 'r', encoding='utf-8') as f:
        manifestaciones = json.load(f)
    with open(os.path.join(DIR_PROCESADA, 'autoridades.json'), 'r', encoding='utf-8') as f:
        autoridades = json.load(f)
    with open(os.path.join(DIR_PROCESADA, 'conceptos.json'), 'r', encoding='utf-8') as f:
        conceptos = json.load(f)
    return manifestaciones, autoridades, conceptos

def limpiar_fecha_marc(fecha_str):
    if pd.isna(fecha_str) or not fecha_str: return None
    match = re.search(r'\d{4}', str(fecha_str))
    if match:
        anio = int(match.group())
        return anio if 1000 <= anio <= 2000 else None
    return None

def limpiar_lugar_marc(lugar_str):
    if pd.isna(lugar_str) or not lugar_str: return "S.l."
    l = str(lugar_str).strip().upper()
    l = re.sub(r'[\[\]:,;]', '', l).strip()
    for prefijo in PREFIJOS_LUGARES: l = re.sub(prefijo, '', l).strip()
    for var, norm in NORMALIZACION_LUGARES.items():
        if var in l: return norm
    return l.title() if l else "S.l."

def normalizar_familia_editor(cadena_original):
    cadena_upper = cadena_original.upper()
    for familia, variantes in AGRUPACION_EDITORES.items():
        if any(var.upper() in cadena_upper for var in variantes): return familia
    return cadena_original.title()

def construir_df_base(manifestaciones):
    filas = []
    for id_manif, nodo in manifestaciones.items():
        fecha_cruda = None
        if 'fecha_publicacion' in nodo:
            for f in nodo['fecha_publicacion']:
                if isinstance(f, dict) and 'subcampos' in f and 'c' in f['subcampos']:
                    fecha_cruda = f['subcampos']['c']
                elif isinstance(f, str): fecha_cruda = f

        lugar_crudo = None
        if 'lugar_publicacion' in nodo:
            for l in nodo['lugar_publicacion']:
                 if isinstance(l, dict) and 'subcampos' in l and 'a' in l['subcampos']:
                     lugar_crudo = l['subcampos']['a']
                 elif isinstance(l, str): lugar_crudo = l

        filas.append({
            'ID_Manifestacion': id_manif,
            'Fuente_Origen': nodo.get('Fuente_Origen', 'Desconocida'),
            'Anio': limpiar_fecha_marc(fecha_cruda),
            'Lugar': limpiar_lugar_marc(lugar_crudo)
        })
    return pd.DataFrame(filas)

# ==============================================================================
# MÓDULOS ANALÍTICOS (CONTROLADORES)
# ==============================================================================

def modulo_1_censo_supervivencia(df_base):
    print("\n--- EJECUTANDO MÓDULO 1: CENSO DE SUPERVIVENCIA ---")
    ruta_inv = os.path.join(DIR_BASE, 'raw', 'inventario_temporalidades.tsv')
    ruta_puente = os.path.join(DIR_BASE, 'raw', 'tabla_puente.tsv')
    ruta_items = os.path.join(DIR_BASE, 'raw', 'materialidad_items.tsv')
    
    if not all(os.path.exists(r) for r in [ruta_inv, ruta_puente, ruta_items]):
        print("⚠️ Faltan archivos TSV. Omitiendo Módulo 1.")
        return

    df_inv = pd.read_csv(ruta_inv, sep='\t')
    df_cruce = pd.merge(df_inv, pd.read_csv(ruta_puente, sep='\t'), on='ID_Inventario', how='left')
    items_agrupados = pd.read_csv(ruta_items, sep='\t').groupby('ID_Manifestacion').size().reset_index(name='Cantidad_Fisicos')
    df_cruce = pd.merge(df_cruce, items_agrupados, on='ID_Manifestacion', how='left')

    rec = df_cruce[df_cruce['Cantidad_Fisicos'].notna()].shape[0]
    ide = df_cruce[(df_cruce['ID_Manifestacion'].notna()) & (df_cruce['Cantidad_Fisicos'].isna())].shape[0]
    lag = df_cruce[df_cruce['ID_Manifestacion'].isna()].shape[0]
    tot = len(df_inv)

    p_rec = (rec / tot) * 100 if tot else 0
    p_ide = (ide / tot) * 100 if tot else 0
    p_lag = (lag / tot) * 100 if tot else 0

    print(f"Total Histórico: {tot} | Recuperados: {rec} ({p_rec:.1f}%) | Identificados BNE: {ide} ({p_ide:.1f}%) | Lagunas: {lag} ({p_lag:.1f}%)")

    etiquetas = ['Recuperados Físicos', 'Identificación Bibliográfica', 'Pérdida (Lagunas)']
    valores = [rec, ide, lag]
    colores = [PALETA['item'], PALETA['manifestacion'], PALETA['inventario']]
    
    graficar_torta(valores, etiquetas, colores, 
                   f'Estado de Reconstrucción (Base: {tot} entradas)', 
                   os.path.join(DIR_REPORTES, '01_censo_supervivencia.png'))

def modulo_2_cronologia(df_base):
    print("\n--- EJECUTANDO MÓDULO 2: CRONOLOGÍA ---")
    df_filtrado = df_base[(df_base['Anio'] >= RANGO_ANIO_INICIO) & (df_base['Anio'] <= RANGO_ANIO_FIN)].copy()
    if df_filtrado.empty: return
    
    total_validos = len(df_filtrado)
    df_filtrado['Decada'] = (df_filtrado['Anio'] // 10) * 10
    df_filtrado['digito_anio'] = df_filtrado['Anio'] % 10
    
    min_dec = (RANGO_ANIO_INICIO // 10) * 10
    max_dec = (RANGO_ANIO_FIN // 10) * 10
    rango_decadas = list(range(min_dec, max_dec + 10, 10))
    
    conteo_decadas = df_filtrado['Decada'].value_counts().reindex(rango_decadas, fill_value=0)
    porcentaje_decadas = (conteo_decadas / total_validos) * 100
    
    top3_decadas = df_filtrado['Decada'].value_counts().head(3)
    top3_str = ", ".join([f"{int(k)}: {v} ({(v/total_validos)*100:.1f}%)" for k, v in top3_decadas.items()])
    
    print(f"Manifestaciones en rango: {total_validos} | Décadas con picos: {top3_str}")

    graficar_histograma(df_filtrado['Anio'].dropna(), 40, f'Distribución Anual ({RANGO_ANIO_INICIO}-{RANGO_ANIO_FIN})', 
                        'Año', 'Cantidad', PALETA['inventario'], os.path.join(DIR_REPORTES, '02a_cronologia_anual.png'))
    graficar_barras_verticales(porcentaje_decadas, 'Peso Porcentual por Década', 'Década', '% del Total', 
                               PALETA['grafico_barras'], os.path.join(DIR_REPORTES, '02b_cronologia_decadas_pct.png'))
    graficar_heatmap(df_filtrado, 'Intensidad Editorial Detallada', os.path.join(DIR_REPORTES, '02c_cronologia_heatmap.png'), rango_decadas)

def modulo_3_topografia(df_base):
    print("\n--- EJECUTANDO MÓDULO 3: TOPOGRAFÍA ---")
    df_geo = df_base[df_base['Lugar'] != 'S.l.'].copy()
    if df_geo.empty: return
    
    conteo = obtener_top_estable(df_geo['Lugar'].tolist())
    total_geo = conteo.sum()
    
    top5_str = ", ".join([f"{k}: {v} ({(v/total_geo)*100:.1f}%)" for k, v in conteo.head(5).items()])
    print(f"Total registros con lugar válido: {total_geo} | Top 5 lugares: {top5_str}")
    
    graficar_barras_horizontales(conteo.head(15), 'Top 15 Centros de Impresión', PALETA['manifestacion'], 
                                 os.path.join(DIR_REPORTES, '03a_topografia_top15.png'))
    graficar_pareto(conteo, 'Ley de Pareto: Concentración Geográfica', PALETA['manifestacion'], PALETA['inventario'], 
                    os.path.join(DIR_REPORTES, '03b_topografia_pareto.png'))

def modulo_4_editores(manifestaciones, autoridades, df_base):
    print("\n--- EJECUTANDO MÓDULO 4: PRODUCCIÓN EDITORIAL ---")
    ediciones = []
    for id_manif, nodo_manif in manifestaciones.items():
        for id_aut in nodo_manif.get('autoridades_vinculadas', []):
            aut = autoridades.get(id_aut)
            if not aut or not str(aut.get('etiqueta_origen', '')).startswith('7'): continue
            
            roles = []
            for sub in ['e', '4']:
                val = aut.get('subcampos', {}).get(sub)
                if val: roles.extend(val if isinstance(val, list) else [val])
            
            if roles and any(any(rp in str(r).strip().lower() for rp in ROLES_EDITORES_PERMITIDOS) for r in roles):
                ediciones.append(normalizar_familia_editor(aut.get('cadena_limpia', 'Anónimo')))

    if not ediciones: return
    
    conteo = obtener_top_estable(ediciones)
    total_ed = conteo.sum()
    
    top3_ed = ", ".join([f"{k}: {v} ({(v/total_ed)*100:.1f}%)" for k, v in conteo.head(3).items()])
    print(f"Familias Impresoras Validadas: {len(conteo)} (Frecuencia total: {total_ed}) | Top 3: {top3_ed}")
    
    graficar_barras_horizontales(conteo.head(15), 'Top 15 Familias Impresoras', PALETA['inventario'], 
                                 os.path.join(DIR_REPORTES, '04a_editores_top15.png'))
    graficar_pareto(conteo, 'Dispersión Editorial (Pareto)', PALETA['inventario'], PALETA['fondo_oscuro'], 
                    os.path.join(DIR_REPORTES, '04b_editores_pareto.png'))

def modulo_5_analisis_tematico(manifestaciones, conceptos, autoridades):
    print("\n--- EJECUTANDO MÓDULO 5: ANÁLISIS TEMÁTICO Y COBERTURA ---")
    temas_extraidos = []
    cobertura = [] 
    
    for id_manif, nodo_manif in manifestaciones.items():
        fuente = nodo_manif.get('Fuente_Origen', 'Desconocida')
        tiene_tema = False
        
        for id_ent in (nodo_manif.get('conceptos_vinculados', []) + nodo_manif.get('autoridades_vinculadas', [])):
            ent = conceptos.get(id_ent) or autoridades.get(id_ent)
            if not ent or not str(ent.get('etiqueta_origen', '')).startswith('6') or ent.get('tipo_entidad') not in CLASES_PERMITIDAS: continue
            
            for code, val in ent.get('subcampos', {}).items():
                if code in SUBCAMPOS_TEMATICOS_PERMITIDOS:
                    for v in (val if isinstance(val, list) else [val]):
                        t = str(v).strip(' .,;[]').upper()
                        if t and t not in [b.upper() for b in BLACKLIST_TEMATICA]: 
                            temas_extraidos.append(t)
                            tiene_tema = True
                            
        cobertura.append({'Fuente': fuente, 'Tiene_Tema': 1 if tiene_tema else 0})

    df_cob = pd.DataFrame(cobertura)
    if not df_cob.empty:
        res = df_cob.groupby('Fuente')['Tiene_Tema'].agg(['count', 'sum'])
        res['% Cobertura'] = (res['sum'] / res['count']) * 100
        pct_cobertura = res['% Cobertura']
        print(f"\nCobertura Temática:\n{res[['count', 'sum', '% Cobertura']].round(1)}")
        graficar_barras_verticales(pct_cobertura, 'Cobertura Temática por Institución', 'Institución', '% con Materias', 
                                   PALETA['grafico_barras'], os.path.join(DIR_REPORTES, '05a_cobertura_fuentes.png'))

    if not temas_extraidos: return
    
    conteo = obtener_top_estable(temas_extraidos)
    total_temas = conteo.sum()
    
    top5_temas = ", ".join([f"{k}: {v} ({(v/total_temas)*100:.1f}%)" for k, v in conteo.head(5).items()])
    print(f"Conceptos Únicos Extraídos: {len(conteo)} (Asignaciones totales: {total_temas})\nTop 5 Materias: {top5_temas}")
    
    graficar_barras_horizontales(conteo.head(20), 'Top 20 Materias Frecuentes', PALETA['grafico_barras'], 
                                 os.path.join(DIR_REPORTES, '05b_temas_top20.png'))
    graficar_pareto(conteo, 'Dispersión Temática (Pareto)', PALETA['grafico_barras'], PALETA['fondo_oscuro'], 
                    os.path.join(DIR_REPORTES, '05c_temas_pareto.png'))

def modulo_6_red_semantica(manifestaciones, conceptos, autoridades):
    print("\n--- EJECUTANDO MÓDULO 6: RED SEMÁNTICA ---")
    todas_las_parejas = []
    frecuencia_nodos = Counter()
    tipo_nodos = {} 

    for nodo_manif in manifestaciones.values():
        nodos_libro = []
        for id_ent in (nodo_manif.get('conceptos_vinculados', []) + nodo_manif.get('autoridades_vinculadas', [])):
            ent = conceptos.get(id_ent) or autoridades.get(id_ent)
            if not ent or not str(ent.get('etiqueta_origen', '')).startswith('6') or ent.get('tipo_entidad') not in CLASES_PERMITIDAS: continue
            
            tipo_base = ent.get('tipo_entidad')
            for code, val in ent.get('subcampos', {}).items():
                if code in SUBCAMPOS_TEMATICOS_PERMITIDOS:
                    for v in (val if isinstance(val, list) else [val]):
                        # LIMPIEZA REGEX: Elimina cualquier trailing space o puntuación
                        t = re.sub(r'[.,;\[\]\s]+$', '', str(v)).strip().upper()
                        
                        if t and t not in [b.upper() for b in BLACKLIST_TEMATICA]:
                            nodos_libro.append(t)
                            tipo_nodos[t] = MAPEO_SUBCAMPOS_ONTOLOGIA.get(code, tipo_base)

        if len(nodos_libro) >= 2:
            nodos_unicos = list(set(nodos_libro))
            for n in nodos_unicos: frecuencia_nodos[n] += 1
            todas_las_parejas.extend(list(combinations(sorted(nodos_unicos), 2)))
        elif len(nodos_libro) == 1:
            frecuencia_nodos[nodos_libro[0]] += 1

    parejas_validas = {pair: weight for pair, weight in Counter(todas_las_parejas).items() if weight >= MIN_COOCURRENCIAS_RED}
    
    total_nodos = len(tipo_nodos)
    total_enlaces = len(parejas_validas)
    densidad = (2 * total_enlaces) / (total_nodos * (total_nodos - 1)) if total_nodos > 1 else 0
    
    total_ocurrencias = sum(frecuencia_nodos.values())
    top3_nodos = ", ".join([f"{k}: {v} ({(v/total_ocurrencias)*100:.1f}%)" for k, v in Counter(frecuencia_nodos).most_common(3)])

    print(f"Total nodos extraídos: {total_nodos} | Pares generados: {total_enlaces} | Densidad: {densidad:.4f}")
    print(f"Top 3 Nodos más conectados: {top3_nodos}")

    G = nx.Graph()
    for n in tipo_nodos.keys(): G.add_node(n)
    for pair, weight in parejas_validas.items(): G.add_edge(pair[0], pair[1], weight=weight)
        
    graficar_red_semantica(G, frecuencia_nodos, tipo_nodos, MAPEO_COLORES_ONTOLOGIA, MIN_COOCURRENCIAS_RED, 
                           PALETA['grafico_barras'], PALETA['fondo_oscuro'], os.path.join(DIR_REPORTES, '06_red_semantica.png'))
    
def modulo_7_materialidad():
    print("\n--- EJECUTANDO MÓDULO 7: ARQUEOLOGÍA DEL LIBRO ---")
    ruta_items = os.path.join(DIR_BASE, 'raw', 'materialidad_items.tsv')
    ruta_huellas = os.path.join(DIR_BASE, 'raw', 'materialidad_huellas.tsv')
    
    if os.path.exists(ruta_items):
        df_items = pd.read_csv(ruta_items, sep='\t')
        if 'Cubiertas' in df_items.columns:
            cubiertas = obtener_top_estable(df_items['Cubiertas'].dropna().tolist())
            tot_cub = cubiertas.sum()
            top_cub_str = ", ".join([f"{k}: {v} ({(v/tot_cub)*100:.1f}%)" for k, v in cubiertas.head(3).items()])
            
            print(f"Encuadernaciones documentadas: {len(cubiertas)} (Total ejemplares: {tot_cub}) | Principales: {top_cub_str}")
            graficar_barras_verticales(cubiertas.head(8), 'Tipos de Encuadernación', 'Cubierta', 'Ejemplares', 
                                       PALETA['item'], os.path.join(DIR_REPORTES, '07a_encuadernacion.png'))
    
    if os.path.exists(ruta_huellas):
        df_huellas = pd.read_csv(ruta_huellas, sep='\t')
        if 'Tipo_huella' in df_huellas.columns:
            huellas = obtener_top_estable(df_huellas['Tipo_huella'].dropna().tolist())
            tot_hue = huellas.sum()
            top_hue_str = ", ".join([f"{k}: {v} ({(v/tot_hue)*100:.1f}%)" for k, v in huellas.head(3).items()])
            
            print(f"Marcas de Propiedad: {len(huellas)} (Total huellas: {tot_hue}) | Principales: {top_hue_str}")
            
            # LÓGICA DATA-DRIVEN: Extrae dinámicamente la rampa secuencial del diccionario unificado
            colores_sec = [PALETA[k] for k in sorted(PALETA.keys()) if k.startswith('huella_seq_')]
            colores_aplicados = [colores_sec[i % len(colores_sec)] for i in range(len(huellas))]
            
            graficar_torta(huellas.values, huellas.index, colores_aplicados, 'Marcas de Propiedad / Huellas', 
                           os.path.join(DIR_REPORTES, '07b_huellas.png'))
            
# ==============================================================================
# ORQUESTADOR
# ==============================================================================

def main():
    print("Iniciando Fase 4: Generación Analítica MVC...")
    manifestaciones, autoridades, conceptos = cargar_grafos()
    df_base = construir_df_base(manifestaciones)
    
    modulo_1_censo_supervivencia(df_base)
    modulo_2_cronologia(df_base)
    modulo_3_topografia(df_base)
    modulo_4_editores(manifestaciones, autoridades, df_base)
    modulo_5_analisis_tematico(manifestaciones, conceptos, autoridades)
    modulo_6_red_semantica(manifestaciones, conceptos, autoridades)
    modulo_7_materialidad()

if __name__ == '__main__':
    main()