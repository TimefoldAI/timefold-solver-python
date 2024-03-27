package ai.timefold.jpyinterpreter;

import java.util.OptionalInt;

import ai.timefold.jpyinterpreter.opcodes.descriptor.OpcodeDescriptor;

public record PythonBytecodeInstruction(String opname, int offset, int arg,
        String argRepr, OptionalInt startsLine,
        OptionalInt resolvedJumpTarget, boolean isJumpTarget) {
    public static PythonBytecodeInstruction atOffset(String opname, int offset) {
        return new PythonBytecodeInstruction(opname, offset, 0, "", java.util.OptionalInt.empty(),
                java.util.OptionalInt.empty(), false);
    }

    public static PythonBytecodeInstruction atOffset(OpcodeDescriptor instruction, int offset) {
        return atOffset(instruction.name(), offset);
    }

    public PythonBytecodeInstruction withArg(int newArg) {
        return new PythonBytecodeInstruction(opname, offset, newArg, argRepr, startsLine, resolvedJumpTarget, isJumpTarget);
    }

    public PythonBytecodeInstruction withArgRepr(String newArgRepr) {
        return new PythonBytecodeInstruction(opname, offset, arg, newArgRepr, startsLine, resolvedJumpTarget, isJumpTarget);
    }

    public PythonBytecodeInstruction withResolvedJumpTarget(int jumpTarget) {
        return new PythonBytecodeInstruction(opname, offset, arg, argRepr, startsLine, OptionalInt.of(jumpTarget),
                isJumpTarget);
    }

    public PythonBytecodeInstruction startsLine(int lineNumber) {
        return new PythonBytecodeInstruction(opname, offset, arg, argRepr, OptionalInt.of(lineNumber), resolvedJumpTarget,
                isJumpTarget);
    }

    public PythonBytecodeInstruction withIsJumpTarget(boolean isJumpTarget) {
        return new PythonBytecodeInstruction(opname, offset, arg, argRepr, startsLine, resolvedJumpTarget, isJumpTarget);
    }

    public PythonBytecodeInstruction markAsJumpTarget() {
        return new PythonBytecodeInstruction(opname, offset, arg, argRepr, startsLine, resolvedJumpTarget, true);
    }

    @Override
    public String toString() {
        return "[%d] %s (%d) %s"
                .formatted(offset, opname, arg, isJumpTarget ? "{JUMP TARGET}" : "");
    }
}
