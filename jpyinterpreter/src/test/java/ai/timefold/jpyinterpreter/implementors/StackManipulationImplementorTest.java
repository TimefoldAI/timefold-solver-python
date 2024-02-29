package ai.timefold.jpyinterpreter.implementors;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.function.Supplier;

import ai.timefold.jpyinterpreter.OpcodeIdentifier;
import ai.timefold.jpyinterpreter.PythonBytecodeToJavaBytecodeTranslator;
import ai.timefold.jpyinterpreter.PythonCompiledFunction;
import ai.timefold.jpyinterpreter.util.PythonFunctionBuilder;

import org.junit.jupiter.api.Test;

public class StackManipulationImplementorTest {
    @Test
    public void testRot2() {
        PythonCompiledFunction pythonCompiledFunction = PythonFunctionBuilder.newFunction()
                .loadConstant(1)
                .loadConstant(2)
                .op(OpcodeIdentifier.ROT_TWO)
                .tuple(2)
                .op(OpcodeIdentifier.RETURN_VALUE)
                .build();

        Supplier<?> javaFunction =
                PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(pythonCompiledFunction, Supplier.class);

        assertThat(javaFunction.get()).isEqualTo(List.of(2, 1));
    }

    @Test
    public void testRot3() {
        PythonCompiledFunction pythonCompiledFunction = PythonFunctionBuilder.newFunction()
                .loadConstant(1)
                .loadConstant(2)
                .loadConstant(3)
                .op(OpcodeIdentifier.ROT_THREE)
                .tuple(3)
                .op(OpcodeIdentifier.RETURN_VALUE)
                .build();

        Supplier<?> javaFunction =
                PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(pythonCompiledFunction, Supplier.class);

        assertThat(javaFunction.get()).isEqualTo(List.of(3, 1, 2));
    }

    @Test
    public void testRot4() {
        PythonCompiledFunction pythonCompiledFunction = PythonFunctionBuilder.newFunction()
                .loadConstant(1)
                .loadConstant(2)
                .loadConstant(3)
                .loadConstant(4)
                .op(OpcodeIdentifier.ROT_FOUR)
                .tuple(4)
                .op(OpcodeIdentifier.RETURN_VALUE)
                .build();

        Supplier<?> javaFunction =
                PythonBytecodeToJavaBytecodeTranslator.translatePythonBytecode(pythonCompiledFunction, Supplier.class);

        assertThat(javaFunction.get()).isEqualTo(List.of(4, 1, 2, 3));
    }
}
