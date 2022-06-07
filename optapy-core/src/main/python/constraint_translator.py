import dataclasses

from .optaplanner_java_interop import get_class
from .jpype_type_conversions import _convert_to_java_compatible_object
from .jpype_type_conversions import PythonFunction, PythonBiFunction, PythonTriFunction, PythonQuadFunction, \
     PythonPentaFunction, PythonToIntFunction, PythonToIntBiFunction, PythonToIntTriFunction, PythonToIntQuadFunction
from javapython import translate_python_bytecode_to_java_bytecode
from enum import Enum
import jpype.imports  # noqa
from jpype import JImplements, JOverride, JObject, JClass
import inspect
from typing import TYPE_CHECKING, Type, List, Optional, Callable
if TYPE_CHECKING:
    from org.optaplanner.core.api.score.stream import ConstraintFactory
    from org.optaplanner.core.api.score.stream.uni import UniConstraintStream
    from org.optaplanner.core.api.score.stream.bi import BiConstraintStream, BiJoiner
    from org.optaplanner.core.api.score.stream.tri import TriConstraintStream, TriJoiner
    from org.optaplanner.core.api.score.stream.quad import QuadConstraintStream, QuadJoiner
    from org.optaplanner.core.api.score.stream.penta import PentaJoiner
    from org.optaplanner.core.api.score import Score


class BytecodeTranslation(Enum):
    """
    Specifies how bytecode translation should occur
    """
    FORCE = 'FORCE'
    """
    Forces bytecode translation, raising an error if it is impossible
    """
    IF_POSSIBLE = 'IF_POSSIBLE'
    """
    Use bytecode translation if possible, resorting to original Python implementation if impossible (default)
    """
    NONE = 'NONE'
    """
    Always use original Python implementation; bytecode translation will not occur
    """


function_bytecode_translation: BytecodeTranslation = BytecodeTranslation.IF_POSSIBLE
all_translated_successfully = True

@JImplements('java.util.function.Predicate', deferred=True)
class PythonPredicate:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def test(self, argument):
        return self.delegate(argument)


@JImplements('java.util.function.BiPredicate', deferred=True)
class PythonBiPredicate:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def test(self, argument1, argument2):
        return self.delegate(argument1, argument2)


@JImplements('org.optaplanner.core.api.function.TriPredicate', deferred=True)
class PythonTriPredicate:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def test(self, argument1, argument2, argument3):
        return self.delegate(argument1, argument2, argument3)


@JImplements('org.optaplanner.core.api.function.QuadPredicate', deferred=True)
class PythonQuadPredicate:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def test(self, argument1, argument2, argument3, argument4):
        return self.delegate(argument1, argument2, argument3, argument4)


@JImplements('org.optaplanner.core.api.function.PentaPredicate', deferred=True)
class PythonPentaPredicate:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def test(self, argument1, argument2, argument3, argument4, argument5):
        return self.delegate(argument1, argument2, argument3, argument4, argument5)


def function_cast(function, *type_args):
    global function_bytecode_translation, all_translated_successfully
    arg_count = len(inspect.signature(function).parameters)
    if len(type_args) != arg_count:
        raise ValueError(f'Invalid function: expected {len(type_args)} arguments but got {arg_count}')
    if function_bytecode_translation is not BytecodeTranslation.NONE:
        from java.util.function import Function, BiFunction
        from org.optaplanner.core.api.function import TriFunction, QuadFunction, PentaFunction
        from org.optaplanner.python.translator import PythonLikeObject

        try:
            if arg_count == 1:
                return translate_python_bytecode_to_java_bytecode(function, Function, *type_args, PythonLikeObject)
            elif arg_count == 2:
                return translate_python_bytecode_to_java_bytecode(function, BiFunction, *type_args, PythonLikeObject)
            elif arg_count == 3:
                return translate_python_bytecode_to_java_bytecode(function, TriFunction, *type_args, PythonLikeObject)
            elif arg_count == 4:
                return translate_python_bytecode_to_java_bytecode(function, QuadFunction, *type_args, PythonLikeObject)
            elif arg_count == 5:
                return translate_python_bytecode_to_java_bytecode(function, PentaFunction, *type_args, PythonLikeObject)
        except:  # noqa
            if function_bytecode_translation is BytecodeTranslation.FORCE:
                raise

            all_translated_successfully = False
            return default_function_cast(function, arg_count)

    return default_function_cast(function, arg_count)


def default_function_cast(function, arg_count):
    if arg_count == 1:
        return PythonFunction(lambda a: _convert_to_java_compatible_object(function(a)))
    elif arg_count == 2:
        return PythonBiFunction(lambda a, b: _convert_to_java_compatible_object(function(a, b)))
    elif arg_count == 3:
        return PythonTriFunction(lambda a, b, c: _convert_to_java_compatible_object(function(a, b, c)))
    elif arg_count == 4:
        return PythonQuadFunction(lambda a, b, c, d: _convert_to_java_compatible_object(function(a, b, c, d)))
    elif arg_count == 5:
        return PythonPentaFunction(lambda a, b, c, d, e: _convert_to_java_compatible_object(function(a, b, c, d, e)))
    else:
        raise ValueError


def predicate_cast(predicate, *type_args):
    global function_bytecode_translation, all_translated_successfully
    arg_count = len(inspect.signature(predicate).parameters)
    if len(type_args) != arg_count:
        raise ValueError(f'Invalid function: expected {len(type_args)} arguments but got {arg_count}')
    if function_bytecode_translation is not BytecodeTranslation.NONE:
        from java.util.function import Predicate, BiPredicate
        from org.optaplanner.core.api.function import TriPredicate, QuadPredicate, PentaPredicate
        try:
            if arg_count == 1:
                return translate_python_bytecode_to_java_bytecode(predicate, Predicate, *type_args)
            elif arg_count == 2:
                return translate_python_bytecode_to_java_bytecode(predicate, BiPredicate, *type_args)
            elif arg_count == 3:
                return translate_python_bytecode_to_java_bytecode(predicate, TriPredicate, *type_args)
            elif arg_count == 4:
                return translate_python_bytecode_to_java_bytecode(predicate, QuadPredicate, *type_args)
            elif arg_count == 5:
                return translate_python_bytecode_to_java_bytecode(predicate, PentaPredicate, *type_args)
        except:  # noqa
            if function_bytecode_translation is BytecodeTranslation.FORCE:
                raise

            all_translated_successfully = False
            return default_predicate_cast(predicate, arg_count)

    return default_predicate_cast(predicate, arg_count)


def default_predicate_cast(predicate, arg_count):
    if arg_count == 1:
        return PythonPredicate(predicate)
    elif arg_count == 2:
        return PythonBiPredicate(predicate)
    elif arg_count == 3:
        return PythonTriPredicate(predicate)
    elif arg_count == 4:
        return PythonQuadPredicate(predicate)
    elif arg_count == 5:
        return PythonPentaPredicate(predicate)
    else:
        raise ValueError


def to_int_function_cast(function, *type_args):
    global function_bytecode_translation, all_translated_successfully
    arg_count = len(inspect.signature(function).parameters)
    if len(type_args) != arg_count:
        raise ValueError(f'Invalid function: expected {len(type_args)} arguments but got {arg_count}')
    if function_bytecode_translation is not BytecodeTranslation.NONE:
        from java.util.function import ToIntFunction, ToIntBiFunction
        from org.optaplanner.core.api.function import ToIntTriFunction, ToIntQuadFunction

        try:
            if arg_count == 1:
                return translate_python_bytecode_to_java_bytecode(function, ToIntFunction, *type_args)
            elif arg_count == 2:
                return translate_python_bytecode_to_java_bytecode(function, ToIntBiFunction, *type_args)
            elif arg_count == 3:
                return translate_python_bytecode_to_java_bytecode(function, ToIntTriFunction, *type_args)
            elif arg_count == 4:
                return translate_python_bytecode_to_java_bytecode(function, ToIntQuadFunction, *type_args)
        except:  # noqa
            if function_bytecode_translation is BytecodeTranslation.FORCE:
                raise

            all_translated_successfully = False
            return default_to_int_function_cast(function, arg_count)

    return default_to_int_function_cast(function, arg_count)


def default_to_int_function_cast(function, arg_count):
    if arg_count == 1:
        return PythonToIntFunction(lambda a: _convert_to_java_compatible_object(function(a)))
    elif arg_count == 2:
        return PythonToIntBiFunction(lambda a, b: _convert_to_java_compatible_object(function(a, b)))
    elif arg_count == 3:
        return PythonToIntTriFunction(lambda a, b, c: _convert_to_java_compatible_object(function(a, b, c)))
    elif arg_count == 4:
        return PythonToIntQuadFunction(lambda a, b, c, d: _convert_to_java_compatible_object(function(a, b, c, d)))
    else:
        raise ValueError


@dataclasses.dataclass
class SamePropertyUniJoiner:
    joiner_creator: Callable
    join_function: Callable


@dataclasses.dataclass
class PropertyJoiner:
    joiner_creator: Callable
    left_join_function: Callable
    right_join_function: Callable


@dataclasses.dataclass
class SameOverlappingPropertyUniJoiner:
    joiner_creator: Callable
    start_function: Callable
    end_function: Callable


@dataclasses.dataclass
class OverlappingPropertyJoiner:
    joiner_creator: Callable
    left_start_function: Callable
    left_end_function: Callable
    right_start_function: Callable
    right_end_function: Callable


@dataclasses.dataclass
class FilteringJoiner:
    joiner_creator: Callable
    filter_function: Callable


def extract_joiners(joiner_tuple, *stream_types):
    from org.optaplanner.core.api.score.stream.bi import BiJoiner
    from org.optaplanner.core.api.score.stream.tri import TriJoiner
    from org.optaplanner.core.api.score.stream.quad import QuadJoiner
    from org.optaplanner.core.api.score.stream.penta import PentaJoiner

    if len(joiner_tuple) == 1 and (isinstance(joiner_tuple[0], list) or isinstance(joiner_tuple[0], tuple)):
        joiner_tuple = joiner_tuple[0] # Joiners was passed as a list of Joiners instead of varargs
    array_size = len(joiner_tuple)
    output_array = None
    array_type = None
    if len(stream_types) == 2:
        array_type = BiJoiner
        output_array = BiJoiner[array_size]
    elif len(stream_types) == 3:
        array_type = TriJoiner
        output_array = TriJoiner[array_size]
    elif len(stream_types) == 4:
        array_type = QuadJoiner
        output_array = QuadJoiner[array_size]
    elif len(stream_types) == 5:
        array_type = PentaJoiner
        output_array = PentaJoiner[array_size]
    else:
        raise ValueError

    for i in range(array_size):
        joiner_info = joiner_tuple[i]
        created_joiner = None
        if isinstance(joiner_info, SamePropertyUniJoiner):
            property_function = function_cast(joiner_info.join_function, stream_types[0])
            created_joiner = joiner_info.joiner_creator(property_function)
        elif isinstance(joiner_info, PropertyJoiner):
            left_property_function = function_cast(joiner_info.left_join_function, stream_types[:-1])
            right_property_function = function_cast(joiner_info.right_join_function, stream_types[-1])
            created_joiner = joiner_info.joiner_creator(left_property_function, right_property_function)
        elif isinstance(joiner_info, SameOverlappingPropertyUniJoiner):
            start_function = function_cast(joiner_info.start_function, stream_types[0])
            end_function = function_cast(joiner_info.end_function, stream_types[0])
            created_joiner = joiner_info.joiner_creator(start_function, end_function)
        elif isinstance(joiner_info, OverlappingPropertyJoiner):
            left_start_function = function_cast(joiner_info.left_start_function, stream_types[:-1])
            left_end_function = function_cast(joiner_info.left_end_function, stream_types[:-1])
            right_start_function = function_cast(joiner_info.right_start_function, stream_types[-1])
            right_end_function = function_cast(joiner_info.right_end_function, stream_types[-1])
            created_joiner = joiner_info.joiner_creator(left_start_function, left_end_function,
                                                        right_start_function, right_end_function)
        elif isinstance(joiner_info, FilteringJoiner):
            filter_function = predicate_cast(joiner_info.filter_function, stream_types)
            created_joiner = joiner_info.joiner_creator(filter_function)
        else:
            raise ValueError(f'Invalid Joiner: {joiner_info}. Create Joiners via optapy.constraint.Joiners.')

        output_array[i] = array_type @ created_joiner

    return output_array


class PythonConstraintFactory:
    delegate: 'ConstraintFactory'
    function_bytecode_translation: BytecodeTranslation

    def __init__(self, delegate: 'ConstraintFactory', function_bytecode_translation: BytecodeTranslation):
        self.delegate = delegate
        self.function_bytecode_translation = function_bytecode_translation

    def getDefaultConstraintPackage(self) -> str:
        return self.delegate.getDefaultConstraintPackage()

    def forEach(self, item_type: Type) -> 'PythonUniConstraintStream':
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonUniConstraintStream(self.delegate.forEach(item_type), self.getDefaultConstraintPackage(),
                                         item_type)

    def forEachIncludingNullVars(self, item_type: Type) -> 'PythonUniConstraintStream':
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonUniConstraintStream(self.delegate.forEachIncludingNullVars(item_type),
                                         self.getDefaultConstraintPackage(), item_type)

    def forEachUniquePair(self, item_type: Type, *joiners: List['BiJoiner']):
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonBiConstraintStream(self.delegate.forEachUniquePair(item_type,
                                                                        extract_joiners(joiners, item_type, item_type)),
                                        self.getDefaultConstraintPackage(), item_type, item_type)

    def from_(self, item_type: Type) -> 'PythonUniConstraintStream':
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonUniConstraintStream(self.delegate.from_(item_type), self.getDefaultConstraintPackage(),
                                         item_type)

    def fromUnfiltered(self, item_type: Type) -> 'PythonUniConstraintStream':
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonUniConstraintStream(self.delegate.fromUnfiltered(item_type), self.getDefaultConstraintPackage(),
                                         item_type)

    def fromUniquePair(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonBiConstraintStream':
        global function_bytecode_translation
        item_type = get_class(item_type)
        function_bytecode_translation = self.function_bytecode_translation
        return PythonBiConstraintStream(self.delegate.fromUniquePair(item_type,
                                                                     extract_joiners(joiners, item_type, item_type)),
                                        self.getDefaultConstraintPackage(), item_type, item_type)


@dataclasses.dataclass
class ConstraintInfo:
    constraint_package: str
    constraint_name: str
    score: Optional['Score']
    impact_function: Optional[Callable]


def extract_constraint_info(default_package: str, args: tuple) -> ConstraintInfo:
    from org.optaplanner.core.api.score import Score
    constraint_package = default_package
    constraint_name = None
    if isinstance(args[1], str):
        constraint_package = args[0]
        constraint_name = args[1]
        args = args[2:]
    else:
        constraint_name = args[0]
        args = args[1:]

    if len(args) == 0:
        return ConstraintInfo(constraint_package, constraint_name, None, None)

    if isinstance(args[0], Score):
        score = args[0]
        args = args[1:]
    else:
        score = None

    if len(args) == 0:
        return ConstraintInfo(constraint_package, constraint_name, score, None)
    else:
        return ConstraintInfo(constraint_package, constraint_name, score, args[0])


def perform_group_by(delegate, package, group_by_args, *type_arguments):
    actual_group_by_args = []
    for i in range(len(group_by_args)):
        if callable(group_by_args[i]):
            actual_group_by_args.append(function_cast(group_by_args[i], *type_arguments))
        else:
            actual_group_by_args.append(group_by_args[i])

    if len(group_by_args) == 1:
        return PythonUniConstraintStream(delegate.groupBy(*actual_group_by_args), package, JClass('java.lang.Object'))
    elif len(group_by_args) == 2:
        return PythonBiConstraintStream(delegate.groupBy(*actual_group_by_args), package, JClass('java.lang.Object'),
                                        JClass('java.lang.Object'))
    elif len(group_by_args) == 3:
        return PythonTriConstraintStream(delegate.groupBy(*actual_group_by_args), package, JClass('java.lang.Object'),
                                         JClass('java.lang.Object'), JClass('java.lang.Object'))
    elif len(group_by_args) == 4:
        return PythonQuadConstraintStream(delegate.groupBy(*actual_group_by_args), package, JClass('java.lang.Object'),
                                          JClass('java.lang.Object'), JClass('java.lang.Object'),
                                          JClass('java.lang.Object'))
    else:
        raise ValueError



class PythonUniConstraintStream:
    delegate: 'UniConstraintStream'
    package: str
    a_type: Type

    def __init__(self, delegate: 'UniConstraintStream', package: str, a_type: Type):
        self.delegate = delegate
        self.package = package
        self.a_type = a_type

    def filter(self, predicate) -> 'PythonUniConstraintStream':
        translated_predicate = predicate_cast(predicate, self.a_type)
        return PythonUniConstraintStream(self.delegate.filter(translated_predicate), self.package, self.a_type)

    def join(self, unistream_or_type, *joiners: List['BiJoiner']) -> 'PythonBiConstraintStream':
        b_type = None
        if isinstance(unistream_or_type, PythonUniConstraintStream):
            b_type = unistream_or_type.a_type
        else:
            b_type = get_class(unistream_or_type)
            unistream_or_type = b_type

        join_result = self.delegate.join(unistream_or_type, extract_joiners(joiners, self.a_type, b_type))
        return PythonBiConstraintStream(join_result, self.package, self.a_type, b_type)

    def ifExists(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifExists(item_type,
                                                                extract_joiners(joiners, self.a_type, item_type)),
                                         self.package, self.a_type)

    def ifExistsIncludingNullVars(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifExistsIncludingNullVars(item_type,
                                                                                 extract_joiners(joiners, self.a_type,
                                                                                                 item_type)),
                                         self.package,
                                         self.a_type)

    def ifExistsOther(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifExistsOther(item_type, extract_joiners(joiners, self.a_type,
                                                                                                item_type)),
                                         self.package, self.a_type)

    def ifExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifExistsOtherIncludingNullVars(item_type,
                                                                                      extract_joiners(joiners,
                                                                                                      self.a_type,
                                                                                                      item_type)),
                                         self.package,
                                         self.a_type)

    def ifNotExists(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifNotExists(item_type, extract_joiners(joiners, self.a_type,
                                                                                              item_type)),
                                         self.package, self.a_type)

    def ifNotExistsIncludingNullVars(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifNotExistsIncludingNullVars(item_type,
                                                                                    extract_joiners(joiners,
                                                                                                    self.a_type,
                                                                                                    item_type)),
                                         self.package,
                                         self.a_type)

    def ifNotExistsOther(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifNotExistsOther(item_type, extract_joiners(joiners, self.a_type,
                                                                                                   item_type)),
                                         self.package,
                                         self.a_type)

    def ifNotExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['BiJoiner']) -> 'PythonUniConstraintStream':
        item_type = get_class(item_type)
        return PythonUniConstraintStream(self.delegate.ifNotExistsOtherIncludingNullVars(item_type,
                                                                                         extract_joiners(joiners,
                                                                                                         self.a_type,
                                                                                                         item_type)),
                                         self.package, self.a_type)

    def groupBy(self, *args):
        return perform_group_by(self.delegate, self.package, args, self.a_type)

    def map(self, mapping_function) -> 'PythonUniConstraintStream':
        translated_function = function_cast(mapping_function, self.a_type)
        return PythonUniConstraintStream(self.delegate.map(translated_function), self.package,
                                         JClass('java.lang.Object'))

    def flattenLast(self, flattening_function) -> 'PythonUniConstraintStream':
        translated_function = function_cast(flattening_function, self.a_type)
        return PythonUniConstraintStream(self.delegate.flattenLast(translated_function), self.package,
                                         JClass('java.lang.Object'))

    def distinct(self) -> 'PythonUniConstraintStream':
        return PythonUniConstraintStream(self.delegate.distinct(), self.package, self.a_type)

    def penalize(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score)
        else:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score,
                                          to_int_function_cast(constraint_info.impact_function, self.a_type))

    def penalizeLong(self, *args):
        raise NotImplementedError

    def penalizeBigDecimal(self, *args):
        raise NotImplementedError

    def penalizeConfigurable(self, *args):
        raise NotImplementedError

    def penalizeConfigurableLong(self, *args):
        raise NotImplementedError

    def penalizeConfigurableBigDecimal(self, *args):
        raise NotImplementedError

    def reward(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type))

    def rewardLong(self, *args):
        raise NotImplementedError

    def rewardBigDecimal(self, *args):
        raise NotImplementedError

    def rewardConfigurable(self, *args):
        raise NotImplementedError

    def impact(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type))

    def impactLong(self, *args):
        raise NotImplementedError

    def impactBigDecimal(self, *args):
        raise NotImplementedError

    def impactConfigurable(self, *args):
        raise NotImplementedError


class PythonBiConstraintStream:
    delegate: 'BiConstraintStream'
    package: str
    a_type: Type
    b_type: Type

    def __init__(self, delegate: 'BiConstraintStream', package: str, a_type: Type, b_type: Type):
        self.delegate = delegate
        self.package = package
        self.a_type = a_type
        self.b_type = b_type

    def filter(self, predicate) -> 'PythonBiConstraintStream':
        translated_predicate = predicate_cast(predicate, self.a_type, self.b_type)
        return PythonBiConstraintStream(self.delegate.filter(translated_predicate), self.package, self.a_type,
                                        self.b_type)

    def join(self, unistream_or_type, *joiners: List['TriJoiner']) -> 'PythonTriConstraintStream':
        c_type = None
        if isinstance(unistream_or_type, PythonUniConstraintStream):
            c_type = unistream_or_type.a_type
        else:
            c_type = get_class(unistream_or_type)
            unistream_or_type = c_type

        join_result = self.delegate.join(unistream_or_type, extract_joiners(joiners, self.a_type, self.b_type, c_type))
        return PythonTriConstraintStream(join_result, self.package, self.a_type, self.b_type, c_type)

    def ifExists(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifExists(item_type,
                                                               extract_joiners(joiners, self.a_type,
                                                                               self.b_type, item_type)),
                                        self.package, self.a_type, self.b_type)

    def ifExistsIncludingNullVars(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifExistsIncludingNullVars(item_type, extract_joiners(joiners,
                                                                                                           self.a_type,
                                                                                                           self.b_type,
                                                                                                           item_type)),
                                        self.package,
                                        self.a_type, self.b_type)

    def ifExistsOther(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifExistsOther(item_type, extract_joiners(joiners, self.a_type,
                                                                                               self.b_type, item_type)),
                                        self.package, self.a_type,
                                        self.b_type)

    def ifExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifExistsOtherIncludingNullVars(item_type,
                                                                                     extract_joiners(joiners,
                                                                                                     self.a_type,
                                                                                                     self.b_type,
                                                                                                     item_type)),
                                        self.package, self.a_type, self.b_type)

    def ifNotExists(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifNotExists(item_type, extract_joiners(joiners, self.a_type,
                                                                                             self.b_type, item_type)),
                                        self.package, self.a_type, self.b_type)

    def ifNotExistsIncludingNullVars(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifNotExistsIncludingNullVars(item_type,
                                                                                   extract_joiners(joiners,
                                                                                                   self.a_type,
                                                                                                   self.b_type,
                                                                                                   item_type)),
                                        self.package, self.a_type, self.b_type)

    def ifNotExistsOther(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifNotExistsOther(item_type,
                                                                       extract_joiners(joiners,
                                                                                       self.a_type,
                                                                                       self.b_type,
                                                                                       item_type)),
                                        self.package, self.a_type, self.b_type)

    def ifNotExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['TriJoiner']) -> 'PythonBiConstraintStream':
        item_type = get_class(item_type)
        return PythonBiConstraintStream(self.delegate.ifNotExistsOtherIncludingNullVars(item_type,
                                                                                        extract_joiners(joiners,
                                                                                                        self.a_type,
                                                                                                        self.b_type,
                                                                                                        item_type)),
                                        self.package, self.a_type, self.b_type)

    def groupBy(self, *args):
        return perform_group_by(self.delegate, self.package, args, self.a_type, self.b_type)

    def map(self, mapping_function) -> 'PythonUniConstraintStream':
        translated_function = function_cast(mapping_function, self.a_type, self.b_type)
        return PythonUniConstraintStream(self.delegate.map(translated_function), self.package, JClass('java.lang.Object'))

    def flattenLast(self, flattening_function) -> 'PythonBiConstraintStream':
        translated_function = function_cast(flattening_function, self.b_type)
        return PythonBiConstraintStream(self.delegate.flattenLast(translated_function), self.package,
                                        self.a_type, JClass('java.lang.Object'))

    def distinct(self) -> 'PythonBiConstraintStream':
        return PythonBiConstraintStream(self.delegate.distinct(), self.package, self.a_type, self.b_type)

    def penalize(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score)
        else:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score,
                                          to_int_function_cast(constraint_info.impact_function, self.a_type,
                                                               self.b_type))

    def penalizeLong(self, *args):
        raise NotImplementedError

    def penalizeBigDecimal(self, *args):
        raise NotImplementedError

    def penalizeConfigurable(self, *args):
        raise NotImplementedError

    def penalizeConfigurableLong(self, *args):
        raise NotImplementedError

    def penalizeConfigurableBigDecimal(self, *args):
        raise NotImplementedError

    def reward(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type))

    def rewardLong(self, *args):
        raise NotImplementedError

    def rewardBigDecimal(self, *args):
        raise NotImplementedError

    def rewardConfigurable(self, *args):
        raise NotImplementedError

    def impact(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type))

    def impactLong(self, *args):
        raise NotImplementedError

    def impactBigDecimal(self, *args):
        raise NotImplementedError

    def impactConfigurable(self, *args):
        raise NotImplementedError


class PythonTriConstraintStream:
    delegate: 'TriConstraintStream'
    package: str
    a_type: Type
    b_type: Type
    c_type: Type

    def __init__(self, delegate: 'TriConstraintStream', package: str, a_type: Type, b_type: Type, c_type: Type):
        self.delegate = delegate
        self.package = package
        self.a_type = a_type
        self.b_type = b_type
        self.c_type = c_type

    def filter(self, predicate) -> 'PythonTriConstraintStream':
        translated_predicate = predicate_cast(predicate, self.a_type, self.b_type, self.c_type)
        return PythonTriConstraintStream(self.delegate.filter(translated_predicate), self.package, self.a_type,
                                         self.b_type, self.c_type)

    def join(self, unistream_or_type, *joiners: List['QuadJoiner']) -> 'PythonQuadConstraintStream':
        d_type = None
        if isinstance(unistream_or_type, PythonUniConstraintStream):
            d_type = unistream_or_type.a_type
        else:
            d_type = get_class(unistream_or_type)
            unistream_or_type = d_type

        join_result = self.delegate.join(unistream_or_type, extract_joiners(joiners, self.a_type, self.b_type,
                                                                            self.c_type, d_type))
        return PythonQuadConstraintStream(join_result, self.package, self.a_type, self.b_type, self.c_type, d_type)

    def ifExists(self, item_type: Type, *joiners: List['QuadJoiner']) -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifExists(item_type, extract_joiners(joiners, self.a_type,
                                                                                           self.b_type, self.c_type,
                                                                                           item_type)), self.package,
                                         self.a_type, self.b_type, self.c_type)

    def ifExistsIncludingNullVars(self, item_type: Type, *joiners: List['QuadJoiner']) -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifExistsIncludingNullVars(item_type, extract_joiners(joiners,
                                                                                                            self.a_type,
                                                                                                            self.b_type,
                                                                                                            self.c_type,
                                                                                                            item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifExistsOther(self, item_type: Type, *joiners: List['QuadJoiner']) -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifExistsOther(item_type, extract_joiners(joiners,
                                                                                                self.a_type,
                                                                                                self.b_type,
                                                                                                self.c_type,
                                                                                                item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['QuadJoiner'])\
            -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifExistsOtherIncludingNullVars(item_type,
                                                                                      extract_joiners(joiners,
                                                                                                      self.a_type,
                                                                                                      self.b_type,
                                                                                                      self.c_type,
                                                                                                      item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifNotExists(self, item_type: Type, *joiners: List['QuadJoiner']) -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifNotExists(item_type, extract_joiners(joiners,
                                                                                              self.a_type,
                                                                                              self.b_type,
                                                                                              self.c_type,
                                                                                              item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifNotExistsIncludingNullVars(self, item_type: Type, *joiners: List['QuadJoiner'])\
            -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifNotExistsIncludingNullVars(item_type,
                                                                                    extract_joiners(joiners,
                                                                                                    self.a_type,
                                                                                                    self.b_type,
                                                                                                    self.c_type,
                                                                                                    item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifNotExistsOther(self, item_type: Type, *joiners: List['QuadJoiner']) -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifNotExistsOther(item_type, extract_joiners(joiners,
                                                                                                   self.a_type,
                                                                                                   self.b_type,
                                                                                                   self.c_type,
                                                                                                   item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def ifNotExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['QuadJoiner'])\
            -> 'PythonTriConstraintStream':
        item_type = get_class(item_type)
        return PythonTriConstraintStream(self.delegate.ifNotExistsOtherIncludingNullVars(item_type,
                                                                                         extract_joiners(joiners,
                                                                                                         self.a_type,
                                                                                                         self.b_type,
                                                                                                         self.c_type,
                                                                                                         item_type)),
                                         self.package, self.a_type, self.b_type, self.c_type)

    def groupBy(self, *args):
        return perform_group_by(self.delegate, self.package, args, self.a_type, self.b_type, self.c_type)

    def map(self, mapping_function) -> 'PythonUniConstraintStream':
        translated_function = function_cast(mapping_function, self.a_type, self.b_type, self.c_type)
        return PythonUniConstraintStream(self.delegate.map(translated_function), self.package,
                                         JClass('java.lang.Object'))

    def flattenLast(self, flattening_function) -> 'PythonTriConstraintStream':
        translated_function = function_cast(flattening_function, self.c_type)
        return PythonTriConstraintStream(self.delegate.flattenLast(translated_function), self.package,
                                         self.a_type, self.b_type, JClass('java.lang.Object'))

    def distinct(self) -> 'PythonTriConstraintStream':
        return PythonTriConstraintStream(self.delegate.distinct(), self.package, self.a_type,
                                         self.b_type, self.c_type)

    def penalize(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score)
        else:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score,
                                          to_int_function_cast(constraint_info.impact_function, self.a_type,
                                                               self.b_type,
                                                               self.c_type))

    def penalizeLong(self, *args):
        raise NotImplementedError

    def penalizeBigDecimal(self, *args):
        raise NotImplementedError

    def penalizeConfigurable(self, *args):
        raise NotImplementedError

    def penalizeConfigurableLong(self, *args):
        raise NotImplementedError

    def penalizeConfigurableBigDecimal(self, *args):
        raise NotImplementedError

    def reward(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type,
                                                             self.c_type))

    def rewardLong(self, *args):
        raise NotImplementedError

    def rewardBigDecimal(self, *args):
        raise NotImplementedError

    def rewardConfigurable(self, *args):
        raise NotImplementedError

    def impact(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type,
                                                             self.c_type))

    def impactLong(self, *args):
        raise NotImplementedError

    def impactBigDecimal(self, *args):
        raise NotImplementedError

    def impactConfigurable(self, *args):
        raise NotImplementedError


class PythonQuadConstraintStream:
    delegate: 'QuadConstraintStream'
    package: str
    a_type: Type
    b_type: Type
    c_type: Type
    d_type: Type

    def __init__(self, delegate: 'QuadConstraintStream', package: str, a_type: Type, b_type: Type, c_type: Type,
                 d_type: type):
        self.delegate = delegate
        self.package = package
        self.a_type = a_type
        self.b_type = b_type
        self.c_type = c_type
        self.d_type = d_type

    def filter(self, predicate) -> 'PythonQuadConstraintStream':
        translated_predicate = predicate_cast(predicate, self.a_type, self.b_type, self.c_type, self.d_type)
        return PythonQuadConstraintStream(self.delegate.filter(translated_predicate), self.package, self.a_type,
                                          self.b_type, self.c_type, self.d_type)

    def ifExists(self, item_type: Type, *joiners: List['PentaJoiner']) -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifExists(item_type, extract_joiners(joiners,
                                                                                            self.a_type,
                                                                                            self.b_type,
                                                                                            self.c_type,
                                                                                            self.d_type,
                                                                                            item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifExistsIncludingNullVars(self, item_type: Type, *joiners: List['PentaJoiner']) -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifExistsIncludingNullVars(item_type,
                                                                                  extract_joiners(joiners,
                                                                                                  self.a_type,
                                                                                                  self.b_type,
                                                                                                  self.c_type,
                                                                                                  self.d_type,
                                                                                                  item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifExistsOther(self, item_type: Type, *joiners: List['PentaJoiner']) -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifExistsOther(item_type, extract_joiners(joiners,
                                                                                                 self.a_type,
                                                                                                 self.b_type,
                                                                                                 self.c_type,
                                                                                                 self.d_type,
                                                                                                 item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['PentaJoiner']) \
            -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifExistsOtherIncludingNullVars(item_type,
                                                                                       extract_joiners(joiners,
                                                                                                       self.a_type,
                                                                                                       self.b_type,
                                                                                                       self.c_type,
                                                                                                       self.d_type,
                                                                                                       item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifNotExists(self, item_type: Type, *joiners: List['PentaJoiner']) -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifNotExists(item_type, extract_joiners(joiners,
                                                                                               self.a_type,
                                                                                               self.b_type,
                                                                                               self.c_type,
                                                                                               self.d_type,
                                                                                               item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifNotExistsIncludingNullVars(self, item_type: Type, *joiners: List['PentaJoiner']) \
            -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifNotExistsIncludingNullVars(item_type,
                                                                                     extract_joiners(joiners,
                                                                                                     self.a_type,
                                                                                                     self.b_type,
                                                                                                     self.c_type,
                                                                                                     self.d_type,
                                                                                                     item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifNotExistsOther(self, item_type: Type, *joiners: List['PentaJoiner']) -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifNotExistsOther(item_type, extract_joiners(joiners,
                                                                                                    self.a_type,
                                                                                                    self.b_type,
                                                                                                    self.c_type,
                                                                                                    self.d_type,
                                                                                                    item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def ifNotExistsOtherIncludingNullVars(self, item_type: Type, *joiners: List['PentaJoiner']) \
            -> 'PythonQuadConstraintStream':
        item_type = get_class(item_type)
        return PythonQuadConstraintStream(self.delegate.ifNotExistsOtherIncludingNullVars(item_type,
                                                                                          extract_joiners(joiners,
                                                                                                          self.a_type,
                                                                                                          self.b_type,
                                                                                                          self.c_type,
                                                                                                          self.d_type,
                                                                                                          item_type)),
                                          self.package, self.a_type, self.b_type, self.c_type, self.d_type)

    def groupBy(self, *args):
        return perform_group_by(self.delegate, self.package, args, self.a_type, self.b_type, self.c_type, self.d_type)

    def map(self, mapping_function) -> 'PythonUniConstraintStream':
        translated_function = function_cast(mapping_function, self.a_type, self.b_type, self.c_type, self.d_type)
        return PythonUniConstraintStream(self.delegate.map(translated_function), self.package,
                                         JClass('java.lang.Object'))

    def flattenLast(self, flattening_function) -> 'PythonQuadConstraintStream':
        translated_function = function_cast(flattening_function, self.d_type)
        return PythonQuadConstraintStream(self.delegate.flattenLast(translated_function), self.package,
                                          self.a_type, self.b_type, self.c_type, JClass('java.lang.Object'))

    def distinct(self) -> 'PythonQuadConstraintStream':
        return PythonQuadConstraintStream(self.delegate.distinct(), self.package, self.a_type,
                                          self.b_type, self.c_type, self.d_type)

    def penalize(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score)
        else:
            return self.delegate.penalize(constraint_info.constraint_package, constraint_info.constraint_name,
                                          constraint_info.score,
                                          to_int_function_cast(constraint_info.impact_function, self.a_type,
                                                               self.b_type, self.c_type, self.d_type))

    def penalizeLong(self, *args):
        raise NotImplementedError

    def penalizeBigDecimal(self, *args):
        raise NotImplementedError

    def penalizeConfigurable(self, *args):
        raise NotImplementedError

    def penalizeConfigurableLong(self, *args):
        raise NotImplementedError

    def penalizeConfigurableBigDecimal(self, *args):
        raise NotImplementedError

    def reward(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.reward(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type,
                                                             self.c_type, self.d_type))

    def rewardLong(self, *args):
        raise NotImplementedError

    def rewardBigDecimal(self, *args):
        raise NotImplementedError

    def rewardConfigurable(self, *args):
        raise NotImplementedError

    def impact(self, *args):
        constraint_info = extract_constraint_info(self.package, args)
        if constraint_info.impact_function is None:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score)
        else:
            return self.delegate.impact(constraint_info.constraint_package, constraint_info.constraint_name,
                                        constraint_info.score,
                                        to_int_function_cast(constraint_info.impact_function, self.a_type, self.b_type,
                                                             self.c_type, self.d_type))

    def impactLong(self, *args):
        raise NotImplementedError

    def impactBigDecimal(self, *args):
        raise NotImplementedError

    def impactConfigurable(self, *args):
        raise NotImplementedError
