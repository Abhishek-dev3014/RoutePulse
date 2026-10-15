"""Export FastAPI OpenAPI; regenerate the web domain types with openapi-typescript."""

import json
from pathlib import Path
from app.main import app

Path("data/openapi.json").write_text(json.dumps(app.openapi(), indent=2))
