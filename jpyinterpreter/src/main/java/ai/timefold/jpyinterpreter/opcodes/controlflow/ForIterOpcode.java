package ai.timefold.jpyinterpreter.opcodes.controlflow;

import java.util.List;

import ai.timefold.jpyinterpreter.FunctionMetadata;
import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.StackMetadata;
import ai.timefold.jpyinterpreter.ValueSourceInfo;
import ai.timefold.jpyinterpreter.implementors.CollectionImplementor;
import ai.timefold.jpyinterpreter.types.BuiltinTypes;

public class ForIterOpcode extends AbstractControlFlowOpcode {
    int jumpTarget;
    boolean popIterator;

    public ForIterOpcode(PythonBytecodeInstruction instruction, int jumpTarget, boolean popIterator) {
        super(instruction);
        this.jumpTarget = jumpTarget;
        this.popIterator = popIterator;
    }

    @Override
    public List<Integer> getPossibleNextBytecodeIndexList() {
        return List.of(
                getBytecodeIndex() + 1,
                jumpTarget);
    }

    @Override
    public List<StackMetadata> getStackMetadataAfterInstructionForBranches(FunctionMetadata functionMetadata,
            StackMetadata stackMetadata) {
        return List.of(stackMetadata.push(ValueSourceInfo.of(this, BuiltinTypes.BASE_TYPE,
                stackMetadata.getValueSourcesUpToStackIndex(1))),
                popIterator ? stackMetadata.pop() : stackMetadata);
    }

    @Override
    public void implement(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        CollectionImplementor.iterateIterator(functionMetadata.methodVisitor, jumpTarget,
                popIterator, stackMetadata, functionMetadata);
    }
}
