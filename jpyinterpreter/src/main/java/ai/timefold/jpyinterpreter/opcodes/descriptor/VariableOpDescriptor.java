package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Optional;
import java.util.function.Function;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.opcodes.variable.DeleteDerefOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.DeleteFastOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.DeleteGlobalOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.LoadClosureOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.LoadConstantOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.LoadDerefOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.LoadFastOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.LoadGlobalOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.StoreDerefOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.StoreFastOpcode;
import ai.timefold.jpyinterpreter.opcodes.variable.StoreGlobalOpcode;

public enum VariableOpDescriptor implements OpcodeDescriptor {
    LOAD_CONST(LoadConstantOpcode::new),

    LOAD_NAME(null), //TODO
    STORE_NAME(null), //TODO
    DELETE_NAME(null), //TODO
    LOAD_GLOBAL(LoadGlobalOpcode::new),
    STORE_GLOBAL(StoreGlobalOpcode::new),
    DELETE_GLOBAL(DeleteGlobalOpcode::new),
    LOAD_FAST(LoadFastOpcode::new),
    STORE_FAST(StoreFastOpcode::new),
    DELETE_FAST(DeleteFastOpcode::new),
    LOAD_CLOSURE(LoadClosureOpcode::new),
    LOAD_DEREF(LoadDerefOpcode::new),
    STORE_DEREF(StoreDerefOpcode::new),
    DELETE_DEREF(DeleteDerefOpcode::new),
    LOAD_CLASSDEREF(null);

    final Function<PythonBytecodeInstruction, Opcode> opcodeFunction;

    VariableOpDescriptor(Function<PythonBytecodeInstruction, Opcode> opcodeFunction) {
        this.opcodeFunction = opcodeFunction;
    }

    @Override
    public Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        if (opcodeFunction == null) {
            return Optional.empty();
        }
        return Optional.of(opcodeFunction.apply(instruction));
    }
}