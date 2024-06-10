package ai.timefold.solver.python.score;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonJavaTypeMapping;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.types.numeric.PythonInteger;
import ai.timefold.solver.core.api.score.buildin.simple.SimpleScore;

public final class SimpleScorePythonJavaTypeMapping implements PythonJavaTypeMapping<PythonLikeObject, SimpleScore> {
    private final PythonLikeType type;
    private final Constructor<?> constructor;
    private final Field initScoreField;
    private final Field scoreField;

    public SimpleScorePythonJavaTypeMapping(PythonLikeType type)
            throws ClassNotFoundException, NoSuchFieldException, NoSuchMethodException {
        this.type = type;
        Class<?> clazz = type.getJavaClass();
        constructor = clazz.getConstructor();
        initScoreField = clazz.getField("init_score");
        scoreField = clazz.getField("score");
    }

    @Override
    public PythonLikeType getPythonType() {
        return type;
    }

    @Override
    public Class<? extends SimpleScore> getJavaType() {
        return SimpleScore.class;
    }

    @Override
    public PythonLikeObject toPythonObject(SimpleScore javaObject) {
        try {
            var instance = constructor.newInstance();
            initScoreField.set(instance, PythonInteger.valueOf(javaObject.initScore()));
            scoreField.set(instance, PythonInteger.valueOf(javaObject.score()));
            return (PythonLikeObject) instance;
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public SimpleScore toJavaObject(PythonLikeObject pythonObject) {
        try {
            var initScore = ((PythonInteger) initScoreField.get(pythonObject)).value.intValue();
            var score = ((PythonInteger) scoreField.get(pythonObject)).value.intValue();
            if (initScore == 0) {
                return SimpleScore.of(score);
            } else {
                return SimpleScore.ofUninitialized(initScore, score);
            }
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
}
