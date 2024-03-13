package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Optional;
import java.util.function.Function;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.opcodes.string.BuildStringOpcode;
import ai.timefold.jpyinterpreter.opcodes.string.FormatValueOpcode;
import ai.timefold.jpyinterpreter.opcodes.string.PrintExprOpcode;

public enum StringOpDescriptor implements OpcodeDescriptor {
    /**
     * Implements the expression statement for the interactive mode. TOS is removed from the stack and printed.
     * In non-interactive mode, an expression statement is terminated with POP_TOP.
     */
    PRINT_EXPR(PrintExprOpcode::new),
    FORMAT_VALUE(FormatValueOpcode::new),
    BUILD_STRING(BuildStringOpcode::new);

    final Function<PythonBytecodeInstruction, Opcode> opcodeFunction;

    StringOpDescriptor(Function<PythonBytecodeInstruction, Opcode> opcodeFunction) {
        this.opcodeFunction = opcodeFunction;
    }

    @Override
    public Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        return Optional.of(opcodeFunction.apply(instruction));
    }
}
