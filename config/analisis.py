"""
Configuración de la Fase Analítica (Reportes y Bibliometría)
Aquí se definen las heurísticas de investigación, independientes del modelo de extracción.
"""

# 1. PARÁMETROS TEMPORALES
RANGO_ANIO_INICIO = 1450
RANGO_ANIO_FIN = 1767

# 2. FILTROS DE RED SEMÁNTICA (LISTAS BLANCAS)
# Subcampos que contienen valor semántico para co-ocurrencia temática
SUBCAMPOS_TEMATICOS_PERMITIDOS = ['a', 'x', 'y', 'z', 't', 'p']

# 3. BLACKLIST TEMÁTICA (Ruido a excluir de los gráficos de materias y red semántica)
# Estos términos existen en el JSON, pero se ignoran en el análisis.
BLACKLIST_TEMATICA = [
    'OBRAS ANTERIORES A 1800',
    'S.XVIII',
    'SIGLO XVII',
    'CRÍTICA E INTERPRETACIÓN',
    'GENERAL',
    'LIBROS ANTIGUOS'
]

# 4. NORMALIZACIÓN DE IMPRESORES (Familias y Talleres)
# Diccionario para agrupar variantes topográficas en el análisis de producción
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