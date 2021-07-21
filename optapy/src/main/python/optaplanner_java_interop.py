import os
import tempfile
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from . import jars
import jpype
import jpype.imports
from jpype.types import *
from jpype import JImplements, JOverride, JImplementationFor
import ctypes
import copy

optaplanner_jars = tempfile.TemporaryDirectory()
classpath_list = text = pkg_resources.read_text('optapy', 'classpath.txt').splitlines()
classpath = []
my_refs = set()
for jar in classpath_list:
    new_classpath_item = os.path.join(optaplanner_jars.name, jar)
    jar_file = pkg_resources.read_binary(jars, jar)
    with open(new_classpath_item, 'wb') as temp_file:
        temp_file.write(jar_file)
    classpath.append(new_classpath_item)

jpype.startJVM(classpath=classpath)
from org.optaplanner.optapy import PythonWrapperGenerator, PythonPlanningSolutionCloner, PythonSolver, PythonObject
from org.optaplanner.core.config.solver import SolverConfig

import java.lang.Object
import java.util.function.Function
import java.util.function.BiFunction
import java.util.Map
import java.util.HashMap
import java.util.ArrayList
import org.optaplanner.core.api.score.Score
import org.optaplanner.core.api.function.TriFunction

optapy_cache = dict()

@JImplements('org.optaplanner.optapy.PythonObject')
class PythonObjectRef:
    def __init__(self, ref, item):
        self.__dict__['__optapy_ref'] = ref.get__optapy_Id()
        self.__dict__['__optapy_map'] = ref.get__optapy_ObjectMap()
        self.__dict__['__optapy_item'] = item
        optapy_cache[id(item)] = self

    def __getattr__(self, name):
        item = self.__dict__['__optapy_item']
        out = getattr(item, name)
        if id(out) in optapy_cache:
            return optapy_cache[id(out)]
        pointer = PythonWrapperGenerator.getPythonObject(self, str(id(out)))
        if pointer is not None:
            return PythonObjectRef(pointer, out)
        else:
            return out

    def __setattr__(self, key, value):
        item = ctypes.cast(int(str(PythonWrapperGenerator.getPythonObjectId(self))), ctypes.py_object).value
        setattr(item, key, value)

    @JOverride
    def get__optapy_Id(self):
        return self.__dict__['__optapy_ref']

    @JOverride
    def get__optapy_ObjectMap(self):
        return self.__dict__['__optapy_map']

@JImplementationFor('org.optaplanner.optapy.PythonObject')
class _PythonObject:
    def __jclass_init__(self):
        pass

    def __getattr__(self, name):
        item = ctypes.cast(int(str(PythonWrapperGenerator.getPythonObjectId(self))), ctypes.py_object).value
        out = getattr(item, name)
        if id(out) in optapy_cache:
            return optapy_cache[id(out)]
        pointer = PythonWrapperGenerator.getPythonObject(self, str(id(out)))
        if pointer is not None:
            return PythonObjectRef(pointer, out)
        else:
            return out

    def __setattr__(self, key, value):
        item = ctypes.cast(int(str(PythonWrapperGenerator.getPythonObjectId(self))), ctypes.py_object).value
        setattr(item, key, value)

    def __copy__(self):
        item = ctypes.cast(int(str(PythonWrapperGenerator.getPythonObjectId(self))), ctypes.py_object).value
        copied_item = copy.copy(item)
        my_refs.add(copied_item)
        return copied_item

    def __deepcopy__(self, memodict={}):
        item = ctypes.cast(int(str(PythonWrapperGenerator.getPythonObjectId(self))), ctypes.py_object).value
        copied_item = copy.copy(item)
        my_refs.add(copied_item)
        for attribute, value in vars(copied_item).items():
            if isinstance(value, _PythonObject):
                vars(copied_item)[attribute] = value.__deepcopy__(self, memodict)
        return copied_item

def getPythonObjectFromId(item_id):
    out = ctypes.cast(int(str(item_id)), ctypes.py_object)
    return out.value

@JImplements(java.util.function.Function)
class PythonFunction:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def apply(self, argument):
        return self.delegate(argument)

@JImplements(java.util.function.BiFunction)
class PythonBiFunction:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def apply(self, argument1, argument2):
        return self.delegate(argument1, argument2)

@JImplements(org.optaplanner.core.api.function.TriFunction)
class PythonTriFunction:
    def __init__(self, delegate):
        self.delegate = delegate

    @JOverride
    def apply(self, argument1, argument2, argument3):
        return self.delegate(argument1, argument2, argument3)

def __getPythonObjectAttribute(objectId, name):
    the_object = ctypes.cast(int(str(objectId)), ctypes.py_object).value
    pythonObjectGetter = getattr(the_object, str(name))
    pythonObject = pythonObjectGetter()
    if pythonObject is None:
        return None
    elif isinstance(pythonObject, (str, int, float, complex, org.optaplanner.core.api.score.Score)):
        out = JObject(pythonObject, java.lang.Object)
        return out
    else:
        return str(id(pythonObject))

def getPythonArrayIdToIdArray(arrayId):
    the_object = ctypes.cast(int(str(arrayId)), ctypes.py_object).value
    out = toList(list(map(lambda x: JObject(str(id(x)), java.lang.Object), the_object)))
    return out

def setPythonObjectAttribute(objectId, name, value):
    the_object = ctypes.cast(int(str(objectId)), ctypes.py_object).value
    getattr(the_object, str(name))(value)

def deepClonePythonObject(the_object):
    the_clone = the_object.__deepcopy__()
    return str(id(the_clone))

PythonWrapperGenerator.setPythonArrayIdToIdArray(JObject(PythonFunction(getPythonArrayIdToIdArray), java.util.function.Function))
PythonWrapperGenerator.setPythonObjectIdAndAttributeNameToValue(JObject(PythonBiFunction(__getPythonObjectAttribute), java.util.function.BiFunction))
PythonWrapperGenerator.setPythonObjectIdAndAttributeSetter(JObject(PythonTriFunction(setPythonObjectAttribute), org.optaplanner.core.api.function.TriFunction))
PythonPlanningSolutionCloner.setDeepClonePythonObject(JObject(PythonFunction(deepClonePythonObject), java.util.function.Function))

import java.lang.Exception
def solve(solverConfig, problem):
    return unwrap(PythonSolver.solve(solverConfig, str(id(problem))))

def unwrap(javaObject):
    if not isinstance(javaObject, (_PythonObject, PythonObject, PythonObjectRef)):
        pythonObject = javaObject
    else:
        pythonObject = ctypes.cast(int(str(javaObject.get__optapy_Id())), ctypes.py_object).value
    if not hasattr(pythonObject, '__dict__'):
        return pythonObject
    for attribute, value in vars(pythonObject).items():
        if isinstance(value, dict):
            setattr(pythonObject, attribute, {k: unwrap(v) for k, v in value.items()})
        elif isinstance(value, list):
            setattr(pythonObject, attribute, list(map(unwrap, value)))
        else:
            setattr(pythonObject, attribute, unwrap(value))
    return pythonObject


def toMap(pythonDict):
    out = java.util.HashMap()
    for key, value in pythonDict.items():
        if isinstance(value, list):
            out.put(JObject(key, java.lang.Object), toList(value).toArray())
        else:
            out.put(JObject(key, java.lang.Object), JObject(value, java.lang.Object))
    return out


def toList(pythonList):
    out = java.util.ArrayList()
    for item in pythonList:
        if isinstance(item, dict):
            out.add(toMap(item))
        else:
            out.add(JObject(item, java.lang.Object))
    return out

def getOptaPlannerAnnotations(pythonClass):
    method_list = [attribute for attribute in dir(pythonClass) if callable(getattr(pythonClass, attribute)) and attribute.startswith('__') is False]
    annotated_methods = []
    for method in method_list:
        optaplanner_annotations = [attribute for attribute in dir(getattr(pythonClass, method)) if attribute.startswith('__optaplanner')]
        if optaplanner_annotations:
            returnType = getattr(getattr(pythonClass, method), "__return", None)
            annotated_methods.append(
                toList([method, returnType,
                        toList(list(map(lambda annotation: getattr(getattr(pythonClass, method), annotation), optaplanner_annotations)))
                                       ]))
    return toList(annotated_methods)

def wrap(javaClass, pythonObject):
    return PythonWrapperGenerator.wrap(javaClass, str(id(pythonObject)))

def getClass(pythonClass):
    return pythonClass.__javaClass

def generateProblemFactClass(pythonClass):
    optaplannerAnnotations = getOptaPlannerAnnotations(pythonClass)
    out = PythonWrapperGenerator.defineProblemFactClass(pythonClass.__name__, optaplannerAnnotations)
    return out

def generatePlanningEntityClass(pythonClass):
    optaplannerAnnotations = getOptaPlannerAnnotations(pythonClass)
    out = PythonWrapperGenerator.definePlanningEntityClass(pythonClass.__name__, optaplannerAnnotations)
    return out

def generatePlanningSolutionClass(pythonClass):
    optaplannerAnnotations = getOptaPlannerAnnotations(pythonClass)
    out = PythonWrapperGenerator.definePlanningSolutionClass(pythonClass.__name__, optaplannerAnnotations)
    return out

import org.optaplanner.core.api.score.stream.Constraint as Constraint
def _toConstraintArray(pythonList):
    out = jpype.JArray(Constraint)(len(pythonList))
    for i in range(len(pythonList)):
        out[i] = pythonList[i]
    return out

def generateConstraintProviderClass(constraintProvider):
    out = PythonWrapperGenerator.defineConstraintProviderClass(constraintProvider.__name__, JObject(PythonFunction(lambda cf: _toConstraintArray(constraintProvider(cf))), java.util.function.Function))
    return out