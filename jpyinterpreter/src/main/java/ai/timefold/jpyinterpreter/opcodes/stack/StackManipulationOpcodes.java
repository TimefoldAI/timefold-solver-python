package ai.timefold.jpyinterpreter.opcodes.stack;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public class StackManipulationOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            case POP_TOP: {
                return Optional.of(new PopOpcode(instruction));
            }
            case ROT_TWO: {
                return Optional.of(new RotateTwoOpcode(instruction));
            }
            case ROT_THREE: {
                return Optional.of(new RotateThreeOpcode(instruction));
            }
            case ROT_FOUR: {
                return Optional.of(new RotateFourOpcode(instruction));
            }
            case COPY: {
                return Optional.of(new CopyOpcode(instruction));
            }
            case SWAP: {
                return Optional.of(new SwapOpcode(instruction));
            }
            case DUP_TOP: {
                return Optional.of(new DupOpcode(instruction));
            }
            case DUP_TOP_TWO: {
                return Optional.of(new DupTwoOpcode(instruction));
            }
            default: {
                return Optional.empty();
            }
        }
    }
}
