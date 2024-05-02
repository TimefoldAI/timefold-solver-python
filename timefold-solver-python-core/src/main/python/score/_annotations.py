from ._constraint_factory import ConstraintFactory
from ._constraint_builder import Constraint
from .._timefold_java_interop import ensure_init, _generate_constraint_provider_class, register_java_class
from typing import TypeVar, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..score import Score

Solution_ = TypeVar('Solution_')


def constraint_provider(constraint_provider_function: Callable[[ConstraintFactory], list[Constraint]], /) \
        -> Callable[[ConstraintFactory], list[Constraint]]:
    ensure_init()

    def constraint_provider_wrapper(function):
        def wrapped_constraint_provider(constraint_factory):
            from ..score import ConstraintFactory
            out = function(ConstraintFactory(constraint_factory))
            return out
        java_class = _generate_constraint_provider_class(function, wrapped_constraint_provider)
        return register_java_class(wrapped_constraint_provider, java_class)

    return constraint_provider_wrapper(constraint_provider_function)


def easy_score_calculator(easy_score_calculator_function: Callable[[Solution_], 'Score']) -> \
        Callable[[Solution_], 'Score']:
    """Used for easy python Score calculation. This is non-incremental calculation, which is slow.

    The function takes a single parameter, the Solution, and
    must return a Score compatible with the Solution Score Type.
    An implementation must be stateless.

    :type easy_score_calculator_function: Callable[[Solution_], '_Score']
    :rtype: Callable[[Solution_], '_Score']
    """
    ensure_init()
    from jpyinterpreter import translate_python_bytecode_to_java_bytecode, generate_proxy_class_for_translated_function
    from ai.timefold.solver.core.api.score.calculator import EasyScoreCalculator
    java_class = generate_proxy_class_for_translated_function(EasyScoreCalculator,
                                                              translate_python_bytecode_to_java_bytecode(
                                                                  easy_score_calculator_function, EasyScoreCalculator))
    return register_java_class(easy_score_calculator_function, java_class)


__all__ = ['constraint_provider', 'easy_score_calculator']
