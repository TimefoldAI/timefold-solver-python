package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Map;
import java.util.NavigableMap;
import java.util.Optional;
import java.util.TreeMap;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.function.ToIntBiFunction;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.ForIterOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.JumpAbsoluteOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.JumpIfFalseOrPopOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.JumpIfNotExcMatchOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.JumpIfTrueOrPopOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.PopJumpIfFalseOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.PopJumpIfIsNoneOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.PopJumpIfIsNotNoneOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.PopJumpIfTrueOpcode;
import ai.timefold.jpyinterpreter.opcodes.controlflow.ReturnValueOpcode;
import ai.timefold.jpyinterpreter.util.JumpUtils;

public enum ControlOpDescriptor implements OpcodeDescriptor {
    /**
     * Returns with TOS to the caller of the function.
     */
    RETURN_VALUE(ReturnValueOpcode::new),
    JUMP_FORWARD(JumpAbsoluteOpcode::new, JumpUtils::getRelativeTarget),
    JUMP_BACKWARD(JumpAbsoluteOpcode::new, JumpUtils::getBackwardRelativeTarget),
    JUMP_BACKWARD_NO_INTERRUPT(JumpAbsoluteOpcode::new, JumpUtils::getBackwardRelativeTarget),
    POP_JUMP_IF_TRUE(PopJumpIfTrueOpcode::new, JumpUtils::getAbsoluteTarget),
    POP_JUMP_FORWARD_IF_TRUE(PopJumpIfTrueOpcode::new, JumpUtils::getRelativeTarget),
    POP_JUMP_BACKWARD_IF_TRUE(PopJumpIfTrueOpcode::new, JumpUtils::getBackwardRelativeTarget),
    POP_JUMP_IF_FALSE(PopJumpIfFalseOpcode::new, JumpUtils::getAbsoluteTarget),
    POP_JUMP_FORWARD_IF_FALSE(PopJumpIfFalseOpcode::new, JumpUtils::getRelativeTarget),
    POP_JUMP_BACKWARD_IF_FALSE(PopJumpIfFalseOpcode::new, JumpUtils::getBackwardRelativeTarget),
    POP_JUMP_FORWARD_IF_NONE(PopJumpIfIsNoneOpcode::new, JumpUtils::getRelativeTarget),
    POP_JUMP_BACKWARD_IF_NONE(PopJumpIfIsNoneOpcode::new, JumpUtils::getBackwardRelativeTarget),
    POP_JUMP_FORWARD_IF_NOT_NONE(PopJumpIfIsNotNoneOpcode::new, JumpUtils::getRelativeTarget),
    POP_JUMP_BACKWARD_IF_NOT_NONE(PopJumpIfIsNotNoneOpcode::new, JumpUtils::getBackwardRelativeTarget),
    JUMP_IF_NOT_EXC_MATCH(JumpIfNotExcMatchOpcode::new, JumpUtils::getAbsoluteTarget),
    JUMP_IF_TRUE_OR_POP(Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, JumpIfTrueOrPopOpcode::new),
            Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, JumpUtils::getAbsoluteTarget,
                    PythonVersion.PYTHON_3_11, JumpUtils::getRelativeTarget)),
    JUMP_IF_FALSE_OR_POP(Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, JumpIfFalseOrPopOpcode::new),
            Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, JumpUtils::getAbsoluteTarget,
                    PythonVersion.PYTHON_3_11, JumpUtils::getRelativeTarget)),
    JUMP_ABSOLUTE(JumpAbsoluteOpcode::new, JumpUtils::getAbsoluteTarget),
    FOR_ITER(ForIterOpcode::new, JumpUtils::getRelativeTarget);

    final NavigableMap<PythonVersion, BiFunction<PythonBytecodeInstruction, Integer, Opcode>> versionToOpcodeFunction;
    final NavigableMap<PythonVersion, ToIntBiFunction<PythonBytecodeInstruction, PythonVersion>> versionToLabelFunction;

    ControlOpDescriptor(Function<PythonBytecodeInstruction, Opcode> opcodeFunction) {
        this((instruction, ignoredLabel) -> opcodeFunction.apply(instruction), (ignored1, ignored2) -> 0);
    }

    ControlOpDescriptor(BiFunction<PythonBytecodeInstruction, Integer, Opcode> opcodeFunction,
            ToIntBiFunction<PythonBytecodeInstruction, PythonVersion> labelFunction) {
        this(Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, opcodeFunction),
                Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, labelFunction));
    }

    ControlOpDescriptor(Map<PythonVersion, BiFunction<PythonBytecodeInstruction, Integer, Opcode>> versionToOpcodeFunction,
            Map<PythonVersion, ToIntBiFunction<PythonBytecodeInstruction, PythonVersion>> versionToLabelFunction) {
        this.versionToOpcodeFunction = new TreeMap<>(versionToOpcodeFunction);
        this.versionToLabelFunction = new TreeMap<>(versionToLabelFunction);
    }

    @Override
    public Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        return Optional.of(versionToOpcodeFunction.floorEntry(pythonVersion)
                .getValue().apply(instruction, versionToLabelFunction.floorEntry(pythonVersion)
                        .getValue().applyAsInt(instruction, pythonVersion)));
    }
}
