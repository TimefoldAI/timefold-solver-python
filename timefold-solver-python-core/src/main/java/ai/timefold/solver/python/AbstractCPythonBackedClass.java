package ai.timefold.solver.python;

import ai.timefold.jpyinterpreter.types.CPythonBackedPythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonLikeType;

public class AbstractCPythonBackedClass extends CPythonBackedPythonLikeObject {
    public static final PythonLikeType $TYPE = CPythonBackedPythonLikeObject.OBJECT_TYPE;

    public AbstractCPythonBackedClass() {
        super($TYPE);
    }

    public AbstractCPythonBackedClass(PythonLikeType __type__) {
        super(__type__);
    }
}
