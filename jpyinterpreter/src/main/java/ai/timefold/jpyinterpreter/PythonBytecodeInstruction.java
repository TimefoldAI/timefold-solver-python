package ai.timefold.jpyinterpreter;

import java.util.Optional;

import ai.timefold.jpyinterpreter.opcodes.descriptor.OpcodeDescriptor;

public record PythonBytecodeInstruction(String opname, int offset, int arg, Optional<Integer> startsLine,
        boolean isJumpTarget) {
    public static PythonBytecodeInstruction atOffset(OpcodeDescriptor instruction, int offset) {
        return new PythonBytecodeInstruction(instruction.name(), offset, 0, Optional.empty(), false);
    }

    public PythonBytecodeInstruction withArg(int newArg) {
        return new PythonBytecodeInstruction(opname, offset, newArg, startsLine, isJumpTarget);
    }

    public PythonBytecodeInstruction withOffset(int newOffset) {
        return new PythonBytecodeInstruction(opname, newOffset, arg, startsLine, isJumpTarget);
    }

    public PythonBytecodeInstruction markAsJumpTarget() {
        return new PythonBytecodeInstruction(opname, offset, arg, startsLine, true);
    }

    @Override
    public String toString() {
        return "[%d] %s (%d) %s"
                .formatted(offset, opname, arg, isJumpTarget ? "{JUMP TARGET}" : "");
    }
}
