"""
Configuración del mapeo de extracción MARC21 a formato tabular.
Cada clave representa el nombre exacto de la columna final en el TSV.
El valor contiene las etiquetas MARC y los subcampos a extraer.
"""

MAPEO_MARC = {
    "id_control": {
        "etiquetas": ["001"], 
        "subcampos": [] # El campo 001 es de control, no posee subcampos
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
    "titulo_completo": {
        "etiquetas": ["245"], 
        "subcampos": ["a", "b"]
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
    }
}