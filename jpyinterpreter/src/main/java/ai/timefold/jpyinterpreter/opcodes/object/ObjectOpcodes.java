package ai.timefold.jpyinterpreter.opcodes.object;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public class ObjectOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            case IS_OP: {
                return Optional.of(new IsOpcode(instruction));
            }
            case LOAD_ATTR: {
                return Optional.of(new LoadAttrOpcode(instruction));
            }
            case STORE_ATTR: {
                return Optional.of(new StoreAttrOpcode(instruction));
            }
            case DELETE_ATTR: {
                return Optional.of(new DeleteAttrOpcode(instruction));
            }
            default: {
                return Optional.empty();
            }
        }
    }
}
