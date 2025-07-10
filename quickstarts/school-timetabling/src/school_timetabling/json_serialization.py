from timefold.solver.score import HardSoftScore
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, BeforeValidator, PlainValidator, ValidationInfo
from pydantic.alias_generators import to_camel
from typing import Annotated, Any


def make_list_item_validator(key: str):
    def validator(v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return None

        if not isinstance(v, str) or not info.context:
            return v

        return info.context.get(key)[v]

    return BeforeValidator(validator)


RoomDeserializer = make_list_item_validator('rooms')
TimeslotDeserializer = make_list_item_validator('timeslots')

IdSerializer = PlainSerializer(lambda item: item.id if item is not None else None,
                               return_type=str | None)
ScoreSerializer = PlainSerializer(lambda score: str(score) if score is not None else None,
                                  return_type=str | None)


def validate_score(v: Any, info: ValidationInfo) -> Any:
    if isinstance(v, HardSoftScore) or v is None:
        return v
    if isinstance(v, str):
        return HardSoftScore.parse(v)
    raise ValueError('"score" should be a string')


ScoreValidator = BeforeValidator(validate_score)


class JsonDomainBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
