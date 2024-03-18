from decimal import Decimal
from ..timefold_java_interop import ensure_init
import jpype.imports # noqa

ensure_init()

from ai.timefold.solver.core.api.domain.valuerange import CountableValueRange
from ai.timefold.solver.python import PythonValueRangeFactory


class ValueRangeFactory:
    @staticmethod
    def create_int_value_range(start: int, end: int, step: int = None) -> CountableValueRange:
        from java.math import BigInteger
        if step is None:
            return PythonValueRangeFactory.createIntValueRange(BigInteger(str(start)), BigInteger(str(end)))
        else:
            return PythonValueRangeFactory.createIntValueRange(BigInteger(str(start)), BigInteger(str(end)),
                                                               BigInteger(str(step)))

    @staticmethod
    def create_float_value_range(start: Decimal, end: Decimal, step: Decimal = None) -> CountableValueRange:
        from java.math import BigDecimal
        if step is None:
            return PythonValueRangeFactory.createFloatValueRange(BigDecimal(str(start)), BigDecimal(str(end)))
        else:
            return PythonValueRangeFactory.createFloatValueRange(BigDecimal(str(start)), BigDecimal(str(end)),
                                                                 BigDecimal(str(step)))

    @staticmethod
    def create_bool_value_range() -> CountableValueRange:
        return PythonValueRangeFactory.createBooleanValueRange()


__all__ = ['CountableValueRange', 'ValueRangeFactory']
