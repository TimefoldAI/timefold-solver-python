from .._timefold_java_interop import ensure_init
from typing import TYPE_CHECKING
from decimal import Decimal
if TYPE_CHECKING:
    from ai.timefold.solver.core.api.domain.valuerange import CountableValueRange


class ValueRangeFactory:
    # Return cannot be typed, since CountableValueRange does not exist in the globals dict
    # since it is loaded lazily (to not start the JVM prematurely)
    @staticmethod
    def create_int_value_range(start: int, end: int, step: int = None):
        ensure_init()
        import jpype.imports
        from ai.timefold.solver.python import PythonValueRangeFactory
        from java.math import BigInteger
        if step is None:
            return PythonValueRangeFactory.createIntValueRange(BigInteger(str(start)), BigInteger(str(end)))
        else:
            return PythonValueRangeFactory.createIntValueRange(BigInteger(str(start)), BigInteger(str(end)),
                                                               BigInteger(str(step)))

    @staticmethod
    def create_float_value_range(start: Decimal, end: Decimal, step: Decimal = None):
        ensure_init()
        import jpype.imports
        from ai.timefold.solver.python import PythonValueRangeFactory
        from java.math import BigDecimal
        if step is None:
            return PythonValueRangeFactory.createFloatValueRange(BigDecimal(str(start)), BigDecimal(str(end)))
        else:
            return PythonValueRangeFactory.createFloatValueRange(BigDecimal(str(start)), BigDecimal(str(end)),
                                                                 BigDecimal(str(step)))

    @staticmethod
    def create_bool_value_range():
        ensure_init()
        import jpype.imports
        from ai.timefold.solver.python import PythonValueRangeFactory
        return PythonValueRangeFactory.createBooleanValueRange()


def lookup_value_range_class(name: str):
    ensure_init()
    import jpype.imports
    from ai.timefold.solver.core.api.domain.valuerange import CountableValueRange
    match name:
        case 'CountableValueRange':
            return CountableValueRange

        case _:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ['ValueRangeFactory']
