"""Root conftest.py – ensures repo root is on sys.path before any test collection."""
import sys
from pathlib import Path


def pytest_configure(config):
    """Inject repo root into sys.path at the earliest pytest hook."""
    root = str(Path(__file__).parent)
    if root not in sys.path:
        sys.path.insert(0, root)
