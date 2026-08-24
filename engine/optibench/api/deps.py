"""Shared FastAPI dependencies for OptiBench API routers."""

from __future__ import annotations

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session


def get_engine(request: Request):
    """Return the application-wide MatchingEngine from app state."""
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return engine


def get_session_maker(request: Request):
    """Return the application-wide SQLAlchemy session maker from app state."""
    session_maker = getattr(request.app.state, "session_maker", None)
    if session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return session_maker


def get_db_session(request: Request):
    """Yield a database session scoped to the request."""
    session_maker = get_session_maker(request)
    session: Session = session_maker()
    try:
        yield session
    finally:
        session.close()
