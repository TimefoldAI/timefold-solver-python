from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from java.time import Duration as _JavaDuration


@dataclass(kw_only=True)
class Duration:
    milliseconds: int = field(default=0)
    seconds: int = field(default=0)
    minutes: int = field(default=0)
    hours: int = field(default=0)
    days: int = field(default=0)

    def to_milliseconds(self) -> int:
        return self._to_java_duration().toMillis()

    def to_seconds(self) -> int:
        return self._to_java_duration().toSeconds()

    def to_minutes(self) -> int:
        return self._to_java_duration().toMinutes()

    def to_hours(self) -> int:
        return self._to_java_duration().toHours()

    def to_days(self) -> int:
        return self._to_java_duration().toDays()

    @staticmethod
    def _from_java_duration(duration: '_JavaDuration'):
        return Duration(
            milliseconds=duration.toMillis()
        )

    def _to_java_duration(self) -> '_JavaDuration':
        from java.time import Duration
        return (Duration.ZERO
                .plusMillis(self.milliseconds)
                .plusSeconds(self.seconds)
                .plusMinutes(self.minutes)
                .plusHours(self.hours)
                .plusDays(self.days)
                )


__all__ = ['Duration']
