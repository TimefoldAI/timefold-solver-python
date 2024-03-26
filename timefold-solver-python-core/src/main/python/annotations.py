import jpype

from .timefold_java_interop import ensure_init, _generate_constraint_provider_class, \
    _generate_incremental_score_calculator_class, \
    _generate_variable_listener_class
from jpyinterpreter import JavaAnnotation
from jpype import JImplements, JOverride
from typing import Union, List, Callable, Type, TYPE_CHECKING, TypeVar
from .constraint_stream import BytecodeTranslation

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.solver.change import ProblemChange as _ProblemChange
    from ai.timefold.solver.core.api.score.stream import Constraint as _Constraint, ConstraintFactory as _ConstraintFactory
    from ai.timefold.solver.core.api.score import Score as _Score
    from ai.timefold.solver.core.api.score.calculator import IncrementalScoreCalculator as _IncrementalScoreCalculator
    from ai.timefold.solver.core.api.domain.variable import PlanningVariableGraphType as _PlanningVariableGraphType, \
        VariableListener as _VariableListener


Solution_ = TypeVar('Solution_')


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
                 graph_type: '_PlanningVariableGraphType' = None):
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
                 allows_unassigned: bool = False):
        ensure_init()
        from ai.timefold.solver.core.api.domain.variable import PlanningListVariable as JavaPlanningListVariable
        super().__init__(JavaPlanningListVariable,
                         {
                             'valueRangeProviderRefs': value_range_provider_refs,
                             # TODO: When updated to 1.8.0, add allowsUnassigned
                             #'allowsUnassigned': allows_unassigned
                         })


class PlanningVariableReference(JavaAnnotation):
    def __init__(self, *,
                 entity_class: Type = None,
                 variable_name: str):
        ensure_init()
        from ai.timefold.solver.core.api.domain.variable import (
            PlanningVariableReference as JavaPlanningVariableReference)
        super().__init__(JavaPlanningVariableReference,
                         {
                             'variableName': variable_name,
                             'entityClass': entity_class,
                         })


class ShadowVariable(JavaAnnotation):
    def __init__(self, *,
                 variable_listener_class: Type['_VariableListener'] = None,
                 source_variable_name: str,
                 source_entity_class: Type = None):
        ensure_init()
        from .timefold_java_interop import get_class
        from ai.timefold.jpyinterpreter import PythonClassTranslator
        from ai.timefold.solver.core.api.domain.variable import (
            ShadowVariable as JavaShadowVariable)
        super().__init__(JavaShadowVariable,
                         {
                             'variableListenerClass': get_class(variable_listener_class),
                             'sourceVariableName': PythonClassTranslator.getJavaFieldName(source_variable_name),
                             'sourceEntityClass': source_entity_class,
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
        from .timefold_java_interop import _generate_planning_entity_class
        from ai.timefold.solver.core.api.domain.entity import PinningFilter
        from jpyinterpreter import add_class_annotation, translate_python_bytecode_to_java_bytecode
        from typing import get_type_hints, get_origin, Annotated
        type_hints = get_type_hints(entity_class_argument, include_extras=True)
        planning_pin_field = None
        for name, type_hint in type_hints.items():
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
        _generate_planning_entity_class(out)
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
    from .timefold_java_interop import _generate_planning_solution_class
    from ai.timefold.solver.core.api.domain.solution import PlanningSolution as JavaPlanningSolution
    out = add_class_annotation(JavaPlanningSolution)(planning_solution_class)
    _generate_planning_solution_class(planning_solution_class)
    return out


def constraint_provider(constraint_provider_function: Callable[['_ConstraintFactory'], List['_Constraint']] = None, /, *,
                        function_bytecode_translation: BytecodeTranslation = BytecodeTranslation.IF_POSSIBLE) -> \
        Union[Callable[[Callable], Callable[['_ConstraintFactory'], List['_Constraint']]],
              Callable[['_ConstraintFactory'], List['_Constraint']]]:
    """Marks a function as a ConstraintProvider.

    The function takes a single parameter, the ConstraintFactory, and
    must return a list of Constraints.
    To create a Constraint, start with ConstraintFactory.from(get_class(PythonClass)).

    :param function_bytecode_translation: Specifies how bytecode translator should occur.
                                          Defaults to BytecodeTranslation.IF_POSSIBLE.
    :type constraint_provider_function: Callable[[ConstraintFactory], List[Constraint]]
    :rtype: Callable[[ConstraintFactory], List[Constraint]]
    """
    ensure_init()

    def constraint_provider_wrapper(function):
        def wrapped_constraint_provider(constraint_factory):
            from . import constraint_stream
            try:
                constraint_stream.convert_to_java = function_bytecode_translation
                out = function(constraint_stream.PythonConstraintFactory(constraint_factory,
                                                                         function_bytecode_translation))
                return out
            finally:
                constraint_stream.convert_to_java = BytecodeTranslation.IF_POSSIBLE
                constraint_stream.all_translated_successfully = True
        wrapped_constraint_provider.__timefold_java_class = (
            _generate_constraint_provider_class(function, wrapped_constraint_provider))
        return wrapped_constraint_provider

    if constraint_provider_function:  # Called as @constraint_provider
        return constraint_provider_wrapper(constraint_provider_function)
    else:  # Called as @constraint_provider(function_bytecode_translation=True)
        return constraint_provider_wrapper


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
    easy_score_calculator_function.__timefold_java_class = \
        generate_proxy_class_for_translated_function(EasyScoreCalculator,
            translate_python_bytecode_to_java_bytecode(easy_score_calculator_function, EasyScoreCalculator))
    return easy_score_calculator_function


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
    incremental_score_calculator.__timefold_java_class = generate_proxy_class_for_translated_class(base_interface, translated_class)
    return incremental_score_calculator


def variable_listener(variable_listener_class: Type['_VariableListener'] = None, /, *,
                      require_unique_entity_events: bool = False) -> Type['_VariableListener']:
    """Changes shadow variables when a genuine planning variable changes.
    Important: it must only change the shadow variable(s) for which it's configured!
    It should never change a genuine variable or a problem fact.
    It can change its shadow variable(s) on multiple entity instances
    (for example: an arrival_time change affects all trailing entities too).

    It is recommended that implementations be kept stateless.
    If state must be implemented, implementations may need to override the default methods
    resetWorkingSolution(score_director: ScoreDirector) and close().

    The following methods must exist:

    def beforeEntityAdded(score_director: ScoreDirector[Solution_], entity: Entity_);

    def afterEntityAdded(score_director: ScoreDirector[Solution_], entity: Entity_);

    def beforeEntityRemoved(score_director: ScoreDirector[Solution_], entity: Entity_);

    def afterEntityRemoved(score_director: ScoreDirector[Solution_], entity: Entity_);

    def beforeVariableChanged(score_director: ScoreDirector[Solution_], entity: Entity_);

    def afterVariableChanged(score_director: ScoreDirector[Solution_], entity: Entity_);

    If the implementation is stateful, then the following methods should also be defined:

    def resetWorkingSolution(score_director: ScoreDirector)

    def close()

    :param require_unique_entity_events: Set to True to guarantee that each of the before/after methods will only be
                                         called once per entity instance per operation type (add, change or remove).
                                         When set to True, this has a slight performance loss.
                                         When set to False, it's often easier to make the listener implementation
                                         correct and fast.
                                         Defaults to False

    :type variable_listener_class: '_VariableListener'
    :type require_unique_entity_events: bool
    :rtype: Type
    """
    ensure_init()

    def variable_listener_wrapper(the_variable_listener_class):
        from jpyinterpreter import translate_python_class_to_java_class, generate_proxy_class_for_translated_class
        from ai.timefold.solver.core.api.domain.variable import VariableListener
        methods = ['beforeEntityAdded',
                   'afterEntityAdded',
                   'beforeVariableChanged',
                   'afterVariableChanged',
                   'beforeEntityRemoved',
                   'afterEntityRemoved']

        missing_method_list = []
        for method in methods:
            if not callable(getattr(the_variable_listener_class, method, None)):
                missing_method_list.append(method)
        if len(missing_method_list) != 0:
            raise ValueError(f'The following required methods are missing from @variable_listener class '
                             f'{the_variable_listener_class}: {missing_method_list}')

        method_on_class = getattr(the_variable_listener_class, 'requiresUniqueEntityEvents', None)
        if method_on_class is None:
            def class_requires_unique_entity_events(self):
                return require_unique_entity_events

            setattr(the_variable_listener_class, 'requiresUniqueEntityEvents', class_requires_unique_entity_events)


        method_on_class = getattr(the_variable_listener_class, 'close', None)
        if method_on_class is None:
            def close(self):
                pass

            setattr(the_variable_listener_class, 'close', close)

        method_on_class = getattr(the_variable_listener_class, 'resetWorkingSolution', None)
        if method_on_class is None:
            def reset_working_solution(self, score_director):
                pass

            setattr(the_variable_listener_class, 'resetWorkingSolution', reset_working_solution)

        translated_class = translate_python_class_to_java_class(the_variable_listener_class)
        the_variable_listener_class.__timefold_java_class = generate_proxy_class_for_translated_class(VariableListener, translated_class)
        return the_variable_listener_class

    if variable_listener_class:  # Called as @variable_listener
        return variable_listener_wrapper(variable_listener_class)
    else:  # Called as @variable_listener(require_unique_entity_events=True)
        return variable_listener_wrapper


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
