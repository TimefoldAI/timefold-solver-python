package ai.timefold.solver.python.score;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonJavaTypeMapping;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.types.numeric.PythonInteger;
import ai.timefold.solver.core.api.score.buildin.hardsoft.HardSoftScore;

public final class HardSoftScorePythonJavaTypeMapping implements PythonJavaTypeMapping<PythonLikeObject, HardSoftScore> {
    private final PythonLikeType type;
    private final Constructor<?> constructor;
    private final Field initScoreField;
    private final Field hardScoreField;
    private final Field softScoreField;

    public HardSoftScorePythonJavaTypeMapping(PythonLikeType type)
            throws ClassNotFoundException, NoSuchFieldException, NoSuchMethodException {
        this.type = type;
        Class<?> clazz = type.getJavaClass();
        constructor = clazz.getConstructor();
        initScoreField = clazz.getField("init_score");
        hardScoreField = clazz.getField("hard_score");
        softScoreField = clazz.getField("soft_score");
    }

    @Override
    public PythonLikeType getPythonType() {
        return type;
    }

    @Override
    public Class<? extends HardSoftScore> getJavaType() {
        return HardSoftScore.class;
    }

    @Override
    public PythonLikeObject toPythonObject(HardSoftScore javaObject) {
        try {
            var instance = constructor.newInstance();
            initScoreField.set(instance, PythonInteger.valueOf(javaObject.initScore()));
            hardScoreField.set(instance, PythonInteger.valueOf(javaObject.hardScore()));
            softScoreField.set(instance, PythonInteger.valueOf(javaObject.softScore()));
            return (PythonLikeObject) instance;
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public HardSoftScore toJavaObject(PythonLikeObject pythonObject) {
        try {
            var initScore = ((PythonInteger) initScoreField.get(pythonObject)).value.intValue();
            var hardScore = ((PythonInteger) hardScoreField.get(pythonObject)).value.intValue();
            var softScore = ((PythonInteger) softScoreField.get(pythonObject)).value.intValue();
            if (initScore == 0) {
                return HardSoftScore.of(hardScore, softScore);
            } else {
                return HardSoftScore.ofUninitialized(initScore, hardScore, softScore);
            }
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
}
