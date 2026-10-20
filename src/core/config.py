"""Caminhos e constantes de configuração, resolvidos a partir da raiz do repo.

Diferente do legado (que usava caminhos relativos frágeis), tudo aqui é
derivado de `PROJECT_ROOT`, então o app funciona de qualquer diretório.
"""

from pathlib import Path

# src/core/config.py -> sobe dois níveis até a raiz do projeto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data em runtime (gitignored): brutos colados, snapshot e exportações.
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXPORTS_DIR = DATA_DIR / "exports"
SNAPSHOT_FILE = DATA_DIR / "hora_a_hora_snapshot.json"

# Planilha corporativa de metas (mesmo layout do PDV_V2).
METAS_FILE = PROJECT_ROOT / "metas" / "metas.xlsx"

# Loja padrão da operação (Torre Shopping); as 17 lojas do E-Store usadas
# nos dropdowns — mesma lista de legacy/atualizarEstore.py.
DEFAULT_STORE = "L062"
E_STORE_STORES = [
    "L025", "L051", "L054", "L056", "L057", "L059", "L061", "L062", "L194",
    "L201", "L287", "L306", "L313", "L316", "L326", "L391", "L393",
]
