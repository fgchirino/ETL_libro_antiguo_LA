"""
Configuración del mapeo de extracción MARC21 a formato tabular.
Cada clave representa el nombre exacto de la columna final en el TSV.
El valor contiene las etiquetas MARC y los subcampos a extraer.
"""

MAPEO_MARC = {
    "id_control": {
        "etiquetas": ["001"], 
        "subcampos": [] 
    },
    "identificadores_alternativos": {
        "etiquetas": ["024"],
        "subcampos": ["*"]
    },
    "responsabilidad_principal_personal": {
        "etiquetas": ["100"], 
        "subcampos": ["*"]
    },
    "responsabilidad_principal_institucional": {
        "etiquetas": ["110"], 
        "subcampos": ["*"]
    },
    "responsabilidad_secundaria_personal": {
        "etiquetas": ["700"], 
        "subcampos": ["*"]
    },
    "responsabilidad_secundaria_institucional": {
        "etiquetas": ["710"], 
        "subcampos": ["*"]
    },
    "titulo_uniforme": {
        "etiquetas": ["130", "240", "730"], 
        "subcampos": ["*"]
    },
    "titulo_completo": {
        "etiquetas": ["245"], 
        "subcampos": ["a", "b", "n", "p", "c"]
    },
    "lugar_publicacion": {
        "etiquetas": ["260"], 
        "subcampos": ["a"]
    },
    "editorial": {
        "etiquetas": ["260"], 
        "subcampos": ["b"]
    },
    "fecha_publicacion": {
        "etiquetas": ["260"], 
        "subcampos": ["c"]
    },
    "extension": {
        "etiquetas": ["300"], 
        "subcampos": ["a"]
    },
    "detalles_fisicos": {
        "etiquetas": ["300"], 
        "subcampos": ["b"]
    },
    "dimensiones": {
        "etiquetas": ["300"], 
        "subcampos": ["c"]
    },
    "materias": {
        "etiquetas": ["600", "610", "611", "630", "648", "650", "651", "653", "655"],
        "subcampos": ["a", "v", "x", "y", "z"]
    }
}

# --- NUEVAS REGLAS PARA LA FASE 2 ---

MAPEO_AUTORIDADES = {
    '100': 'Persona',
    '700': 'Persona',
    '600': 'Persona',
    '110': 'Institucion',
    '710': 'Institucion',
    '610': 'Institucion',
    '111': 'Congreso/Reunion',
    '711': 'Congreso/Reunion',
    '611': 'Congreso/Reunion',
    '130': 'Obra',
    '730': 'Obra',
    '630': 'Obra'
}

MAPEO_LOD = {
    '035': [
        {'prefijo_origen': '(OCoLC)', 'columna_destino': 'uri_oclc', 'uri_base': 'http://www.worldcat.org/oclc/'},
        {'prefijo_origen': '(SpMaBN)', 'columna_destino': 'uri_bne', 'uri_base': 'https://datos.bne.es/resource/'}
    ],
    '016': [
        {'prefijo_origen': '(SpMaBN)', 'columna_destino': 'uri_bne', 'uri_base': 'https://datos.bne.es/resource/'}
    ]
}

ARCHIVOS_LOCALES = {
    'materialidad_items.tsv': {
        'columna_id': 'No. de sistema',
        'requiere_padding': True,
        'longitud_padding': 9,
        'prefijo': 'bnmm_'
    },
    'materialidad_huellas.tsv': {
        'columna_id': 'No. de sistema',
        'requiere_padding': True,
        'longitud_padding': 9,
        'prefijo': 'bnmm_'
    },
    'inventario_temporalidades.tsv': {
        'columna_id': 'ID_Inventario',
        'requiere_padding': False,
        'longitud_padding': 0,
        'prefijo': ''
    }
}