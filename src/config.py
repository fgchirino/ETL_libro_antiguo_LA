from pathlib import Path

# 1. Identificar la ruta absoluta del archivo actual (src/config.py)
_SRC_DIR = Path(__file__).resolve().parent

# 2. La raíz del proyecto es exactamente un nivel arriba de src/
PROJECT_ROOT = _SRC_DIR.parent

# 3. Definir rutas relativas a los directorios del proyecto usando pathlib (/)
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESADA_DIR = PROJECT_ROOT / "data" / "procesada"
CONFIG_DIR = PROJECT_ROOT / "config"

# Rutas heredadas del notebook original que podríamos necesitar
LOGS_DIR = PROJECT_ROOT / "logs"