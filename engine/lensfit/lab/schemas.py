"""Pydantic schemas for the optics lab API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ExperimentListItem(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    linked_concepts: list[str]
    linked_formulas: list[str]
    prerequisites: list[str]
    learning_objectives: list[str]
    parameters: list[dict[str, Any]]


class ExperimentListResponse(BaseModel):
    items: list[ExperimentListItem]


class ExperimentRunRequest(BaseModel):
    params: dict[str, Any] = {}


class ExperimentRunResponse(BaseModel):
    data: dict[str, Any]
    svg: str
    warnings: list[str]
    learning_hints: list[str]
