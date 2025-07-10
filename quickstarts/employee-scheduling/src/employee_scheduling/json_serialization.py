from timefold.solver.score import HardSoftDecimalScore
from typing import Any
from pydantic import BaseModel, ConfigDict, PlainSerializer, BeforeValidator
from pydantic.alias_generators import to_camel

ScoreSerializer = PlainSerializer(lambda score: str(score) if score is not None else None, return_type=str | None)


def validate_score(v: Any) -> Any:
    if isinstance(v, HardSoftDecimalScore) or v is None:
        return v
    if isinstance(v, str):
        return HardSoftDecimalScore.parse(v)
    raise ValueError('"score" should be a string')


ScoreValidator = BeforeValidator(validate_score)


class JsonDomainBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
