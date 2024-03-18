import builtins
import ctypes
import dis
import inspect
import sys
import abc
from dataclasses import dataclass
from types import FunctionType
from typing import TypeVar, Any, List, Tuple, Dict, Union, Annotated, Type, Callable, \
    get_origin, get_args, get_type_hints, TYPE_CHECKING
from jpype import JInt, JLong, JDouble, JBoolean, JProxy, JClass, JArray

if TYPE_CHECKING:
    from java.util import IdentityHashMap

MINIMUM_SUPPORTED_PYTHON_VERSION = (3, 9)
MAXIMUM_SUPPORTED_PYTHON_VERSION = (3, 11)

global_dict_to_instance = dict()
global_dict_to_key_set = dict()
type_to_compiled_java_class = dict()
type_to_annotations = dict()

function_interface_pair_to_instance = dict()
function_interface_pair_to_class = dict()


@dataclass
class JavaAnnotation:
    annotation_type: JClass
    annotation_values: Dict[str, Any]

    def __hash__(self):
        return 0


T = TypeVar('T')


def add_class_annotation(annotation_type, /, **annotation_values: Any) -> Callable[[Type[T]], Type[T]]:
    def decorator(_cls: Type[T]) -> Type[T]:
        global type_to_compiled_java_class
        global type_to_annotations
        if _cls in type_to_compiled_java_class:
            raise RuntimeError('Cannot add an annotation after a class been compiled.')
        annotations = type_to_annotations.get(_cls, [])
        annotation = JavaAnnotation(annotation_type, annotation_values)
        annotations.append(annotation)
        type_to_annotations[_cls] = annotations
        return _cls

    return decorator


def is_python_version_supported(python_version):
    python_version_major_minor = python_version[0:2]
    return MINIMUM_SUPPORTED_PYTHON_VERSION <= python_version_major_minor <= MAXIMUM_SUPPORTED_PYTHON_VERSION


def is_current_python_version_supported():
    return is_python_version_supported(sys.version_info)


def check_current_python_version_supported():
    if not is_current_python_version_supported():
        raise NotImplementedError(f'The translator does not support the current Python version ({sys.version}). '
                                  f'The minimum version currently supported is '
                                  f'{MINIMUM_SUPPORTED_PYTHON_VERSION[0]}.{MINIMUM_SUPPORTED_PYTHON_VERSION[1]}. '
                                  f'The maximum version currently supported is '
                                  f'{MAXIMUM_SUPPORTED_PYTHON_VERSION[0]}.{MAXIMUM_SUPPORTED_PYTHON_VERSION[1]}.')


def get_translated_java_system_error_message(error):
    from ai.timefold.jpyinterpreter.util import TracebackUtils
    top_line = f'{error.getClass().getSimpleName()}:  {error.getMessage()}'
    traceback = TracebackUtils.getTraceback(error)
    return f'{top_line}\n{traceback}'


class TranslatedJavaSystemError(SystemError):
    def __init__(self, error):
        super().__init__(get_translated_java_system_error_message(error))


# Taken from https://stackoverflow.com/a/60953150
def is_native_module(module):
    """ is_native_module(thing) -> boolean predicate, True if `module`
        is a native-compiled ("extension") module.

        Q.v. this fine StackOverflow answer on this subject:
            https://stackoverflow.com/a/39304199/298171
    """
    import importlib.machinery
    import inspect

    QUALIFIER = '.'
    EXTENSION_SUFFIXES = tuple(suffix.lstrip(QUALIFIER)
                               for suffix
                               in importlib.machinery.EXTENSION_SUFFIXES)

    suffix = lambda filename: QUALIFIER in filename \
                              and filename.rpartition(QUALIFIER)[-1] \
                              or ''
    # Step one: modules only beyond this point:
    if not inspect.ismodule(module):
        return False

    # Step two: return truly when “__loader__” is set:
    if isinstance(getattr(module, '__loader__', None),
                  importlib.machinery.ExtensionFileLoader):
        return True

    # Step three: in leu of either of those indicators,
    # check the module path’s file suffix:
    try:
        ext = suffix(inspect.getfile(module))
    except TypeError as exc:
        return 'is a built-in' in str(exc)

    return ext in EXTENSION_SUFFIXES


def is_c_native(item):
    import importlib
    module = getattr(item, '__module__', '')

    # __main__ is a built-in module, according to Python (and this be seen as c-native). We can also compile builtins,
    # so return False, so we can compile them
    if module == '__main__' or \
            module == 'builtins' \
            or module == '':  # if we cannot find module, assume it is not native
        return False

    return is_native_module(importlib.import_module(module))


def init_type_to_compiled_java_class():
    from ai.timefold.jpyinterpreter.builtins import GlobalBuiltins
    from ai.timefold.jpyinterpreter.types import BuiltinTypes
    import ai.timefold.jpyinterpreter.types.datetime as java_datetime_types
    import datetime
    import builtins

    if len(type_to_compiled_java_class) > 0:
        return

    check_current_python_version_supported()

    type_to_compiled_java_class[staticmethod] = BuiltinTypes.STATIC_FUNCTION_TYPE
    type_to_compiled_java_class[classmethod] = BuiltinTypes.CLASS_FUNCTION_TYPE

    type_to_compiled_java_class[int] = BuiltinTypes.INT_TYPE
    type_to_compiled_java_class[float] = BuiltinTypes.FLOAT_TYPE
    type_to_compiled_java_class[complex] = BuiltinTypes.COMPLEX_TYPE
    type_to_compiled_java_class[bool] = BuiltinTypes.BOOLEAN_TYPE

    type_to_compiled_java_class[type(None)] = BuiltinTypes.NONE_TYPE
    type_to_compiled_java_class[str] = BuiltinTypes.STRING_TYPE
    type_to_compiled_java_class[bytes] = BuiltinTypes.BYTES_TYPE
    type_to_compiled_java_class[bytearray] = BuiltinTypes.BYTE_ARRAY_TYPE
    type_to_compiled_java_class[object] = BuiltinTypes.BASE_TYPE

    type_to_compiled_java_class[list] = BuiltinTypes.LIST_TYPE
    type_to_compiled_java_class[tuple] = BuiltinTypes.TUPLE_TYPE
    type_to_compiled_java_class[set] = BuiltinTypes.SET_TYPE
    type_to_compiled_java_class[frozenset] = BuiltinTypes.FROZEN_SET_TYPE
    type_to_compiled_java_class[dict] = BuiltinTypes.DICT_TYPE

    type_to_compiled_java_class[datetime.datetime] = java_datetime_types.PythonDateTime.DATE_TIME_TYPE
    type_to_compiled_java_class[datetime.date] = java_datetime_types.PythonDate.DATE_TYPE
    type_to_compiled_java_class[datetime.time] = java_datetime_types.PythonTime.TIME_TYPE
    type_to_compiled_java_class[datetime.timedelta] = java_datetime_types.PythonTimeDelta.TIME_DELTA_TYPE

    # Type aliases
    type_to_compiled_java_class[any] = BuiltinTypes.BASE_TYPE
    type_to_compiled_java_class[type] = BuiltinTypes.TYPE_TYPE

    for java_type in GlobalBuiltins.getBuiltinTypes():
        try:
            type_to_compiled_java_class[getattr(builtins, java_type.getTypeName())] = java_type
        except AttributeError:
            # This version of python does not have this builtin type; pass
            pass


def copy_iterable(iterable):
    from java.util import ArrayList
    if iterable is None:
        return None
    iterable_copy = ArrayList()
    for item in iterable:
        iterable_copy.add(item)
    return iterable_copy


def copy_variable_names(iterable):
    from java.util import ArrayList
    from ai.timefold.jpyinterpreter.util import JavaIdentifierUtils

    if iterable is None:
        return None
    iterable_copy = ArrayList()
    for item in iterable:
        iterable_copy.add(JavaIdentifierUtils.sanitizeFieldName(item))
    return iterable_copy


def remove_from_instance_map(instance_map, object_id):
    instance_map.remove(object_id)


def put_in_instance_map(instance_map, python_object, java_object):
    global objects_without_weakref_id_set
    instance_map.put(id(python_object), java_object)


class CodeWrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getitem__(self, item):
        if item == 'wrapped':
            return self.wrapped
        else:
            raise KeyError(f'No item: {item}')


def convert_object_to_java_python_like_object(value, instance_map=None):
    import datetime
    from java.lang import Object, ClassNotFoundException
    from java.util import HashMap
    from ai.timefold.jpyinterpreter import CPythonBackedPythonInterpreter
    from ai.timefold.jpyinterpreter.types import PythonLikeType, AbstractPythonLikeObject, CPythonBackedPythonLikeObject
    from ai.timefold.jpyinterpreter.types.wrappers import OpaquePythonReference, CPythonType, JavaObjectWrapper, PythonLikeFunctionWrapper
    from ai.timefold.jpyinterpreter.types.datetime import PythonDate, PythonDateTime, PythonTime, PythonTimeDelta

    if instance_map is None:
        instance_map = HashMap()

    if isinstance(value, Object):
        out = JavaObjectWrapper(value)
        put_in_instance_map(instance_map, value, out)
        return out
    if isinstance(value, JavaAnnotation):
        return None
    elif isinstance(value, datetime.datetime):
        out = PythonDateTime.of(value.year, value.month, value.day, value.hour, value.minute, value.second,
                                value.microsecond, value.tzname(), value.fold)
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, datetime.date):
        out = PythonDate.of(value.year, value.month, value.day)
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, datetime.time):
        out = PythonTime.of(value.hour, value.minute, value.second, value.microsecond, value.tzname(), value.fold)
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, datetime.timedelta):
        out = PythonTimeDelta.of(value.days, value.seconds, value.microseconds)
        put_in_instance_map(instance_map, value, out)
        return out
    elif inspect.iscode(value):
        try:
            from ai.timefold.jpyinterpreter.types import PythonLikeFunction, PythonCode
            java_class = translate_python_code_to_java_class(value, PythonLikeFunction)
            out = PythonCode(java_class)
            put_in_instance_map(instance_map, value, out)
            return out
        except:
            from ai.timefold.jpyinterpreter.types import PythonLikeFunction, PythonCode
            java_class = translate_python_code_to_python_wrapper_class(value)
            out = PythonCode(java_class)
            put_in_instance_map(instance_map, value, out)
            return out
    elif type(value) is object:
        java_type = type_to_compiled_java_class[type(value)]
        out = CPythonBackedPythonLikeObject(java_type)
        put_in_instance_map(instance_map, value, out)
        CPythonBackedPythonInterpreter.updateJavaObjectFromPythonObject(out,
                                                                        JProxy(OpaquePythonReference, inst=value,
                                                                               convert=True),
                                                                        instance_map)
        return out
    elif not inspect.isfunction(value) and type(value) in type_to_compiled_java_class:
        if type_to_compiled_java_class[type(value)] is None:
            return None
        java_type = type_to_compiled_java_class[type(value)]
        if isinstance(java_type, CPythonType):
            return None
        try:
            java_class = java_type.getJavaClass()
        except ClassNotFoundException:
            # Class is currently being generated
            return None
        out = java_class.getConstructor(PythonLikeType).newInstance(java_type)
        if isinstance(out, CPythonBackedPythonLikeObject):
            # Mark the item as created from python
            getattr(out, '$markValidPythonReference')()
        put_in_instance_map(instance_map, value, out)
        CPythonBackedPythonInterpreter.updateJavaObjectFromPythonObject(out,
                                                                        JProxy(OpaquePythonReference, inst=value,
                                                                               convert=True),
                                                                        instance_map)

        if isinstance(out, AbstractPythonLikeObject):
            for (key, value) in getattr(value, '__dict__', dict()).items():
                out.setAttribute(key, convert_to_java_python_like_object(value, instance_map))

        return out
    elif inspect.isbuiltin(value) or is_c_native(value):
        return None
    elif inspect.isfunction(value):
        try:
            from ai.timefold.jpyinterpreter.types import PythonLikeFunction
            wrapped = PythonLikeFunctionWrapper()
            put_in_instance_map(instance_map, value, wrapped)
            out = translate_python_bytecode_to_java_bytecode(value, PythonLikeFunction)
            wrapped.setWrapped(out)
            put_in_instance_map(instance_map, value, out)
            return out
        except:
            return None
    else:
        try:
            java_type = translate_python_class_to_java_class(type(value))
            if isinstance(java_type, CPythonType):
                return None
            java_class = java_type.getJavaClass()
            out = java_class.getConstructor(PythonLikeType).newInstance(java_type)
            if isinstance(out, CPythonBackedPythonLikeObject):
                # Mark the item as created from python
                getattr(out, '$markValidPythonReference')()
            put_in_instance_map(instance_map, value, out)
            CPythonBackedPythonInterpreter.updateJavaObjectFromPythonObject(out,
                                                                            JProxy(OpaquePythonReference, inst=value,
                                                                                   convert=True),
                                                                            instance_map)

            if isinstance(out, AbstractPythonLikeObject):
                for (key, value) in getattr(value, '__dict__', dict()).items():
                    out.setAttribute(key, convert_to_java_python_like_object(value, instance_map))

            return out
        except:
            return None


def is_banned_module(module: str):
    banned_modules = {'jpype', 'importlib', 'builtins'}
    for banned_module in banned_modules:
        if module == banned_module:
            return True
        elif module == f'_{banned_module}':
            return True
        elif module.startswith(f'{banned_module}.'):
            return True
        elif module.startswith(f'_{banned_module}.'):
            return True
    return False


def convert_to_java_python_like_object(value, instance_map=None):
    from java.util import HashMap
    from java.math import BigInteger
    from types import ModuleType
    from ai.timefold.jpyinterpreter import PythonLikeObject, CPythonBackedPythonInterpreter
    from ai.timefold.jpyinterpreter.types import PythonString, PythonBytes, PythonByteArray, PythonNone, \
        PythonModule, PythonSlice, PythonRange, NotImplemented as JavaNotImplemented
    from ai.timefold.jpyinterpreter.types.collections import PythonLikeList, PythonLikeTuple, PythonLikeSet, \
        PythonLikeFrozenSet, PythonLikeDict
    from ai.timefold.jpyinterpreter.types.numeric import PythonInteger, PythonFloat, PythonBoolean, PythonComplex
    from ai.timefold.jpyinterpreter.types.wrappers import PythonObjectWrapper, CPythonType, OpaquePythonReference

    global type_to_compiled_java_class

    if instance_map is None:
        instance_map = HashMap()

    if instance_map.containsKey(JLong(id(value))):
        return instance_map.get(JLong(id(value)))
    elif isinstance(value, PythonLikeObject):
        put_in_instance_map(instance_map, value, value)
        return value
    elif value is None:
        return PythonNone.INSTANCE
    elif value is NotImplemented:
        return JavaNotImplemented.INSTANCE
    elif isinstance(value, bool):
        return PythonBoolean.valueOf(JBoolean(value))
    elif isinstance(value, int):
        out = PythonInteger.valueOf(BigInteger("{0:x}".format(value), 16))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, float):
        out = PythonFloat.valueOf(JDouble(value))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, complex):
        out = PythonComplex.valueOf(convert_to_java_python_like_object(value.real, instance_map),
                                    convert_to_java_python_like_object(value.imag, instance_map))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, str):
        out = PythonString.valueOf(value)
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, bytes):
        out = PythonBytes.fromIntTuple(convert_to_java_python_like_object(tuple(value)))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, bytearray):
        out = PythonByteArray.fromIntTuple(convert_to_java_python_like_object(tuple(value)))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, tuple):
        out = PythonLikeTuple()
        put_in_instance_map(instance_map, value, out)
        for item in value:
            out.add(convert_to_java_python_like_object(item, instance_map))
        return out
    elif isinstance(value, list):
        out = PythonLikeList()
        put_in_instance_map(instance_map, value, out)
        for item in value:
            out.add(convert_to_java_python_like_object(item, instance_map))
        return out
    elif isinstance(value, set):
        out = PythonLikeSet()
        put_in_instance_map(instance_map, value, out)
        for item in value:
            out.add(convert_to_java_python_like_object(item, instance_map))
        return out
    elif isinstance(value, frozenset):
        out = PythonLikeFrozenSet()
        put_in_instance_map(instance_map, value, out)
        for item in value:
            out.delegate.add(convert_to_java_python_like_object(item, instance_map))
        return out
    elif isinstance(value, dict):
        out = PythonLikeDict()
        put_in_instance_map(instance_map, value, out)
        for map_key, map_value in value.items():
            out.put(convert_to_java_python_like_object(map_key, instance_map),
                    convert_to_java_python_like_object(map_value, instance_map))
        return out
    elif isinstance(value, slice):
        out = PythonSlice(convert_to_java_python_like_object(value.start, instance_map),
                          convert_to_java_python_like_object(value.stop, instance_map),
                          convert_to_java_python_like_object(value.step, instance_map))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, range):
        out = PythonRange(convert_to_java_python_like_object(value.start, instance_map),
                          convert_to_java_python_like_object(value.stop, instance_map),
                          convert_to_java_python_like_object(value.step, instance_map))
        put_in_instance_map(instance_map, value, out)
        return out
    elif isinstance(value, type):
        raw_type = erase_generic_args(value)
        if raw_type in type_to_compiled_java_class:
            if type_to_compiled_java_class[raw_type] is None:
                return None
            out = type_to_compiled_java_class[raw_type]
            put_in_instance_map(instance_map, value, out)
            return out
        else:
            out = translate_python_class_to_java_class(raw_type)
            put_in_instance_map(instance_map, value, out)
            return out
    elif isinstance(value, ModuleType) and repr(value).startswith('<module \'') and not \
            is_banned_module(value.__name__):  # should not convert java modules
        out = PythonModule(instance_map)
        out.setPythonReference(JProxy(OpaquePythonReference, inst=value, convert=True))
        put_in_instance_map(instance_map, value, out)
        # Module is populated lazily
        return out
    else:
        out = convert_object_to_java_python_like_object(value, instance_map)
        if out is not None:
            return out

        proxy = JProxy(OpaquePythonReference, inst=value, convert=True)
        out = PythonObjectWrapper(proxy)
        put_in_instance_map(instance_map, value, out)
        CPythonBackedPythonInterpreter.updateJavaObjectFromPythonObject(out,
                                                                        proxy,
                                                                        instance_map)
        return out


@dataclass
class PythonCloneMap:
    java_object_to_clone_id: 'IdentityHashMap'
    clone_id_to_python_object: dict

    def add_clone(self, java_object, python_object):
        object_id = self.java_object_to_clone_id.size()
        self.java_object_to_clone_id[java_object] = object_id
        self.clone_id_to_python_object[object_id] = python_object
        return python_object

    def has_clone(self, java_object):
        return self.java_object_to_clone_id.containsKey(java_object)

    def get_clone(self, java_object):
        return self.clone_id_to_python_object[self.java_object_to_clone_id.get(java_object)]


def unwrap_python_like_object(python_like_object, clone_map=None, default=NotImplementedError):
    from ai.timefold.jpyinterpreter import PythonLikeObject
    from java.util import List, Map, Set, Iterator, IdentityHashMap
    from ai.timefold.jpyinterpreter.types import PythonString, PythonBytes, PythonByteArray, PythonNone, \
        PythonModule, PythonSlice, PythonRange, CPythonBackedPythonLikeObject, PythonLikeType, PythonLikeGenericType, \
        NotImplemented as JavaNotImplemented, PythonCell
    from ai.timefold.jpyinterpreter.types.collections import PythonLikeList, PythonLikeTuple, PythonLikeSet, \
        PythonLikeFrozenSet, PythonLikeDict
    from ai.timefold.jpyinterpreter.types.numeric import PythonInteger, PythonFloat, PythonBoolean, PythonComplex
    from ai.timefold.jpyinterpreter.types.wrappers import JavaObjectWrapper, PythonObjectWrapper, CPythonType, \
        OpaquePythonReference
    from types import CellType

    if clone_map is None:
        clone_map = PythonCloneMap(IdentityHashMap(), dict())

    if clone_map.has_clone(python_like_object):
        return clone_map.get_clone(python_like_object)

    if isinstance(python_like_object, (PythonObjectWrapper, JavaObjectWrapper)):
        out = python_like_object.getWrappedObject()
        return clone_map.add_clone(python_like_object, out)
    elif isinstance(python_like_object, PythonNone):
        return clone_map.add_clone(python_like_object, None)
    elif isinstance(python_like_object, JavaNotImplemented):
        return clone_map.add_clone(python_like_object, NotImplemented)
    elif isinstance(python_like_object, PythonFloat):
        return clone_map.add_clone(python_like_object, float(python_like_object.getValue()))
    elif isinstance(python_like_object, PythonString):
        return clone_map.add_clone(python_like_object, python_like_object.getValue())
    elif isinstance(python_like_object, PythonBytes):
        return clone_map.add_clone(python_like_object,
                                   bytes(unwrap_python_like_object(python_like_object.asIntTuple(),
                                                                   clone_map, default)))
    elif isinstance(python_like_object, PythonByteArray):
        return clone_map.add_clone(python_like_object, bytearray(unwrap_python_like_object(
            python_like_object.asIntTuple(), clone_map, default)))
    elif isinstance(python_like_object, PythonBoolean):
        return clone_map.add_clone(python_like_object, python_like_object == PythonBoolean.TRUE)
    elif isinstance(python_like_object, PythonInteger):
        return clone_map.add_clone(python_like_object, int(python_like_object.getValue().toString(16), 16))
    elif isinstance(python_like_object, PythonComplex):
        real = unwrap_python_like_object(python_like_object.getReal(), clone_map, default)
        imaginary = unwrap_python_like_object(python_like_object.getImaginary(), clone_map, default)
        return clone_map.add_clone(python_like_object, complex(real, imaginary))
    elif isinstance(python_like_object, (PythonLikeTuple, tuple)):
        out = []
        for item in python_like_object:
            out.append(unwrap_python_like_object(item, clone_map, default))
        return clone_map.add_clone(python_like_object, tuple(out))
    elif isinstance(python_like_object, List):
        out = []
        clone_map.add_clone(python_like_object, out)
        for item in python_like_object:
            out.append(unwrap_python_like_object(item, clone_map, default))
        return out
    elif isinstance(python_like_object, Set):
        out = set()
        if not isinstance(python_like_object, PythonLikeFrozenSet):
            clone_map.add_clone(python_like_object, out)

        for item in python_like_object:
            out.add(unwrap_python_like_object(item, clone_map, default))

        if isinstance(python_like_object, PythonLikeFrozenSet):
            return clone_map.add_clone(python_like_object, frozenset(out))

        return out
    elif isinstance(python_like_object, Map):
        out = dict()
        clone_map.add_clone(python_like_object, out)
        for entry in python_like_object.entrySet():
            out[unwrap_python_like_object(entry.getKey(), clone_map, default)] = (
                unwrap_python_like_object(entry.getValue(), clone_map, default))
        return out
    elif isinstance(python_like_object, PythonSlice):
        return clone_map.add_clone(python_like_object, slice(
                     unwrap_python_like_object(python_like_object.start, clone_map, default),
                     unwrap_python_like_object(python_like_object.stop, clone_map, default),
                     unwrap_python_like_object(python_like_object.step, clone_map, default)))
    elif isinstance(python_like_object, PythonRange):
        return clone_map.add_clone(python_like_object, range(unwrap_python_like_object(python_like_object.start, clone_map, default),
                     unwrap_python_like_object(python_like_object.stop, clone_map, default),
                     unwrap_python_like_object(python_like_object.step, clone_map, default)))
    elif isinstance(python_like_object, Iterator):
        class JavaIterator:
            def __init__(self, iterator):
                self.iterator = iterator

            def __iter__(self):
                return self

            def __next__(self):
                try:
                    if not self.iterator.hasNext():
                        raise StopIteration()
                    else:
                        return unwrap_python_like_object(self.iterator.next(), clone_map, default)
                except StopIteration:
                    raise
                except Exception as e:
                    raise unwrap_python_like_object(e, clone_map, default)

            def send(self, sent):
                try:
                    return unwrap_python_like_object(self.iterator.send(convert_to_java_python_like_object(sent)),
                                                     clone_map,
                                                     default)
                except Exception as e:
                    raise unwrap_python_like_object(e, clone_map, default)

            def throw(self, thrown):
                try:
                    return unwrap_python_like_object(
                        self.iterator.throwValue(convert_to_java_python_like_object(thrown)),
                        clone_map, default)
                except Exception as e:
                    raise unwrap_python_like_object(e, clone_map, default)

        return clone_map.add_clone(python_like_object, JavaIterator(python_like_object))
    elif isinstance(python_like_object, PythonCell):
        out = CellType()
        clone_map.add_clone(python_like_object, out)
        out.cell_contents = unwrap_python_like_object(python_like_object.cellValue, clone_map, default)
        return out
    elif isinstance(python_like_object, PythonModule):
        return clone_map.add_clone(python_like_object, python_like_object.getPythonReference())
    elif isinstance(python_like_object, CPythonBackedPythonLikeObject):
        if getattr(python_like_object, '$shouldCreateNewInstance')():
            maybe_cpython_type = getattr(python_like_object, "$CPYTHON_TYPE")
            if isinstance(maybe_cpython_type, CPythonType):
                out = object.__new__(maybe_cpython_type.getPythonReference())
                setattr(python_like_object, '$cpythonReference', JProxy(OpaquePythonReference, inst=out, convert=True))
                setattr(python_like_object, '$cpythonId', PythonInteger.valueOf(JLong(id(out))))
            else:
                out = None
        else:
            out = getattr(python_like_object, '$cpythonReference')

        if out is not None:
            clone_map.add_clone(python_like_object, out)
            update_python_object_from_java(python_like_object, clone_map)
            return out
    elif isinstance(python_like_object, Exception):
        try:
            exception_name = getattr(python_like_object, '$TYPE').getTypeName()
            exception_python_type = getattr(builtins, exception_name)
            args = unwrap_python_like_object(getattr(python_like_object, '$getArgs')(),
                                             clone_map, default)
            return clone_map.add_clone(python_like_object, exception_python_type(*args))
        except AttributeError:
            return clone_map.add_clone(python_like_object, TranslatedJavaSystemError(python_like_object))
    elif isinstance(python_like_object, PythonLikeType):
        if python_like_object.getClass() == PythonLikeGenericType:
            return clone_map.add_clone(python_like_object, type)

        for (key, value) in type_to_compiled_java_class.items():
            if value == python_like_object:
                return clone_map.add_clone(python_like_object, key)
        else:
            raise KeyError(f'Cannot find corresponding Python type for Java class {python_like_object.getClass().getName()}')
    elif not isinstance(python_like_object, PythonLikeObject):
        return clone_map.add_clone(python_like_object, python_like_object)
    else:
        out = unwrap_python_like_builtin_module_object(python_like_object, clone_map, default)
        if out is not None:
            return out

        if default == NotImplementedError:
            raise NotImplementedError(f'Unable to convert object of type {type(python_like_object)}')
        return default


def update_python_object_from_java(java_object, clone_map=None):
    from java.util import IdentityHashMap
    from ai.timefold.jpyinterpreter.types.wrappers import OpaquePythonReference
    if clone_map is None:
        clone_map = PythonCloneMap(IdentityHashMap(), dict())

    try:
        getattr(java_object, '$writeFieldsToCPythonReference')(JProxy(OpaquePythonReference,
                                                                             inst=clone_map,
                                                                             convert=True))
    except TypeError:
        # The Python Object is immutable; so no changes from Java
        pass


def unwrap_python_like_builtin_module_object(python_like_object, clone_map, default=NotImplementedError):
    from java.util import IdentityHashMap
    from ai.timefold.jpyinterpreter.types.datetime import PythonDate, PythonTime, PythonDateTime, PythonTimeDelta
    import datetime

    if clone_map is None:
        clone_map = PythonCloneMap(IdentityHashMap(), dict())

    if isinstance(python_like_object, PythonDateTime):
        return clone_map.add_clone(python_like_object, datetime.datetime(unwrap_python_like_object(python_like_object.year, clone_map, default),
                                 unwrap_python_like_object(python_like_object.month, clone_map, default),
                                 unwrap_python_like_object(python_like_object.day, clone_map, default),
                                 unwrap_python_like_object(python_like_object.hour, clone_map, default),
                                 unwrap_python_like_object(python_like_object.minute, clone_map, default),
                                 unwrap_python_like_object(python_like_object.second, clone_map, default),
                                 unwrap_python_like_object(python_like_object.microsecond, clone_map, default),
                                 tzinfo=None,  # TODO: Support timezones
                                 fold=unwrap_python_like_object(python_like_object.fold, clone_map, default)))

    if isinstance(python_like_object, PythonDate):
        return clone_map.add_clone(python_like_object, datetime.date(unwrap_python_like_object(python_like_object.year, clone_map, default),
                             unwrap_python_like_object(python_like_object.month, clone_map, default),
                             unwrap_python_like_object(python_like_object.day, clone_map, default)))

    if isinstance(python_like_object, PythonTime):
        return clone_map.add_clone(python_like_object, datetime.time(unwrap_python_like_object(python_like_object.hour, clone_map, default),
                             unwrap_python_like_object(python_like_object.minute, clone_map, default),
                             unwrap_python_like_object(python_like_object.second, clone_map, default),
                             unwrap_python_like_object(python_like_object.microsecond, clone_map, default),
                             tzinfo=None,  # TODO: Support timezones
                             fold=unwrap_python_like_object(python_like_object.fold, clone_map, default)))

    if isinstance(python_like_object, PythonTimeDelta):
        return clone_map.add_clone(python_like_object, datetime.timedelta(unwrap_python_like_object(python_like_object.days, clone_map, default),
                                  unwrap_python_like_object(python_like_object.seconds, clone_map, default),
                                  unwrap_python_like_object(python_like_object.microseconds, clone_map, default)))

    return None

def get_java_type_for_python_type(the_type):
    from ai.timefold.jpyinterpreter.types import BuiltinTypes
    global type_to_compiled_java_class

    if isinstance(the_type, type):
        the_type = erase_generic_args(the_type)
        if the_type in type_to_compiled_java_class:
            return type_to_compiled_java_class[the_type]
        else:
            try:
                return translate_python_class_to_java_class(the_type)
            except:
                return type_to_compiled_java_class[the_type]
    if isinstance(the_type, str):
        try:
            the_type = erase_generic_args(the_type)
            maybe_type = globals()[the_type]
            if isinstance(maybe_type, type):
                return get_java_type_for_python_type(maybe_type)
            return BuiltinTypes.BASE_TYPE
        except:
            return BuiltinTypes.BASE_TYPE
    # return base type, since users could use something like 1
    return BuiltinTypes.BASE_TYPE


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def copy_type_annotations(hinted_object, default_args, vargs_name, kwargs_name):
    from java.util import HashMap, Collections
    from ai.timefold.jpyinterpreter import TypeHint

    global type_to_compiled_java_class

    out = HashMap()
    type_hints = get_type_hints(hinted_object, include_extras=True)

    for name, type_hint in type_hints.items():
        if not isinstance(name, str):
            continue
        if name == vargs_name:
            out.put(name, TypeHint.withoutAnnotations(type_to_compiled_java_class[tuple]))
            continue
        if name == kwargs_name:
            out.put(name, TypeHint.withoutAnnotations(type_to_compiled_java_class[dict]))
            continue
        hint_type = type_hint
        hint_annotations = Collections.emptyList()
        if get_origin(type_hint) is Annotated:
            hint_type = get_args(type_hint)[0]
            hint_annotations = get_java_annotations(type_hint.__metadata__)

        if name in default_args:
            hint_type = Union[hint_type, type(default_args[name])]

        java_type_hint = get_java_type_hint(hint_type)
        out.put(name, java_type_hint.addAnnotations(hint_annotations))

    return out


def get_java_type_hint(hint_type):
    from typing import get_args as get_generic_args
    from java.lang import Class as JavaClass
    from java.util import Collections
    from ai.timefold.jpyinterpreter import TypeHint
    from ai.timefold.jpyinterpreter.types import BuiltinTypes
    from ai.timefold.jpyinterpreter.types.wrappers import JavaObjectWrapper
    origin_type = get_origin(hint_type)
    if origin_type is None:
        # Happens for Callable[[parameter_types], return_type]
        if isinstance(hint_type, list) or isinstance(hint_type, tuple):
            return TypeHint(BuiltinTypes.BASE_TYPE, Collections.emptyList())
        # Not a generic type
        elif hint_type in type_to_compiled_java_class:
            return TypeHint(type_to_compiled_java_class[hint_type], Collections.emptyList())
        elif isinstance(hint_type, (JClass, JavaClass)):
            java_type = JavaObjectWrapper.getPythonTypeForClass(hint_type)
            type_to_compiled_java_class[hint_type] = java_type
            return TypeHint(java_type, Collections.emptyList())
        elif isinstance(hint_type, (type, str)):
            return TypeHint(get_java_type_for_python_type(hint_type), Collections.emptyList())
        else:
            return TypeHint(BuiltinTypes.BASE_TYPE, Collections.emptyList())

    origin_type_hint = get_java_type_hint(origin_type)
    generic_args = get_generic_args(hint_type)
    generic_arg_type_hint_array = JArray(TypeHint)(len(generic_args))
    for i in range(len(generic_args)):
        generic_arg_type_hint_array[i] = get_java_type_hint(generic_args[i])
    return TypeHint(origin_type_hint.type(), Collections.emptyList(), generic_arg_type_hint_array)


def get_java_annotations(annotated_metadata: List[Any]):
    from java.util import ArrayList
    out = ArrayList()
    for metadata in annotated_metadata:
        if not isinstance(metadata, JavaAnnotation):
            if isinstance(metadata, type) and issubclass(metadata, JavaAnnotation):
                try:
                    metadata = metadata()
                except TypeError as e:
                    raise ValueError(f'The annotation class {metadata.__name__} has required attributes.'
                                     f'Create an instance using {metadata.__name__}(...).') from e
            else:
                continue
        out.add(convert_java_annotation(metadata))
    return out


def convert_java_annotation(java_annotation: JavaAnnotation):
    from java.util import HashMap
    from ai.timefold.jpyinterpreter import AnnotationMetadata
    annotation_values = HashMap()
    for attribute_name, attribute_value in java_annotation.annotation_values.items():
        annotation_method = java_annotation.annotation_type.class_.getDeclaredMethod(attribute_name)
        attribute_type = annotation_method.getReturnType()
        java_attribute_value = convert_annotation_value(java_annotation.annotation_type, attribute_type,
                                                        attribute_name, attribute_value)
        if java_attribute_value is not None:
            annotation_values.put(attribute_name, java_attribute_value)
    return AnnotationMetadata(java_annotation.annotation_type.class_, annotation_values)


def convert_annotation_value(annotation_type: JClass, attribute_type: JClass, attribute_name: str, attribute_value: Any):
    from jpype import JBoolean, JByte, JChar, JShort, JInt, JLong, JFloat, JDouble, JString, JArray

    if attribute_value is None:
        return None
    # See 9.6.1 of the Java spec for possible element values of annotations
    if attribute_type == JClass('boolean').class_:
        return JBoolean(attribute_value)
    elif attribute_type == JClass('byte').class_:
        return JByte(attribute_value)
    elif attribute_type == JClass('char').class_:
        return JChar(attribute_value)
    elif attribute_type == JClass('short').class_:
        return JShort(attribute_value)
    elif attribute_type == JClass('int').class_:
        return JInt(attribute_value)
    elif attribute_type == JClass('long').class_:
        return JLong(attribute_value)
    elif attribute_type == JClass('float').class_:
        return JFloat(attribute_value)
    elif attribute_type == JClass('double').class_:
        return JDouble(attribute_value)
    elif attribute_type == JClass('java.lang.String').class_:
        return JString(attribute_value)
    elif attribute_type == JClass('java.lang.Class').class_:
        if isinstance(attribute_value, JClass('java.lang.Class')):
            return attribute_value
        elif isinstance(attribute_value, type):
            return get_java_type_for_python_type(attribute_type)
        elif isinstance(attribute_value, FunctionType):
            method = annotation_type.class_.getDeclaredMethod(attribute_name)
            generic_type = method.getGenericReturnType()
            try:
                function_type_and_generic_args = resolve_java_function_type_as_tuple(generic_type)
                instance = translate_python_bytecode_to_java_bytecode(attribute_value, *function_type_and_generic_args)
                return generate_proxy_class_for_translated_function(function_type_and_generic_args[0], instance)
            except ValueError:
                raw_type = resolve_raw_type(generic_type.getActualTypeArguments()[0])
                instance = translate_python_bytecode_to_java_bytecode(attribute_value, raw_type)
                return generate_proxy_class_for_translated_function(raw_type, instance)
        else:
            raise ValueError(f'Illegal value for {attribute_name} in annotation {annotation_type}: {attribute_value}')
    elif attribute_type.isEnum():
        return attribute_value
    elif attribute_type.isArray():
        dimensions = get_dimensions(attribute_type)
        component_type = get_component_type(attribute_type)
        return JArray(component_type, dims=dimensions)(convert_annotation_array_elements(annotation_type,
                                                                                         component_type.class_,
                                                                                         attribute_name,
                                                                                         attribute_value))
    elif JClass('java.lang.Annotation').class_.isAssignableFrom(attribute_type):
        if not isinstance(attribute_value, JavaAnnotation):
            raise ValueError(f'Illegal value for {attribute_name} in annotation {annotation_type}: {attribute_value}')
        return convert_java_annotation(attribute_value)
    else:
        raise ValueError(f'Illegal type for annotation element {attribute_type} for element named '
                         f'{attribute_name} on annotation type {annotation_type}.')


def generate_proxy_class_for_translated_function(interface_type, translated_function):
    from ai.timefold.jpyinterpreter import InterfaceProxyGenerator
    return InterfaceProxyGenerator.generateProxyForFunction(interface_type, translated_function)


def generate_proxy_class_for_translated_class(interface_type, translated_class):
    from ai.timefold.jpyinterpreter import InterfaceProxyGenerator
    return InterfaceProxyGenerator.generateProxyForClass(interface_type, translated_class)



def resolve_java_function_type_as_tuple(function_class) -> Tuple[JClass]:
    from java.lang.reflect import ParameterizedType, WildcardType
    if isinstance(function_class, WildcardType):
        return resolve_java_type_as_tuple(function_class.getUpperBounds()[0])
    elif isinstance(function_class, ParameterizedType):
        return resolve_java_type_as_tuple(function_class.getActualTypeArguments()[0])
    else:
        raise ValueError(f'Unable to determine interface for type {function_class}')


def resolve_java_type_as_tuple(generic_type) -> Tuple[JClass]:
    from java.lang.reflect import ParameterizedType, WildcardType
    if isinstance(generic_type, WildcardType):
        return (*map(resolve_java_type_as_tuple, generic_type.getUpperBounds()),)
    elif isinstance(generic_type, ParameterizedType):
        return resolve_raw_types(generic_type.getRawType(), *generic_type.getActualTypeArguments())
    elif isinstance(generic_type, JClass):
        return (generic_type,)
    else:
        raise ValueError(f'Unable to determine interface for type {generic_type}')


def resolve_raw_types(*type_arguments) -> Tuple[JClass]:
    return (*map(resolve_raw_type, type_arguments),)


def resolve_raw_type(type_argument) -> JClass:
    from java.lang.reflect import ParameterizedType, WildcardType
    if isinstance(type_argument, ParameterizedType):
        return resolve_raw_type(type_argument.getRawType())
    elif isinstance(type_argument, WildcardType):
        return resolve_raw_type(type_argument.getUpperBounds()[0])
    return type_argument


def convert_annotation_array_elements(annotation_type: JClass, component_type: JClass, attribute_name: str,
                                      array_elements: List) -> List:
    out = []
    for item in array_elements:
        if isinstance(item, (list, tuple)):
            out.append(convert_annotation_array_elements(annotation_type, component_type, attribute_name, item))
        else:
            out.append(convert_annotation_value(annotation_type, component_type, attribute_name, item))
    return out


def get_dimensions(array_type: JClass) -> int:
    if array_type.getComponentType() is None:
        return 0
    return get_dimensions(array_type.getComponentType()) + 1


def get_component_type(array_type: JClass) -> JClass:
    if not array_type.getComponentType().isArray():
        return JClass(array_type.getComponentType().getCanonicalName())
    return get_component_type(array_type.getComponentType())


def copy_constants(constants_iterable):
    from java.util import ArrayList
    from ai.timefold.jpyinterpreter import CPythonBackedPythonInterpreter
    if constants_iterable is None:
        return None
    iterable_copy = ArrayList()
    for item in constants_iterable:
        iterable_copy.add(convert_to_java_python_like_object(item, CPythonBackedPythonInterpreter.pythonObjectIdToConvertedObjectMap))
    return iterable_copy


def copy_closure(closure):
    from ai.timefold.jpyinterpreter.types import PythonCell
    from ai.timefold.jpyinterpreter.types.collections import PythonLikeTuple
    from ai.timefold.jpyinterpreter import CPythonBackedPythonInterpreter
    out = PythonLikeTuple()
    if closure is None:
        return out
    else:
        for cell in closure:
            java_cell = PythonCell()
            java_cell.cellValue = convert_to_java_python_like_object(cell.cell_contents, CPythonBackedPythonInterpreter.pythonObjectIdToConvertedObjectMap)
            out.add(java_cell)
        return out


def copy_globals(globals_dict, co_names):
    global global_dict_to_instance
    global global_dict_to_key_set
    from java.util import HashMap
    from ai.timefold.jpyinterpreter import CPythonBackedPythonInterpreter

    globals_dict_key = id(globals_dict)
    if globals_dict_key in global_dict_to_instance:
        out = global_dict_to_instance[globals_dict_key]
        key_set = global_dict_to_key_set[globals_dict_key]
    else:
        out = HashMap()
        key_set = set()
        global_dict_to_instance[globals_dict_key] = out
        global_dict_to_key_set[globals_dict_key] = key_set

    instance_map = CPythonBackedPythonInterpreter.pythonObjectIdToConvertedObjectMap
    for key, value in globals_dict.items():
        if key not in key_set and key in co_names:
            key_set.add(key)
            out.put(key, convert_to_java_python_like_object(value, instance_map))
    return out


def find_globals_dict_for_java_map(java_globals):
    for python_global_id in global_dict_to_instance:
        if global_dict_to_instance[python_global_id] == java_globals:
            return ctypes.cast(python_global_id, ctypes.py_object).value

    raise ValueError(f'Could not find python globals corresponding to {str(java_globals.toString())}')


def get_instructions(python_function):
    try:
        yield from dis.get_instructions(python_function, show_caches=True)  # Python 3.11 and above
    except TypeError:  # Python 3.10 and below
        yield from dis.get_instructions(python_function)


# From https://github.com/python/cpython/blob/main/Objects/exception_handling_notes.txt
def parse_varint(iterator):
    b = next(iterator)
    val = b & 63
    while b&64:
        val <<= 6
        b = next(iterator)
        val |= b&63
    return val


# From https://github.com/python/cpython/blob/main/Objects/exception_handling_notes.txt
def parse_exception_table(code):
    iterator = iter(code.co_exceptiontable)
    try:
        while True:
            start = parse_varint(iterator)*2
            length = parse_varint(iterator)*2
            end = start + length - 2 # Present as inclusive, not exclusive
            target = parse_varint(iterator)*2
            dl = parse_varint(iterator)
            depth = dl >> 1
            lasti = bool(dl&1)
            yield start, end, target, depth, lasti
    except StopIteration:
        return


def get_python_exception_table(python_code):
    from ai.timefold.jpyinterpreter import PythonExceptionTable, PythonVersion
    out = PythonExceptionTable()

    if hasattr(python_code, 'co_exceptiontable'):
        python_version = PythonVersion(sys.hexversion)
        for start, end, target, depth, lasti in parse_exception_table(python_code):
            out.addEntry(python_version, start, end, target, depth, lasti)

    return out


def get_function_bytecode_object(python_function):
    from java.util import ArrayList
    from ai.timefold.jpyinterpreter import PythonBytecodeInstruction, PythonCompiledFunction, PythonVersion # noqa

    init_type_to_compiled_java_class()

    python_compiled_function = PythonCompiledFunction()
    instruction_list = ArrayList()
    for instruction in get_instructions(python_function):
        java_instruction = (
            PythonBytecodeInstruction
            .atOffset(instruction.opname, JInt(instruction.offset // 2))
            .withIsJumpTarget(JBoolean(instruction.is_jump_target)))
        if instruction.arg is not None:
            java_instruction = java_instruction.withArg(instruction.arg)
        if instruction.starts_line:
            java_instruction = java_instruction.startsLine(instruction.starts_line)

        instruction_list.add(java_instruction)

    python_compiled_function.module = python_function.__module__
    python_compiled_function.qualifiedName = python_function.__qualname__
    python_compiled_function.instructionList = instruction_list
    python_compiled_function.co_exceptiontable = get_python_exception_table(python_function.__code__)
    python_compiled_function.co_names = copy_iterable(python_function.__code__.co_names)
    python_compiled_function.co_varnames = copy_variable_names(python_function.__code__.co_varnames)
    python_compiled_function.co_cellvars = copy_variable_names(python_function.__code__.co_cellvars)
    python_compiled_function.co_freevars = copy_variable_names(python_function.__code__.co_freevars)
    python_compiled_function.co_constants = copy_constants(python_function.__code__.co_consts)
    python_compiled_function.co_argcount = python_function.__code__.co_argcount
    python_compiled_function.co_kwonlyargcount = python_function.__code__.co_kwonlyargcount
    python_compiled_function.closure = copy_closure(python_function.__closure__)
    python_compiled_function.globalsMap = copy_globals(python_function.__globals__, python_function.__code__.co_names)
    python_compiled_function.typeAnnotations = copy_type_annotations(python_function,
                                                                     get_default_args(python_function),
                                                                     inspect.getfullargspec(python_function).varargs,
                                                                     inspect.getfullargspec(python_function).varkw)
    python_compiled_function.defaultPositionalArguments = convert_to_java_python_like_object(
        python_function.__defaults__ if python_function.__defaults__ else tuple())
    python_compiled_function.defaultKeywordArguments = convert_to_java_python_like_object(
        python_function.__kwdefaults__ if python_function.__kwdefaults__ else dict())
    python_compiled_function.supportExtraPositionalArgs = inspect.getfullargspec(python_function).varargs is not None
    python_compiled_function.supportExtraKeywordsArgs = inspect.getfullargspec(python_function).varkw is not None
    python_compiled_function.pythonVersion = PythonVersion(sys.hexversion)
    return python_compiled_function


def get_static_function_bytecode_object(the_class, python_function):
    return get_function_bytecode_object(python_function.__get__(the_class))


def get_code_bytecode_object(python_code):
    from java.util import ArrayList, HashMap
    from ai.timefold.jpyinterpreter import PythonBytecodeInstruction, PythonCompiledFunction, PythonVersion # noqa

    init_type_to_compiled_java_class()

    python_compiled_function = PythonCompiledFunction()
    instruction_list = ArrayList()
    for instruction in get_instructions(python_code):
        java_instruction = (
            PythonBytecodeInstruction
            .atOffset(instruction.opname, JInt(instruction.offset // 2))
            .withIsJumpTarget(JBoolean(instruction.is_jump_target)))
        if instruction.arg is not None:
            java_instruction = java_instruction.withArg(instruction.arg)
        if instruction.starts_line:
            java_instruction = java_instruction.startsLine(instruction.starts_line)
        instruction_list.add(java_instruction)

    python_compiled_function.module = '__code__'
    python_compiled_function.qualifiedName = '__code__'
    python_compiled_function.instructionList = instruction_list
    python_compiled_function.co_exceptiontable = get_python_exception_table(python_code)
    python_compiled_function.co_names = copy_iterable(python_code.co_names)
    python_compiled_function.co_varnames = copy_variable_names(python_code.co_varnames)
    python_compiled_function.co_cellvars = copy_variable_names(python_code.co_cellvars)
    python_compiled_function.co_freevars = copy_variable_names(python_code.co_freevars)
    python_compiled_function.co_constants = copy_constants(python_code.co_consts)
    python_compiled_function.co_argcount = python_code.co_argcount
    python_compiled_function.co_kwonlyargcount = python_code.co_kwonlyargcount
    python_compiled_function.closure = copy_closure(None)
    python_compiled_function.globalsMap = HashMap()
    python_compiled_function.typeAnnotations = HashMap()
    python_compiled_function.defaultPositionalArguments = convert_to_java_python_like_object(tuple())
    python_compiled_function.defaultKeywordArguments = convert_to_java_python_like_object(dict())
    python_compiled_function.typeAnnotations = HashMap()
    python_compiled_function.supportExtraPositionalArgs = False
    python_compiled_function.supportExtraKeywordsArgs = False
    python_compiled_function.pythonVersion = PythonVersion(sys.hexversion)
    return python_compiled_function


def translate_python_bytecode_to_java_bytecode(python_function, java_function_type, *type_args):
    from ai.timefold.jpyinterpreter import PythonBytecodeToJavaBytecodeTranslator # noqa
    if (python_function, java_function_type, type_args) in function_interface_pair_to_instance:
        return function_interface_pair_to_instance[(python_function, java_function_type, type_args)]

    python_compiled_function = get_function_bytecode_object(python_function)

    if len(type_args) == 0:
        out = PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(python_compiled_function,
                                                                             java_function_type)
        function_interface_pair_to_instance[(python_function, java_function_type, type_args)] = out
        return out
    else:
        out = PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(python_compiled_function,
                                                                             java_function_type,
                                                                             copy_iterable(type_args))
        function_interface_pair_to_instance[(python_function, java_function_type, type_args)] = out
        return out


def _force_translate_python_bytecode_to_generator_java_bytecode(python_function, java_function_type):
    from ai.timefold.jpyinterpreter import PythonBytecodeToJavaBytecodeTranslator # noqa
    if (python_function, java_function_type) in function_interface_pair_to_instance:
        return function_interface_pair_to_instance[(python_function, java_function_type)]

    python_compiled_function = get_function_bytecode_object(python_function)

    out = PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(python_compiled_function,
                                                                         java_function_type)
    function_interface_pair_to_instance[(python_function, java_function_type)] = out
    return out


def translate_python_code_to_java_class(python_function, java_function_type, *type_args):
    from ai.timefold.jpyinterpreter import PythonBytecodeToJavaBytecodeTranslator # noqa
    if (python_function, java_function_type, type_args) in function_interface_pair_to_class:
        return function_interface_pair_to_class[(python_function, java_function_type, type_args)]

    python_compiled_function = get_code_bytecode_object(python_function)

    if len(type_args) == 0:
        out = PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecodeToClass(python_compiled_function,
                                                                                    java_function_type)
        function_interface_pair_to_class[(python_function, java_function_type, type_args)] = out
        return out
    else:
        out = PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecodeToClass(python_compiled_function,
                                                                                    java_function_type,
                                                                                    copy_iterable(type_args))
        function_interface_pair_to_class[(python_function, java_function_type, type_args)] = out
        return out


def translate_python_code_to_python_wrapper_class(python_function):
    from ai.timefold.jpyinterpreter import PythonBytecodeToJavaBytecodeTranslator # noqa
    from ai.timefold.jpyinterpreter.types.wrappers import OpaquePythonReference # noqa
    if (python_function,) in function_interface_pair_to_class:
        return function_interface_pair_to_class[(python_function,)]

    python_compiled_function = get_code_bytecode_object(python_function)
    out = PythonBytecodeToJavaBytecodeTranslator.\
        translatePythonBytecodeToPythonWrapperClass(python_compiled_function, JProxy(OpaquePythonReference,
                                                                                     CodeWrapper(python_function),
                                                                                     convert=True))
    function_interface_pair_to_class[(python_function,)] = out
    return out


def wrap_untyped_java_function(java_function):
    def wrapped_function(*args, **kwargs):
        from java.util import ArrayList, HashMap

        instance_map = HashMap()
        java_args = ArrayList(len(args))
        java_kwargs = HashMap()

        for arg in args:
            java_args.add(convert_to_java_python_like_object(arg, instance_map))

        for key, value in kwargs:
            java_kwargs.put(convert_to_java_python_like_object(key, instance_map),
                            convert_to_java_python_like_object(value, instance_map))

        try:
            return unwrap_python_like_object(getattr(java_function, '$call')(java_args, java_kwargs, None))
        except Exception as e:
            raise unwrap_python_like_object(e)

    return wrapped_function


def wrap_typed_java_function(java_function):
    def wrapped_function(*args):
        from java.util import ArrayList, HashMap

        instance_map = HashMap()
        java_args = [convert_to_java_python_like_object(arg, instance_map) for arg in args]

        try:
            return unwrap_python_like_object(java_function.invoke(*java_args))
        except Exception as e:
            raise unwrap_python_like_object(e)

    return wrapped_function


def as_java(python_function):
    return as_typed_java(python_function)


def as_untyped_java(python_function):
    from ai.timefold.jpyinterpreter.types import PythonLikeFunction
    java_function = translate_python_bytecode_to_java_bytecode(python_function, PythonLikeFunction)
    return wrap_untyped_java_function(java_function)


def as_typed_java(python_function):
    from ai.timefold.jpyinterpreter import PythonClassTranslator
    function_bytecode = get_function_bytecode_object(python_function)
    function_interface_declaration = PythonClassTranslator.getInterfaceForPythonFunction(function_bytecode)
    function_interface_class = PythonClassTranslator.getInterfaceClassForDeclaration(function_interface_declaration)
    java_function = translate_python_bytecode_to_java_bytecode(python_function, function_interface_class)
    return wrap_typed_java_function(java_function)


def _force_as_java_generator(python_function):
    from ai.timefold.jpyinterpreter.types import PythonLikeFunction
    java_function = _force_translate_python_bytecode_to_generator_java_bytecode(python_function,
                                                                                PythonLikeFunction)
    return wrap_untyped_java_function(java_function)


class MethodTypeHelper:
    @classmethod
    def class_method_type(cls):
        pass

    @staticmethod
    def static_method_type():
        pass


__CLASS_METHOD_TYPE = type(MethodTypeHelper.__dict__['class_method_type'])
__STATIC_METHOD_TYPE = type(MethodTypeHelper.__dict__['static_method_type'])


def force_update_type(python_type, java_type):
    global type_to_compiled_java_class
    type_to_compiled_java_class[python_type] = java_type


def erase_generic_args(python_type):
    from typing import get_origin
    if isinstance(python_type, type):
        out = python_type
        if get_origin(out) is not None:
            return get_origin(out)
        return out
    elif isinstance(python_type, str):
        try:
            generics_start = python_type.index('[')
            return python_type[generics_start:-2]
        except ValueError:
            return python_type
    else:
        raise ValueError


def translate_python_class_to_java_class(python_class):
    from java.lang import Class as JavaClass
    from java.util import ArrayList, HashMap
    from ai.timefold.jpyinterpreter import AnnotationMetadata, PythonCompiledClass, PythonClassTranslator, CPythonBackedPythonInterpreter # noqa
    from ai.timefold.jpyinterpreter.types import BuiltinTypes
    from ai.timefold.jpyinterpreter.types.wrappers import JavaObjectWrapper, OpaquePythonReference, CPythonType # noqa

    global type_to_compiled_java_class

    init_type_to_compiled_java_class()

    raw_type = erase_generic_args(python_class)
    if raw_type in type_to_compiled_java_class:
        return type_to_compiled_java_class[raw_type]

    if python_class == abc.ABC or inspect.isabstract(python_class):  # TODO: Implement a class for interfaces?
        python_class_java_type = BuiltinTypes.BASE_TYPE
        type_to_compiled_java_class[python_class] = python_class_java_type
        return python_class_java_type

    if hasattr(python_class, '__module__') and python_class.__module__ is not None and \
            is_banned_module(python_class.__module__):
        python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
        type_to_compiled_java_class[python_class] = python_class_java_type
        return python_class_java_type

    if isinstance(python_class, JArray):
        python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
        type_to_compiled_java_class[python_class] = python_class_java_type
        return python_class_java_type

    if isinstance(python_class, (JClass, JavaClass)):
        try:
            out = JavaObjectWrapper.getPythonTypeForClass(python_class)
            type_to_compiled_java_class[python_class] = out
            return out
        except TypeError:
            print(f'Bad type: {type(python_class)}, from {python_class}')
            python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
            type_to_compiled_java_class[python_class] = python_class_java_type
            return python_class_java_type

    if is_c_native(python_class):
        python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
        type_to_compiled_java_class[python_class] = python_class_java_type
        return python_class_java_type

    prepared_class_info = PythonClassTranslator.getPreparedClassInfo(python_class.__name__,
                                                                     python_class.__module__,
                                                                     python_class.__qualname__)
    type_to_compiled_java_class[python_class] = prepared_class_info.type()
    methods = []
    for method_name in python_class.__dict__:
        method = inspect.getattr_static(python_class, method_name)
        if inspect.isfunction(method) or \
                isinstance(method, __STATIC_METHOD_TYPE) or \
                isinstance(method, __CLASS_METHOD_TYPE):
            methods.append((method_name, method))

    static_attributes = inspect.getmembers(python_class, predicate=lambda member: not (inspect.isfunction(member)
                                                                                       or isinstance(member, __STATIC_METHOD_TYPE)
                                                                                       or isinstance(member, __CLASS_METHOD_TYPE)))
    static_attributes = [attribute for attribute in static_attributes if attribute[0] in python_class.__dict__]
    static_methods = [method for method in methods if isinstance(method[1], __STATIC_METHOD_TYPE)]
    class_methods = [method for method in methods if isinstance(method[1], __CLASS_METHOD_TYPE)]
    instance_methods = [method for method in methods if method not in static_methods and method not in class_methods]

    superclass_list = ArrayList()
    for superclass in python_class.__bases__:
        superclass = erase_generic_args(superclass)
        if superclass in type_to_compiled_java_class:
            if isinstance(type_to_compiled_java_class[superclass], CPythonType):
                python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
                type_to_compiled_java_class[python_class] = python_class_java_type
                return python_class_java_type
            superclass_list.add(type_to_compiled_java_class[superclass])
        else:
            try:
                superclass_list.add(translate_python_class_to_java_class(superclass))
                if isinstance(type_to_compiled_java_class[superclass], CPythonType):
                    python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
                    type_to_compiled_java_class[python_class] = python_class_java_type
                    return python_class_java_type
            except Exception:
                superclass_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=superclass, convert=True))
                type_to_compiled_java_class[superclass] = superclass_java_type
                python_class_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class, convert=True))
                type_to_compiled_java_class[python_class] = python_class_java_type
                return python_class_java_type

    static_method_map = HashMap()
    for method in static_methods:
        static_method_map.put(method[0], get_static_function_bytecode_object(python_class, method[1]))

    class_method_map = HashMap()
    for method in class_methods:
        class_method_map.put(method[0], get_static_function_bytecode_object(python_class, method[1]))

    instance_method_map = HashMap()
    for method in instance_methods:
        instance_method_map.put(method[0], get_function_bytecode_object(method[1]))

    static_attributes_map = HashMap()
    static_attributes_to_class_instance_map = HashMap()
    for attribute in static_attributes:
        attribute_type = type(attribute[1])
        if attribute_type == python_class:
            static_attributes_to_class_instance_map.put(attribute[0],
                                                        JProxy(OpaquePythonReference,
                                                               inst=attribute[1], convert=True))
        else:
            if attribute_type not in type_to_compiled_java_class:
                try:
                    translate_python_class_to_java_class(attribute_type)
                except:
                    superclass_java_type = CPythonType.getType(JProxy(OpaquePythonReference, inst=attribute_type, convert=True))
                    type_to_compiled_java_class[attribute_type] = superclass_java_type

            static_attributes_map.put(attribute[0], convert_to_java_python_like_object(attribute[1]))

    python_compiled_class = PythonCompiledClass()
    python_compiled_class.annotations = ArrayList()
    for annotation in type_to_annotations.get(python_class, []):
        python_compiled_class.annotations.add(convert_java_annotation(annotation))

    python_compiled_class.binaryType = CPythonType.getType(JProxy(OpaquePythonReference, inst=python_class,
                                                                  convert=True))
    python_compiled_class.module = python_class.__module__
    python_compiled_class.qualifiedName = python_class.__qualname__
    python_compiled_class.className = python_class.__name__
    python_compiled_class.typeAnnotations = copy_type_annotations(python_class,
                                                                  dict(),
                                                                  None,
                                                                  None)
    python_compiled_class.superclassList = superclass_list
    python_compiled_class.instanceFunctionNameToPythonBytecode = instance_method_map
    python_compiled_class.staticFunctionNameToPythonBytecode = static_method_map
    python_compiled_class.classFunctionNameToPythonBytecode = class_method_map
    python_compiled_class.staticAttributeNameToObject = static_attributes_map
    python_compiled_class.staticAttributeNameToClassInstance = static_attributes_to_class_instance_map

    out = PythonClassTranslator.translatePythonClass(python_compiled_class, prepared_class_info)
    PythonClassTranslator.setSelfStaticInstances(python_compiled_class, out.getJavaClass(), out,
                                                 CPythonBackedPythonInterpreter.pythonObjectIdToConvertedObjectMap)
    return out
