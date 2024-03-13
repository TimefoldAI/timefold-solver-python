package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Optional;
import java.util.function.Function;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.opcodes.object.DeleteAttrOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.IsOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.LoadAttrOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.StoreAttrOpcode;

public enum ObjectOpDescriptor implements OpcodeDescriptor {
    IS_OP(IsOpcode::new),
    LOAD_ATTR(LoadAttrOpcode::new),
    STORE_ATTR(StoreAttrOpcode::new),
    DELETE_ATTR(DeleteAttrOpcode::new);

    final Function<PythonBytecodeInstruction, Opcode> opcodeFunction;

    ObjectOpDescriptor(Function<PythonBytecodeInstruction, Opcode> opcodeFunction) {
        this.opcodeFunction = opcodeFunction;
    }

    @Override
    public Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        return Optional.of(opcodeFunction.apply(instruction));
    }
}
