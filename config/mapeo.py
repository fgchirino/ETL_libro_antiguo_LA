"""
Configuración del mapeo de extracción MARC21.
Single Source of Truth (SoT) para la generación de grafos JSON y el subproducto tabular.
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
        "subcampos": ["*"]
    }
}

# --- REGLAS ONTOLÓGICAS (FASE 2) ---

MAPEO_AUTORIDADES = {
    '100': {'entidad': 'Persona'},
    '700': {'entidad': 'Persona'},
    '600': {'entidad': 'Persona'},
    '110': {'entidad': 'Institucion'},
    '710': {'entidad': 'Institucion'},
    '610': {'entidad': 'Institucion'},
    '111': {'entidad': 'Congreso_Reunion'},
    '711': {'entidad': 'Congreso_Reunion'},
    '611': {'entidad': 'Congreso_Reunion'},
    '130': {'entidad': 'Obra'},
    '730': {'entidad': 'Obra'},
    '630': {'entidad': 'Obra'}
}

MAPEO_CONCEPTOS = {
    '648': {'entidad': 'Termino_Cronologico', 'split_caracter': '--'},
    '650': {'entidad': 'Topico', 'split_caracter': '--'},
    '651': {'entidad': 'Lugar_Geografico', 'split_caracter': '--'},
    '653': {'entidad': 'Keyword_No_Controlada', 'split_caracter': '--'},
    '655': {'entidad': 'Genero_Forma', 'split_caracter': '--'}
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