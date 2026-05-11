from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app as backend_app  # noqa: E402


class ApiPrefixMiddleware:
    def __init__(self, wrapped_app):
        self.wrapped_app = wrapped_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/api"):
            scope = dict(scope)
            scope["root_path"] = f'{scope.get("root_path", "")}/api'
            scope["path"] = scope["path"][4:] or "/"
        await self.wrapped_app(scope, receive, send)


app = ApiPrefixMiddleware(backend_app)
