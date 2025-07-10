from dataclasses import dataclass
from typing import Annotated

from .json_serialization import *


@dataclass
class MatchAnalysisDTO:
    name: str
    score: Annotated[HardSoftScore, ScoreSerializer]
    justification: object


@dataclass
class ConstraintAnalysisDTO:
    name: str
    weight: Annotated[HardSoftScore, ScoreSerializer]
    matches: list[MatchAnalysisDTO]
    score: Annotated[HardSoftScore, ScoreSerializer]
