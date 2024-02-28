package ai.timefold.jpyinterpreter.opcodes.generator;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.util.JumpUtils;

public class GeneratorOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            case RESUME: {
                return Optional.of(new ResumeOpcode(instruction));
            }
            case SEND: {
                return Optional.of(new SendOpcode(instruction, JumpUtils.getRelativeTarget(instruction, pythonVersion)));
            }
            case YIELD_VALUE: {
                return Optional.of(new YieldValueOpcode(instruction));
            }
            case YIELD_FROM: {
                return Optional.of(new YieldFromOpcode(instruction));
            }
            case GET_YIELD_FROM_ITER: {
                return Optional.of(new GetYieldFromIterOpcode(instruction));
            }
            case GEN_START: {
                return Optional.of(new GeneratorStartOpcode(instruction));
            }
            default: {
                return Optional.empty();
            }
        }
    }
}
