package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Map;
import java.util.NavigableMap;
import java.util.Optional;
import java.util.TreeMap;
import java.util.function.Function;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;
import ai.timefold.jpyinterpreter.opcodes.function.LoadMethodOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.DeleteAttrOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.IsOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.LoadAttrOpcode;
import ai.timefold.jpyinterpreter.opcodes.object.StoreAttrOpcode;

public enum ObjectOpDescriptor implements OpcodeDescriptor {
    IS_OP(IsOpcode::new),
    LOAD_ATTR(Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, LoadAttrOpcode::new,
            PythonVersion.PYTHON_3_12,
            instruction -> ((instruction.arg() & 1) == 1) ? new LoadMethodOpcode(instruction.withArg(instruction.arg() >> 1))
                    : new LoadAttrOpcode(instruction.withArg(instruction.arg() >> 1)))),
    STORE_ATTR(StoreAttrOpcode::new),
    DELETE_ATTR(DeleteAttrOpcode::new);

    final NavigableMap<PythonVersion, Function<PythonBytecodeInstruction, Opcode>> opcodeFunctionMap;

    ObjectOpDescriptor(Function<PythonBytecodeInstruction, Opcode> opcodeFunction) {
        this(Map.of(PythonVersion.MINIMUM_PYTHON_VERSION, opcodeFunction));
    }

    ObjectOpDescriptor(Map<PythonVersion, Function<PythonBytecodeInstruction, Opcode>> opcodeFunctionMap) {
        this.opcodeFunctionMap = new TreeMap<>(opcodeFunctionMap);
    }

    @Override
    public Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        return Optional.of(opcodeFunctionMap.floorEntry(pythonVersion).getValue().apply(instruction));
    }
}
