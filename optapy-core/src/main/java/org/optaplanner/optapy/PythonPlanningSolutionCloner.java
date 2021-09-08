package org.optaplanner.optapy;

import org.optaplanner.core.api.domain.solution.cloner.SolutionCloner;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

public class PythonPlanningSolutionCloner implements SolutionCloner {
    // A function in python that deep clones a given OpaquePythonReference
    private static Function<PythonObject, OpaquePythonReference> deepClonePythonObject;

    public static void setDeepClonePythonObject(Function<PythonObject, OpaquePythonReference> cloner) {
        deepClonePythonObject = cloner;
    }

    @Override
    public Object cloneSolution(Object o) {
        // Deep clone the OpaquePythonReference
        OpaquePythonReference deepClone = deepClonePythonObject.apply((PythonObject) o);

        // Wrap the deep cloned OpaquePythonReference into a new PythonObject
        return PythonWrapperGenerator.wrap(o.getClass(), deepClone, new HashMap<>());
    }
}