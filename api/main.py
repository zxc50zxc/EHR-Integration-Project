from pathlib import Path
import sys

from fastapi import FastAPI

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app as backend_app  # noqa: E402

app = FastAPI(title="EHR Integration API")
app.mount("/api", backend_app)
app.mount("/", backend_app)
