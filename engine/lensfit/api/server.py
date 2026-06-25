"""FastAPI server for LensFit engine."""

from __future__ import annotations

import argparse
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from lensfit.api.routers import (
    catalog,
    domains,
    export,
    knowledge,
    lab,
    matching,
    projects,
    visualization,
)
from lensfit.db.models import init_db
from lensfit.domains.industrial import IndustrialVisionModule
from lensfit.domains.infrared import InfraredModule
from lensfit.domains.microscope import MicroscopyModule
from lensfit.domains.photography import PhotographyModule
from lensfit.matching.engine import MatchingEngine

# Global instances — kept for backwards compatibility with tests that patch the
# module-level globals before creating a TestClient.
_engine = None
_session_maker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global _engine, _session_maker
    # Skip initialization if a session maker is already set (e.g., in tests),
    # but always mirror the instances onto app.state so dependencies can access
    # them without relying on module-level globals (which may differ when the
    # server is started with ``python -m lensfit.api.server`` vs imported in
    # tests).
    if _session_maker is not None:
        app.state.session_maker = _session_maker
        if _engine is not None:
            app.state.engine = _engine
        yield
        return

    db_url = getattr(app.state, "db_url", None) or "sqlite:///lensfit.db"

    init_db(db_url)

    # SQLite requires check_same_thread=False for use in FastAPI thread pool.
    # Memory databases keep the shared StaticPool so the in-memory DB survives
    # across connections; file databases use NullPool to avoid pinning a single
    # connection and to make shutdown/dispose reliable.
    is_memory = ":memory:" in db_url
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool if is_memory else NullPool
    db_engine = create_engine(
        db_url,
        echo=False,
        connect_args=connect_args,
        poolclass=poolclass,
    )

    if not is_memory:
        # WAL improves concurrent read/write on the local desktop database.
        with db_engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))

    _session_maker = sessionmaker(bind=db_engine)

    _engine = MatchingEngine(_session_maker)
    _engine.register_domain(IndustrialVisionModule())
    _engine.register_domain(MicroscopyModule())
    _engine.register_domain(InfraredModule())
    _engine.register_domain(PhotographyModule())

    app.state.session_maker = _session_maker
    app.state.engine = _engine
    app.state.db_engine = db_engine

    # In desktop mode, expose the API key to the local sidecar supervisor via stdout
    # so the Tauri host can forward it to the frontend without leaking it over HTTP.
    if getattr(app.state, "mode", None) == "desktop":
        print(f"LENSFIT_API_KEY {_API_KEY}", flush=True)

    yield
    if _engine is not None:
        try:
            _engine.shutdown()
        except Exception:
            pass
        _engine = None
    if getattr(app.state, "db_engine", None) is not None:
        app.state.db_engine.dispose()
        app.state.db_engine = None
    _session_maker = None
    app.state.session_maker = None
    app.state.engine = None


# API Key — generated at startup if not provided via env
_API_KEY = os.environ.get("LENSFIT_API_KEY") or os.urandom(32).hex()


def verify_api_key(request: Request) -> None:
    """Verify X-API-Key header for non-health endpoints in desktop mode."""
    if request.url.path == "/health":
        return
    # In dev/web mode we rely on local network/CORS instead of the API key.
    if getattr(request.app.state, "mode", "desktop") != "desktop":
        return
    key = request.headers.get("X-API-Key")
    if key != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app = FastAPI(
    title="LensFit Engine API",
    version="1.1.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)

# CORS: only allow known local origins for desktop/web dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",   # Vite dev
        "http://localhost:5173",   # Vite dev fallback
        "http://localhost:1420",   # Tauri dev
        "http://localhost:3000",   # Alternative dev
        "tauri://localhost",       # Tauri production
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# Routers
app.include_router(catalog.router)
app.include_router(domains.router)
app.include_router(matching.router)
app.include_router(knowledge.router)
app.include_router(visualization.router)
app.include_router(projects.router)
app.include_router(lab.router)
app.include_router(export.router)


# =====================================================================
# Health
# =====================================================================
@app.get("/health")
def health_check():
    """Health check endpoint — Sidecar Supervisor polls this."""
    return {"status": "ok", "version": "1.1.0"}


# =====================================================================
# CLI Entry
# =====================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--mode", type=str, default="desktop")
    parser.add_argument("--db", type=str, default="sqlite:///lensfit.db")
    args = parser.parse_args()

    app.state.db_url = args.db
    app.state.mode = args.mode

    import uvicorn
    # Pass the app object directly so uvicorn does not re-import the module
    # and discard state (e.g. mode/db_url) set above.
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
