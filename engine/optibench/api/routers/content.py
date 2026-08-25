"""Content API endpoints — serves the module concept index (content contract v1)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from optibench.content.contract import ConceptMeta
from optibench.content.loader import get_content_index
from optibench.content.quiz import get_quiz_index

router = APIRouter(prefix="/api/v1/content", tags=["content"])


class ContentIndexErrorItem(BaseModel):
    path: str
    error: str


class ConceptListResponse(BaseModel):
    items: list[ConceptMeta]
    errors: list[ContentIndexErrorItem]


class ConceptDetail(ConceptMeta):
    body: str


@router.get("/concepts", response_model=ConceptListResponse)
def list_concepts():
    """List all indexed concepts (metadata only, no bodies)."""
    index = get_content_index()
    return {
        "items": index.list_concepts(),
        "errors": [{"path": e.path, "error": e.error} for e in index.errors],
    }


@router.get("/concepts/{concept_id}", response_model=ConceptDetail)
def get_concept(concept_id: str):
    """Get a single concept with its markdown body."""
    index = get_content_index()
    meta = index.get(concept_id)
    body = index.get_body(concept_id)
    if meta is None or body is None:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_id}")
    return ConceptDetail(**meta.model_dump(), body=body)


class QuizQuestionItem(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class QuizItem(BaseModel):
    id: str
    title: str
    module: str
    concepts: list[str]
    pass_score: int
    questions: list[QuizQuestionItem]


class QuizListResponse(BaseModel):
    items: list[QuizItem]
    errors: list[ContentIndexErrorItem]


def _quiz_item(quiz) -> QuizItem:
    return QuizItem(
        id=quiz.id,
        title=quiz.title,
        module=quiz.module,
        concepts=quiz.concepts,
        pass_score=quiz.pass_score,
        questions=[QuizQuestionItem(**vars(q)) for q in quiz.questions],
    )


@router.get("/quizzes", response_model=QuizListResponse)
def list_quizzes(concept: str | None = None):
    """List all indexed quizzes; ``?concept=<id>`` filters by linked concept."""
    index = get_quiz_index()
    quizzes = (
        index.for_concept(concept) if concept is not None else index.list_quizzes()
    )
    return {
        "items": [_quiz_item(q) for q in quizzes],
        "errors": [{"path": e.path, "error": e.error} for e in index.errors],
    }


@router.get("/quizzes/{quiz_id}", response_model=QuizItem)
def get_quiz(quiz_id: str):
    """Get a single quiz with its questions."""
    quiz = get_quiz_index().get(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail=f"Quiz not found: {quiz_id}")
    return _quiz_item(quiz)
