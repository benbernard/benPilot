"""Keep the existing CI entry point for the shared bootstrap verifier."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / 'installer/verify_artifact.py'), run_name='__main__')
