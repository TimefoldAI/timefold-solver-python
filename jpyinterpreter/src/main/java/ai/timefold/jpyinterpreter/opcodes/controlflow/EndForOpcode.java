package ai.timefold.jpyinterpreter.opcodes.controlflow;

import ai.timefold.jpyinterpreter.FunctionMetadata;
import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.StackMetadata;
import ai.timefold.jpyinterpreter.implementors.StackManipulationImplementor;
import ai.timefold.jpyinterpreter.opcodes.AbstractOpcode;

public class EndForOpcode extends AbstractOpcode {
    public EndForOpcode(PythonBytecodeInstruction instruction) {
        super(instruction);
    }

    @Override
    protected StackMetadata getStackMetadataAfterInstruction(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        // Python needs to pop 2, we only need to pop one
        return stackMetadata.pop();
    }

    @Override
    public void implement(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        StackManipulationImplementor.popTOS(functionMetadata.methodVisitor);
    }
}
