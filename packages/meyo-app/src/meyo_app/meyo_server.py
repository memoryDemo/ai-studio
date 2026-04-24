from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from meyo import version
from meyo_app.config import AppConfig, load_app_config


def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI(
        title="Meyo",
        description="Minimal Meyo webserver",
        version=version,
    )

    @app.get("/api/healthz")
    async def healthz() -> dict[str, object]:
        return {
            "status": "ok",
            "host": config.web.host,
            "port": config.web.port,
            "config_path": str(config.path),
        }

    @app.get("/api/hello")
    async def hello() -> dict[str, str]:
        return {"message": "Hello from Meyo!"}

    static_dir = Path(__file__).resolve().parent / "static" / "web"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app


def run_webserver(config_file: Optional[str] = None) -> None:
    import uvicorn

    config = load_app_config(config_file)
    uvicorn.run(
        create_app(config),
        host=config.web.host,
        port=config.web.port,
    )
