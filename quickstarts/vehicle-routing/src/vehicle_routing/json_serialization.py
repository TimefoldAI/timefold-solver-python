from timefold.solver.score import HardSoftScore

from typing import Any
from datetime import timedelta
from pydantic import BaseModel, ConfigDict, PlainSerializer, BeforeValidator, ValidationInfo
from pydantic.alias_generators import to_camel


class JsonDomainBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


def make_id_item_validator(key: str):
    def validator(v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return None

        if not isinstance(v, str) or not info.context:
            return v

        return info.context.get(key)[v]

    return BeforeValidator(validator)


def make_id_list_item_validator(key: str):
    def validator(v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return None

        if isinstance(v, (list, tuple)):
            out = []
            for item in v:
                if not isinstance(v, str) or not info.context:
                    return v
                out.append(info.context.get(key)[item])
            return out

        return v

    return BeforeValidator(validator)


LocationSerializer = PlainSerializer(lambda location: [
    location.latitude,
    location.longitude,
], return_type=list[float])
ScoreSerializer = PlainSerializer(lambda score: str(score), return_type=str)
IdSerializer = PlainSerializer(lambda item: item.id if item is not None else None, return_type=str | None)
IdListSerializer = PlainSerializer(lambda items: [item.id for item in items], return_type=list)
DurationSerializer = PlainSerializer(lambda duration: duration // timedelta(seconds=1), return_type=int)

VisitListValidator = make_id_list_item_validator('visits')
VisitValidator = make_id_item_validator('visits')
VehicleValidator = make_id_item_validator('vehicles')


def validate_score(v: Any, info: ValidationInfo) -> Any:
    if isinstance(v, HardSoftScore) or v is None:
        return v
    if isinstance(v, str):
        return HardSoftScore.parse(v)
    raise ValueError('"score" should be a string')


ScoreValidator = BeforeValidator(validate_score)
