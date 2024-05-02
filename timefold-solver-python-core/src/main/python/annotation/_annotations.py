import jpype

from .._jpype_type_conversions import PythonSupplier
from ..api import VariableListener
from ..constraint import ConstraintFactory
from .._timefold_java_interop import ensure_init, _generate_constraint_provider_class, register_java_class, get_asm_type
from jpyinterpreter import JavaAnnotation, AnnotationValueSupplier
from jpype import JImplements, JOverride
from typing import Union, List, Callable, Type, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.solver.change import ProblemChange as _ProblemChange
    from ai.timefold.solver.core.api.score.stream import Constraint as _Constraint
    from ai.timefold.solver.core.api.score import Score as _Score
    from ai.timefold.solver.core.api.score.calculator import IncrementalScoreCalculator as _IncrementalScoreCalculator
    from ai.timefold.solver.core.api.domain.variable import PlanningVariableGraphType as _PlanningVariableGraphType


Solution_ = TypeVar('Solution_')
Origin_ = TypeVar('Origin_')
Destination_ = TypeVar('Destination_')


class PlanningId(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.lookup import PlanningId as JavaPlanningId
        super().__init__(JavaPlanningId, {})


class PlanningPin:
    pass


class PlanningVariable(JavaAnnotation):
    def __init__(self, *,
                 value_range_provider_refs: List[str] = None,
                 allows_unassigned: bool = False,
                 graph_type=None):
        ensure_init()
        from ai.timefold.solver.core.api.domain.variable import PlanningVariable as JavaPlanningVariable
        super().__init__(JavaPlanningVariable,
                         {
                             'valueRangeProviderRefs': value_range_provider_refs,
                             'graphType': graph_type,
                             'allowsUnassigned': allows_unassigned
                         })


class PlanningListVariable(JavaAnnotation):
    def __init__(self, *,
                 value_range_provider_refs: List[str] = None,
                 allows_unassigned_values: bool = False):
        ensure_init()
        from ai.timefold.solver.core.api.domain.variable import PlanningListVariable as JavaPlanningListVariable
        super().__init__(JavaPlanningListVariable,
                         {
                             'valueRangeProviderRefs': value_range_provider_refs,
                             'allowsUnassignedValues': allows_unassigned_values
                         })


class ShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 variable_listener_class: Type[VariableListener] = None,
                 source_variable_name: str,
                 source_entity_class: Type = None):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import ShadowVariable as JavaShadowVariable

        super().__init__(JavaShadowVariable,
                         {
                             'variableListenerClass': AnnotationValueSupplier(
                                 lambda: get_asm_type(variable_listener_class)),
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name),
                             'sourceEntityClass': source_entity_class,
                         })


class PiggybackShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 shadow_variable_name: str,
                 shadow_entity_class: Type = None):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            PiggybackShadowVariable as JavaPiggybackShadowVariable)
        super().__init__(JavaPiggybackShadowVariable,
                         {
                             'shadowVariableName': PythonClassTranslator.getJavaFieldName(shadow_variable_name),
                             'shadowEntityClass': shadow_entity_class,
                         })


class IndexShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 source_variable_name: str):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            IndexShadowVariable as JavaIndexShadowVariable)
        super().__init__(JavaIndexShadowVariable,
                         {
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name)
                         })


class PreviousElementShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 source_variable_name: str):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            PreviousElementShadowVariable as JavaPreviousElementShadowVariable)
        super().__init__(JavaPreviousElementShadowVariable,
                         {
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name)
                         })


class NextElementShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 source_variable_name: str):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            NextElementShadowVariable as JavaNextElementShadowVariable)
        super().__init__(JavaNextElementShadowVariable,
                         {
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name)
                         })


class AnchorShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 source_variable_name: str):
        ensure_init()
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            AnchorShadowVariable as JavaAnchorShadowVariable)
        super().__init__(JavaAnchorShadowVariable,
                         {
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name)
                         })


class InverseRelationShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 source_variable_name: str):
        ensure_init()
        from ai.timefold.solver.core.api.domain.variable import (
            InverseRelationShadowVariable as JavaInverseRelationShadowVariable)
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        super().__init__(JavaInverseRelationShadowVariable,
                         {
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name)
                         })


class ProblemFactProperty(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution import (
            ProblemFactProperty as JavaProblemFactProperty)
        super().__init__(JavaProblemFactProperty, {})


class ProblemFactCollectionProperty(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution import (
            ProblemFactCollectionProperty as JavaProblemFactCollectionProperty)
        super().__init__(JavaProblemFactCollectionProperty, {})


class PlanningEntityProperty(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution import (
            PlanningEntityProperty as JavaPlanningEntityProperty)
        super().__init__(JavaPlanningEntityProperty, {})


class PlanningEntityCollectionProperty(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution import (
            PlanningEntityCollectionProperty as JavaPlanningEntityCollectionProperty)
        super().__init__(JavaPlanningEntityCollectionProperty, {})


class ValueRangeProvider(JavaAnnotation):
    def __init__(self, *, id: str = None):
        ensure_init()
        from ai.timefold.solver.core.api.domain.valuerange import (
            ValueRangeProvider as JavaValueRangeProvider)
        super().__init__(JavaValueRangeProvider, {
            'id': id
        })


class PlanningScore(JavaAnnotation):
    def __init__(self, *,
                 bendable_hard_levels_size: int = None,
                 bendable_soft_levels_size: int = None):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution import (
            PlanningScore as JavaPlanningScore)
        super().__init__(JavaPlanningScore,
                         {
                             'bendableHardLevelsSize': bendable_hard_levels_size,
                             'bendableSoftLevelsSize': bendable_soft_levels_size
                         })


class DeepPlanningClone(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.solution.cloner import (
            DeepPlanningClone as JavaDeepPlanningClone)
        super().__init__(JavaDeepPlanningClone, {})


class ConstraintConfigurationProvider(JavaAnnotation):
    def __init__(self):
        ensure_init()
        from ai.timefold.solver.core.api.domain.constraintweight import (
            ConstraintConfigurationProvider as JavaConstraintConfigurationProvider)
        super().__init__(JavaConstraintConfigurationProvider, {})


class ConstraintWeight(JavaAnnotation):
    def __init__(self, constraint_name: str, *, constraint_package: str = None):
        ensure_init()
        from ai.timefold.solver.core.api.domain.constraintweight import ConstraintWeight as JavaConstraintWeight
        super().__init__(JavaConstraintWeight, {
            'value': constraint_name,
            'constraintPackage': constraint_package
        })


@JImplements('ai.timefold.solver.core.api.domain.entity.PinningFilter', deferred=True)
class _PythonPinningFilter:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def accept(self, solution, entity):
        return self.delegate(solution, entity)


def planning_entity(entity_class: Type = None, /, *, pinning_filter: Callable = None) -> Union[Type,
                                                                                               Callable[[Type], Type]]:
    """Specifies that the class is a planning entity. Each planning entity must have at least
    1 PlanningVariable property.

    The class MUST allow passing None to all of __init__ arguments, so it can be cloned.
    (ex: this is allowed:

    def __init__(self, a_list):
        self.a_list = a_list

    this is NOT allowed:

    def __init__(self, a_list):
        self.a_list = a_list
        self.list_length = len(a_list)
    )

    Optional Parameters: @:param pinning_filter: A function that takes the @planning_solution class and an entity,
    and return true if the entity cannot be changed, false otherwise
    """
    ensure_init()
    from ai.timefold.solver.core.api.domain.entity import PlanningEntity as JavaPlanningEntity

    def planning_entity_wrapper(entity_class_argument):
        from .._timefold_java_interop import _add_to_compilation_queue
        from ai.timefold.solver.core.api.domain.entity import PinningFilter
        from jpyinterpreter import add_class_annotation, translate_python_bytecode_to_java_bytecode
        from typing import get_origin, Annotated

        planning_pin_field = None
        for name, type_hint in entity_class_argument.__annotations__.items():
            if get_origin(type_hint) == Annotated:
                for metadata in type_hint.__metadata__:
                    if metadata == PlanningPin or isinstance(metadata, PlanningPin):
                        if planning_pin_field is not None:
                            raise ValueError(f'Only one attribute can be annotated with PlanningPin, '
                                             f'but found multiple fields ({planning_pin_field} and {name}).')
                        planning_pin_field = name

        pinning_filter_function = None
        if pinning_filter is not None:
            if planning_pin_field is not None:
                pinning_filter_function = lambda solution, entity: (getattr(entity, planning_pin_field, False) or
                                                                    pinning_filter(solution, entity))
            else:
                pinning_filter_function = pinning_filter
        else:
            if planning_pin_field is not None:
                pinning_filter_function = lambda solution, entity: getattr(entity, planning_pin_field, False)

        out = add_class_annotation(JavaPlanningEntity,
                                   pinningFilter=pinning_filter_function)(entity_class_argument)
        _add_to_compilation_queue(out)
        return out

    if entity_class:  # Called as @planning_entity
        return planning_entity_wrapper(entity_class)
    else:  # Called as @planning_entity(pinning_filter=some_function)
        return planning_entity_wrapper


def planning_solution(planning_solution_class: Type[Solution_]) -> Type[Solution_]:
    """Specifies that the class is a planning solution (represents a problem and a possible solution of that problem).

    A possible solution does not need to be optimal or even feasible.
    A solution's planning variables might not be initialized (especially when delivered as a problem).

    A solution is mutable. For scalability reasons (to facilitate incremental score calculation),
    the same solution instance (called the working solution per move thread) is continuously modified.
    It's cloned to recall the best solution.

    Each planning solution must have exactly 1 PlanningScore property.
    Each planning solution must have at least 1 PlanningEntityCollectionProperty property.

    The class MUST allow passing None to all of __init__ arguments, so it can be cloned.
    (ex: this is allowed:

    def __init__(self, a_list):
        self.a_list = a_list

    this is NOT allowed:

    def __init__(self, a_list):
        self.a_list = a_list
        self.list_length = len(a_list)
    )
    """
    ensure_init()
    from jpyinterpreter import add_class_annotation
    from .._timefold_java_interop import _add_to_compilation_queue
    from ai.timefold.solver.core.api.domain.solution import PlanningSolution as JavaPlanningSolution
    out = add_class_annotation(JavaPlanningSolution)(planning_solution_class)
    _add_to_compilation_queue(planning_solution_class)
    return out


def constraint_configuration(constraint_configuration_class: Type[Solution_]) -> Type[Solution_]:
    ensure_init()
    from jpyinterpreter import add_class_annotation
    from ai.timefold.solver.core.api.domain.constraintweight import (
        ConstraintConfiguration as JavaConstraintConfiguration)
    out = add_class_annotation(JavaConstraintConfiguration)(constraint_configuration_class)
    return out


def nearby_distance_meter(distance_function: Callable[[Origin_, Destination_], float], /) \
        -> Callable[[Origin_, Destination_], float]:
    ensure_init()
    from jpyinterpreter import translate_python_bytecode_to_java_bytecode, generate_proxy_class_for_translated_function
    from ai.timefold.solver.core.impl.heuristic.selector.common.nearby import NearbyDistanceMeter  # noqa
    java_class = generate_proxy_class_for_translated_function(NearbyDistanceMeter,
                                                              translate_python_bytecode_to_java_bytecode(
                                                                  distance_function,
                                                                  NearbyDistanceMeter))
    return register_java_class(distance_function, java_class)


def constraint_provider(constraint_provider_function: Callable[[ConstraintFactory], List['_Constraint']], /) \
        -> Callable[[ConstraintFactory], List['_Constraint']]:
    ensure_init()

    def constraint_provider_wrapper(function):
        def wrapped_constraint_provider(constraint_factory):
            from ..constraint import ConstraintFactory
            out = function(ConstraintFactory(constraint_factory))
            return out
        java_class = _generate_constraint_provider_class(function, wrapped_constraint_provider)
        return register_java_class(wrapped_constraint_provider, java_class)

    return constraint_provider_wrapper(constraint_provider_function)


def easy_score_calculator(easy_score_calculator_function: Callable[[Solution_], '_Score']) -> \
        Callable[[Solution_], '_Score']:
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


def incremental_score_calculator(incremental_score_calculator: Type['_IncrementalScoreCalculator']) -> \
        Type['_IncrementalScoreCalculator']:
    """Used for incremental python Score calculation. This is much faster than EasyScoreCalculator
    but requires much more code to implement too.

    Any implementation is naturally stateful.

    The following methods must exist:

    def resetWorkingSolution(self, workingSolution: Solution_);

    def beforeEntityAdded(self, entity: any);

    def afterEntityAdded(self, entity: any);

    def beforeVariableChanged(self, entity: any, variableName: str);

    def afterVariableChanged(self, entity: any, variableName: str);

    def beforeEntityRemoved(self, entity: any);

    def afterEntityRemoved(self, entity: any);

    def calculateScore(self) -> Score;

    If you also want to support Constraint Matches, the following methods need to be added:

    def getConstraintMatchTotals(self)

    def getIndictmentMap(self)

    def resetWorkingSolution(self, workingSolution: Solution_, constraintMatchEnabled=False);
    (A default value must be specified in resetWorkingSolution for constraintMatchEnabled)

    :type incremental_score_calculator: '_IncrementalScoreCalculator'
    :rtype: Type
    """
    ensure_init()
    from jpyinterpreter import translate_python_class_to_java_class, generate_proxy_class_for_translated_class
    from ai.timefold.solver.core.api.score.calculator import IncrementalScoreCalculator, \
        ConstraintMatchAwareIncrementalScoreCalculator
    constraint_match_aware = callable(getattr(incremental_score_calculator, 'getConstraintMatchTotals', None)) and \
        callable(getattr(incremental_score_calculator, 'getIndictmentMap', None))
    methods = ['resetWorkingSolution',
               'beforeEntityAdded',
               'afterEntityAdded',
               'beforeVariableChanged',
               'afterVariableChanged',
               'beforeEntityRemoved',
               'afterEntityRemoved',
               'calculateScore']
    base_interface = IncrementalScoreCalculator
    if constraint_match_aware:
        methods.extend(['getIndictmentMap', 'getConstraintMatchTotals'])
        base_interface = ConstraintMatchAwareIncrementalScoreCalculator

    missing_method_list = []
    for method in methods:
        if not callable(getattr(incremental_score_calculator, method, None)):
            missing_method_list.append(method)
    if len(missing_method_list) != 0:
        raise ValueError(f'The following required methods are missing from @incremental_score_calculator class '
                         f'{incremental_score_calculator}: {missing_method_list}')
    # for method in methods:
    #     method_on_class = getattr(incremental_score_calculator, method, None

    translated_class = translate_python_class_to_java_class(incremental_score_calculator)
    java_class = generate_proxy_class_for_translated_class(base_interface, translated_class)
    return register_java_class(incremental_score_calculator, java_class)


def problem_change(problem_change_class: Type['_ProblemChange']) -> \
        Type['_ProblemChange']:
    """A ProblemChange represents a change in 1 or more planning entities or problem facts of a PlanningSolution.
    Problem facts used by a Solver must not be changed while it is solving,
    but by scheduling this command to the Solver, you can change them when the time is right.

    Note that the Solver clones a PlanningSolution at will. Any change must be done on the problem facts and planning
    entities referenced by the PlanningSolution of the ProblemChangeDirector.

    The following methods must exist:

    def doChange(self, workingSolution: Solution_, problemChangeDirector: ProblemChangeDirector)

    :type problem_change_class: '_ProblemChange'
    :rtype: Type
    """
    ensure_init()
    from ai.timefold.solver.core.api.solver.change import ProblemChange
    if not callable(getattr(problem_change_class, 'doChange', None)):
        raise ValueError(f'@problem_change annotated class ({problem_change_class}) does not have required method '
                         f'doChange(self, solution, problem_change_director).')

    class_doChange = getattr(problem_change_class, 'doChange', None)

    def wrapper_doChange(self, solution, problem_change_director):
        run_id = id(problem_change_director)
        solution.forceUpdate()

        reference_map = solution.get__timefold_reference_map()
        python_setter = solution._timefoldPythonSetter

        problem_change_director._set_instance_map(run_id, solution.get__timefold_reference_map())
        problem_change_director._set_update_function(run_id, solution._timefoldPythonSetter)

        class_doChange(self, solution, problem_change_director)

        problem_change_director._unset_instance_map(run_id)
        problem_change_director._unset_update_function(run_id)

        reference_map.clear()
        getattr(solution, "$setFields")(solution.get__timefold_id(), id(solution.get__timefold_id()), reference_map,
                                        python_setter)

    setattr(problem_change_class, 'doChange', JOverride()(wrapper_doChange))
    out = jpype.JImplements(ProblemChange)(problem_change_class)
    return out


__all__ = ['PlanningId', 'PlanningScore', 'PlanningPin', 'PlanningVariable',
           'PlanningListVariable', 'ShadowVariable',
           'PiggybackShadowVariable',
           'IndexShadowVariable', 'PreviousElementShadowVariable', 'NextElementShadowVariable',
           'AnchorShadowVariable', 'InverseRelationShadowVariable',
           'ProblemFactProperty', 'ProblemFactCollectionProperty',
           'PlanningEntityProperty', 'PlanningEntityCollectionProperty',
           'ValueRangeProvider', 'DeepPlanningClone', 'ConstraintConfigurationProvider',
           'ConstraintWeight',
           'planning_entity', 'planning_solution', 'constraint_configuration',
           'nearby_distance_meter',
           'constraint_provider', 'easy_score_calculator', 'incremental_score_calculator',
           'problem_change']
