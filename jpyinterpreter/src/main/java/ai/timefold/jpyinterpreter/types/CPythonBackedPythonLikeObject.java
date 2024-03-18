package ai.timefold.jpyinterpreter.types;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.numeric.PythonInteger;
import ai.timefold.jpyinterpreter.types.wrappers.OpaquePythonReference;
import ai.timefold.jpyinterpreter.util.ConcurrentWeakIdentityHashMap;

public class CPythonBackedPythonLikeObject extends AbstractPythonLikeObject implements PythonLikeFunction {
    public static final PythonLikeType CPYTHON_BACKED_OBJECT_TYPE =
            new PythonLikeType("object", CPythonBackedPythonLikeObject.class);

    private static final Set<CPythonBackedPythonLikeObject> $hasReferenceSet =
            Collections.newSetFromMap(new ConcurrentWeakIdentityHashMap<>());

    public OpaquePythonReference $cpythonReference;

    public PythonInteger $cpythonId;

    public Map<Number, PythonLikeObject> $instanceMap;

    public CPythonBackedPythonLikeObject(PythonLikeType __type__) {
        this(__type__, (OpaquePythonReference) null);
    }

    public CPythonBackedPythonLikeObject(PythonLikeType __type__, Map<String, PythonLikeObject> __dir__) {
        this(__type__, __dir__, null);
    }

    public CPythonBackedPythonLikeObject(PythonLikeType __type__,
            OpaquePythonReference reference) {
        super(__type__);
        this.$cpythonReference = reference;
        $instanceMap = new HashMap<>();
    }

    public CPythonBackedPythonLikeObject(PythonLikeType __type__,
            Map<String, PythonLikeObject> __dir__,
            OpaquePythonReference reference) {
        super(__type__, __dir__);
        this.$cpythonReference = reference;
        $instanceMap = new HashMap<>();
    }

    public OpaquePythonReference $getCPythonReference() {
        return $cpythonReference;
    }

    public void $setCPythonReference(OpaquePythonReference pythonReference) {
        this.$cpythonReference = pythonReference;
    }

    public PythonInteger $getCPythonId() {
        return $cpythonId;
    }

    public void $setCPythonId(PythonInteger $cpythonId) {
        this.$cpythonId = $cpythonId;
    }

    public Map<Number, PythonLikeObject> $getInstanceMap() {
        return $instanceMap;
    }

    public void $setInstanceMap(Map<Number, PythonLikeObject> $instanceMap) {
        this.$instanceMap = $instanceMap;
    }

    public void $markValidPythonReference() {
        $hasReferenceSet.add(this);
    }

    public boolean $shouldCreateNewInstance() {
        return $cpythonReference == null || $hasReferenceSet.add(this);
    }

    public void $readFieldsFromCPythonReference() {
    }

    public void $writeFieldsToCPythonReference(OpaquePythonReference cloneMap) {
    }

    @Override
    public PythonLikeObject $call(List<PythonLikeObject> positionalArguments,
            Map<PythonString, PythonLikeObject> namedArguments, PythonLikeObject callerInstance) {
        return PythonNone.INSTANCE;
    }
}
