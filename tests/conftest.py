from __future__ import annotations

import sys
from pathlib import Path

# Allow tests to import the package without installing it.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
