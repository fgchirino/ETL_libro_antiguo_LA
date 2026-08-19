"""
Registro centralizado de parámetros institucionales y estrategias de ingesta.
"""

CONFIG_INSTITUCIONES = {
    'bnmm': {
        'tipo_extractor': 'Z3950',
        'archivo_origen': 'BNMM_urls.tsv',
        'estrategia_extraccion': 'regex',
        'parametros_red': {
            'host': 'tcp:200.123.191.9:9991/BNA01',
            'credenciales': '-u Z39.50/Z39.50'
        },
        'parametros_busqueda': {
            'atributo_id': '12',  # Local Number en el estándar Bib-1
            'formato_salida': 'usmarc',
            'extension_salida': '.mrc'
        },
        'parseo_entrada': {
            'regex_id': r'doc_number=(\d+)'
            
        }
    },
    'bne': {
        'tipo_extractor': 'SRU',
        'archivo_origen': 'BNE_listado_ids_001.tsv',
        'estrategia_extraccion': 'directa',
        'parametros_red': {
            'host': 'https://catalogo.bne.es/view/sru/34BNE_INST'
        },
        'parametros_busqueda': {
            'version': '1.2',
            'recordSchema': 'marcxml',
            'indice_busqueda': 'alma.mms_id',
            'extension_salida': '.xml'
        }
    }
}