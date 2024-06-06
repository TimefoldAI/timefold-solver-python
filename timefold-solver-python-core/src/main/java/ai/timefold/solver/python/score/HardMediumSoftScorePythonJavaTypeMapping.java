package ai.timefold.solver.python.score;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonJavaTypeMapping;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.types.numeric.PythonInteger;
import ai.timefold.solver.core.api.score.buildin.hardmediumsoft.HardMediumSoftScore;

public final class HardMediumSoftScorePythonJavaTypeMapping
        implements PythonJavaTypeMapping<PythonLikeObject, HardMediumSoftScore> {
    private final PythonLikeType type;
    private final Constructor<?> constructor;
    private final Field initScoreField;
    private final Field hardScoreField;
    private final Field mediumScoreField;
    private final Field softScoreField;

    public HardMediumSoftScorePythonJavaTypeMapping(PythonLikeType type)
            throws ClassNotFoundException, NoSuchFieldException, NoSuchMethodException {
        this.type = type;
        Class<?> clazz = type.getJavaClass();
        constructor = clazz.getConstructor();
        initScoreField = clazz.getField("init_score");
        hardScoreField = clazz.getField("hard_score");
        mediumScoreField = clazz.getField("medium_score");
        softScoreField = clazz.getField("soft_score");
    }

    @Override
    public PythonLikeType getPythonType() {
        return type;
    }

    @Override
    public Class<? extends HardMediumSoftScore> getJavaType() {
        return HardMediumSoftScore.class;
    }

    @Override
    public PythonLikeObject toPythonObject(HardMediumSoftScore javaObject) {
        try {
            var instance = constructor.newInstance();
            initScoreField.set(instance, PythonInteger.valueOf(javaObject.initScore()));
            hardScoreField.set(instance, PythonInteger.valueOf(javaObject.hardScore()));
            mediumScoreField.set(instance, PythonInteger.valueOf(javaObject.mediumScore()));
            softScoreField.set(instance, PythonInteger.valueOf(javaObject.softScore()));
            return (PythonLikeObject) instance;
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public HardMediumSoftScore toJavaObject(PythonLikeObject pythonObject) {
        try {
            var initScore = ((PythonInteger) initScoreField.get(pythonObject)).value.intValue();
            var hardScore = ((PythonInteger) hardScoreField.get(pythonObject)).value.intValue();
            var mediumScore = ((PythonInteger) mediumScoreField.get(pythonObject)).value.intValue();
            var softScore = ((PythonInteger) softScoreField.get(pythonObject)).value.intValue();
            if (initScore == 0) {
                return HardMediumSoftScore.of(hardScore, mediumScore, softScore);
            } else {
                return HardMediumSoftScore.ofUninitialized(initScore, hardScore, mediumScore, softScore);
            }
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
}
