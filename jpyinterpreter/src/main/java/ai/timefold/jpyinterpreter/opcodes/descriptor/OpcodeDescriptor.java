package ai.timefold.jpyinterpreter.opcodes.descriptor;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public sealed interface OpcodeDescriptor permits AsyncOpDescriptor,
        CollectionOpDescriptor,
        ControlOpDescriptor,
        DunderOpDescriptor,
        ExceptionOpDescriptor,
        FunctionOpDescriptor,
        GeneratorOpDescriptor,
        MetaOpDescriptor,
        ModuleOpDescriptor,
        ObjectOpDescriptor,
        StackOpDescriptor,
        StringOpDescriptor,
        VariableOpDescriptor {
    String name();

    Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion);
}
