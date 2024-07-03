package ai.timefold.solver.python.score.constraint;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonJavaTypeMapping;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.types.PythonString;
import ai.timefold.solver.core.api.score.constraint.ConstraintRef;

public final class ConstraintRefPythonJavaTypeMapping implements PythonJavaTypeMapping<PythonLikeObject, ConstraintRef> {
    private final PythonLikeType type;
    private final Constructor<?> constructor;
    private final Field packageNameField;
    private final Field constraintNameField;

    public ConstraintRefPythonJavaTypeMapping(PythonLikeType type)
            throws ClassNotFoundException, NoSuchFieldException, NoSuchMethodException {
        this.type = type;
        Class<?> clazz = type.getJavaClass();
        constructor = clazz.getConstructor();
        packageNameField = clazz.getField("package_name");
        constraintNameField = clazz.getField("constraint_name");
    }

    @Override
    public PythonLikeType getPythonType() {
        return type;
    }

    @Override
    public Class<? extends ConstraintRef> getJavaType() {
        return ConstraintRef.class;
    }

    @Override
    public PythonLikeObject toPythonObject(ConstraintRef javaObject) {
        try {
            var instance = constructor.newInstance();
            packageNameField.set(instance, PythonString.valueOf(javaObject.packageName()));
            constraintNameField.set(instance, PythonString.valueOf(javaObject.constraintName()));
            return (PythonLikeObject) instance;
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public ConstraintRef toJavaObject(PythonLikeObject pythonObject) {
        try {
            var packageName = ((PythonString) packageNameField.get(pythonObject)).value.toString();
            var constraintName = ((PythonString) constraintNameField.get(pythonObject)).value.toString();
            return ConstraintRef.of(packageName, constraintName);
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
}
