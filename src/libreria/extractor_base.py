from abc import ABC, abstractmethod
from typing import Set

class ExtractorBase(ABC):
    """
    Clase abstracta que define el contrato estándar para cualquier
    motor de extracción (Z39.50, API REST, OAI-PMH, etc.).
    """
    def __init__(self, config_institucion: dict):
        self.config = config_institucion

    @abstractmethod
    def extraer_ids(self, ruta_fuente: str) -> Set[str]:
        """
        Lee el archivo de origen (ej. TSV) y extrae los identificadores únicos
        aplicando las reglas de la configuración de la institución.
        """
        pass

    @abstractmethod
    def descargar_registros(self, ids: Set[str], ruta_destino: str) -> bool:
        """
        Ejecuta la extracción contra el servidor remoto y persiste
        los resultados crudos en data/raw. Retorna True si la ejecución fue exitosa.
        """
        pass