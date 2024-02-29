package ai.timefold.jpyinterpreter.opcodes.async;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public class AsyncOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            // TODO
            case GET_AWAITABLE:
            case GET_AITER:
            case GET_ANEXT:
            case END_ASYNC_FOR:
            case BEFORE_ASYNC_WITH:
            case SETUP_ASYNC_WITH:
            default: {
                return Optional.empty();
            }
        }
    }
}
