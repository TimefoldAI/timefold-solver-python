package ai.timefold.jpyinterpreter.opcodes.string;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public class StringOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            case PRINT_EXPR: {
                return Optional.of(new PrintExprOpcode(instruction));
            }

            case FORMAT_VALUE: {
                return Optional.of(new FormatValueOpcode(instruction));
            }

            case BUILD_STRING: {
                return Optional.of(new BuildStringOpcode(instruction));
            }

            default: {
                return Optional.empty();
            }
        }
    }
}
