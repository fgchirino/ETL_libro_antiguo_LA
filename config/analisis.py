"""
Configuración de la Fase Analítica (Reportes y Bibliometría)
Single Source of Truth para las heurísticas de investigación (Fase 4).
"""

# ==============================================================================
# 1. PARÁMETROS TEMPORALES
# ==============================================================================
RANGO_ANIO_INICIO = 1450
RANGO_ANIO_FIN = 1767

# ==============================================================================
# 2. FILTROS PARA ANÁLISIS DE CONTENIDO Y RED SEMÁNTICA
# ==============================================================================
CLASES_PERMITIDAS = [
    'Topico', 
    'Topico_Otro',
    'Persona',           # 600
    'Institucion',       # 610
    'Congreso_Reunion',  # 611
    'Obra/Titulo',       # 630 o subcampos $t, $p
    'Geografico'         # 651 o subcampos $z
]

BLACKLIST_TEMATICA = [
    'CRÍTICA E INTERPRETACIÓN',
    'BIOGRAFÍAS',
    'OBRAS ANTERIORES A 1800',
    'GENERAL',
    'S.XVIII',
    'SIGLO XVII'
]

SUBCAMPOS_TEMATICOS_PERMITIDOS = ['a', 'x', 'y', 'z', 't', 'p']

# ==============================================================================
# 3. NORMALIZACIÓN DE IMPRESORES (Familias y Talleres)
# ==============================================================================
AGRUPACION_EDITORES = {
    'Anisson':      ['ANISSOU', 'ANISSON', 'ANISSONIOS', 'LAURENTII ANISSON', 'LAURENTIJ ANISSON'],
    'Baglioni':     ['BALLEONIANA', 'BALLEONI', 'TYPOGRAPHIA BALLEONIANA'],
    'Plantino-Moreto': ['PLANTINIANA', 'PLANTIN', 'BALTHASARIS MORETI', 'MORETI'],
    'Veith (Hermanos)': ['VEITH', 'FFF. VEITH', 'WIDMANSTADIANIS'],
    'Placho':       ['PLACHI', 'PLACHO', 'GEORGII PLACHI'],
    'Sánchez':      ['LUIS SANCHEZ', 'LUDOVICI SACHEZ', 'SÃCHEZ', 'SANCHEZ'],
    'Cuesta':       ['IUAN DE LA CUESTA', 'JUAN DE LA CUESTA'],
    'Ibarra':       ['YBAR', 'IBARRA'], 
    'Cendrat':      ['CENDRAT', 'IAYME CENDRAT'],
    'Cardon':       ['CARDON', 'HORATII CARDON'],
    'Imprenta Real':['TYPOGRAPHIA REGIA', 'OFFICINA REGIA', 'IMPRENTA REAL'],
    'Compañía de Jesús': ['COLLEGIO DAS ARTES', 'SOCIETATIS IESU', 'COMPANHIA DE JESU']
}

# ==============================================================================
# 4. NORMALIZACIÓN TOPOGRÁFICA (Lugares de Edición)
# ==============================================================================
PREFIJOS_LUGARES = [r'^EN\s+', r'^IMPRESSO EN\s+', r'^IMPRESO EN\s+']

NORMALIZACION_LUGARES = {
    'MATRITI': 'Madrid', 'MADRITI': 'Madrid', 'MADRID': 'Madrid',
    'LUGDUNI': 'Lyon', 'LVGDUNI': 'Lyon', 'LVGDVNI': 'Lyon',
    'ULYSSIPONE': 'Lisboa', 'VLYSSIPONE': 'Lisboa',
    'ROMÆ': 'Roma', 'ROMAE': 'Roma', 'ROMĘ': 'Roma', 
    'ANTVERPIÆ': 'Amberes', 'ANTVERPIAE': 'Amberes',
    'AUGUSTÆ VINDELICORUM ET GRÆCII': 'Augsburgo',
    'AUGUSTÆ VINDELICORUM': 'Augsburgo', 'AUGUSTAE VINDELICORUM': 'Augsburgo',
    'GRAECIJ': 'Graz', 'DILINGAE': 'Dillingen', 'MOGVNTIÆ': 'Maguncia',
    'COLONIÆ-ALLOBROGUM': 'Ginebra', 'COLONIAE-ALLOBROGUM': 'Ginebra',
    'DUACI': 'Douai', 'VENETIIS': 'Venecia', 'EBORAE': 'Évora',
    'GADIBUS': 'Cádiz', 'HISPALI': 'Sevilla', 'SEVILLA': 'Sevilla',
    'ZARAGOÇA': 'Zaragoza', 'NAPOLES': 'Nápoles' 
}

# ==============================================================================
# 5. ESTÉTICA Y VISUALIZACIÓN (Paleta Unificada Tufte/Brewer)
# ==============================================================================
PALETA = {
    # --- Colores Base Estructurales ---
    'inventario': '#8C1515',   # Rojo Cardenal (Acento Tufte para destacar lagunas/anomalías)
    'manifestacion': '#5F715F', # Verde Salvia (Neutro cálido para el catálogo bibliográfico)
    'item': '#D4B872',         # Ocre Pergamino (Materialidad física)
    'fondo_web': '#F9F6F0',    # Blanco Roto
    'fondo_oscuro': '#2C3E50', # Gris Grafito (Textos)
    'grafico_barras': '#708090',# Gris Pizarra (Neutro universal para ejes y fondos)
    
    # --- Rampa Secuencial ColorBrewer ---
    # Derivados de Marrón Nogal (#4A3B32) modificando luminosidad para variables categóricas
    'huella_seq_1': '#4A3B32', # Base L:24%
    'huella_seq_2': '#6B574A', # L:35%
    'huella_seq_3': '#8D7462', # L:47%
    'huella_seq_4': '#AE917A', # L:58%
    'huella_seq_5': '#D0AE92', # L:69%
    'huella_seq_6': '#E5CFBE'  # L:82%
}

# ==============================================================================
# 6. FILTROS DE ROLES (RELATORES MARC $e / $4)
# ==============================================================================
ROLES_EDITORES_PERMITIDOS = [
    'impresor', 'editor', 'librero', 'impr.',
    'typographus', 'typographi', 'typis', 'prt', 'pbl', 'bsl'
]

# ==============================================================================
# 7. PARÁMETROS DE RED SEMÁNTICA (GRAFOS)
# ==============================================================================
MIN_COOCURRENCIAS_RED = 1

MAPEO_SUBCAMPOS_ONTOLOGIA = {
    'x': 'Topico',
    'z': 'Geografico',
    't': 'Obra/Titulo',
    'p': 'Obra/Titulo'
}

MAPEO_COLORES_ONTOLOGIA = {
    'Topico': PALETA['manifestacion'],      
    'Topico_Otro': PALETA['manifestacion'], 
    'Persona': PALETA['inventario'],        
    'Institucion': PALETA['fondo_oscuro'],  
    'Obra/Titulo': PALETA['item'],          
    'Geografico': PALETA['grafico_barras']  
}