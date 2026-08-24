"""OptiBench - Optical Lens & Detector Matching Engine."""

__version__ = "0.1.0"

from optibench.core.types import MatchingTask, MatchResult, OpticalParams
from optibench.domains.base import DomainModule
from optibench.matching.engine import MatchingEngine

__all__ = [
    "MatchingEngine",
    "DomainModule",
    "MatchResult",
    "MatchingTask",
    "OpticalParams",
]
