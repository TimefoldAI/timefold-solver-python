package ai.timefold.solver.python.score;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.*;

import ai.timefold.jpyinterpreter.types.numeric.PythonInteger;
import ai.timefold.solver.core.api.score.buildin.simple.SimpleScore;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SimpleScorePythonJavaTypeMappingTest {
    SimpleScorePythonJavaTypeMapping typeMapping;

    @BeforeEach
    void setUp() throws NoSuchFieldException, ClassNotFoundException, NoSuchMethodException {
        this.typeMapping = new SimpleScorePythonJavaTypeMapping(PythonSimpleScore.TYPE);
    }

    @Test
    void getPythonType() {
        assertThat(typeMapping.getPythonType()).isEqualTo(PythonSimpleScore.TYPE);
    }

    @Test
    void getJavaType() {
        assertThat(typeMapping.getJavaType()).isEqualTo(SimpleScore.class);
    }

    @Test
    void toPythonObject() {
        var initializedScore = SimpleScore.of(10);

        var initializedPythonScore = (PythonSimpleScore) typeMapping.toPythonObject(initializedScore);

        assertThat(initializedPythonScore.init_score).isEqualTo(PythonInteger.ZERO);
        assertThat(initializedPythonScore.score).isEqualTo(PythonInteger.valueOf(10));

        var uninitializedScore = SimpleScore.ofUninitialized(-5, 20);
        var uninitializedPythonScore = (PythonSimpleScore) typeMapping.toPythonObject(uninitializedScore);

        assertThat(uninitializedPythonScore.init_score).isEqualTo(PythonInteger.valueOf(-5));
        assertThat(uninitializedPythonScore.score).isEqualTo(PythonInteger.valueOf(20));
    }

    @Test
    void toJavaObject() {
        var initializedScore = PythonSimpleScore.of(10);

        var initializedJavaScore = typeMapping.toJavaObject(initializedScore);

        assertThat(initializedJavaScore.initScore()).isEqualTo(0);
        assertThat(initializedJavaScore.score()).isEqualTo(10);

        var uninitializedScore = PythonSimpleScore.ofUninitialized(-5, 20);
        var uninitializedJavaScore = typeMapping.toJavaObject(uninitializedScore);

        assertThat(uninitializedJavaScore.initScore()).isEqualTo(-5);
        assertThat(uninitializedJavaScore.score()).isEqualTo(20);
    }
}