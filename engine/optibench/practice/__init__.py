"""Practice domain — unified interface for learning-referenced practice activities."""

from optibench.practice.base import PracticeActivity, PracticeRegistry, get_practice_registry

__all__ = [
    "PracticeActivity",
    "PracticeRegistry",
    "get_practice_registry",
]
