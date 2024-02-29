package ai.timefold.jpyinterpreter.opcodes.exceptions;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import ai.timefold.jpyinterpreter.FunctionMetadata;
import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.StackMetadata;
import ai.timefold.jpyinterpreter.implementors.ExceptionImplementor;
import ai.timefold.jpyinterpreter.opcodes.controlflow.AbstractControlFlowOpcode;
import ai.timefold.jpyinterpreter.types.BuiltinTypes;
import ai.timefold.jpyinterpreter.types.errors.PythonBaseException;
import ai.timefold.jpyinterpreter.types.errors.PythonTraceback;

public class SetupFinallyOpcode extends AbstractControlFlowOpcode {
    int jumpTarget;

    public SetupFinallyOpcode(PythonBytecodeInstruction instruction, int jumpTarget) {
        super(instruction);
        this.jumpTarget = jumpTarget;
    }

    @Override
    public List<Integer> getPossibleNextBytecodeIndexList() {
        return List.of(getBytecodeIndex() + 1,
                jumpTarget);
    }

    @Override
    public void relabel(Map<Integer, Integer> originalBytecodeIndexToNewBytecodeIndex) {
        jumpTarget = originalBytecodeIndexToNewBytecodeIndex.get(jumpTarget);
        super.relabel(originalBytecodeIndexToNewBytecodeIndex);
    }

    @Override
    public List<StackMetadata> getStackMetadataAfterInstructionForBranches(FunctionMetadata functionMetadata,
            StackMetadata stackMetadata) {
        return List.of(stackMetadata.copy(),
                stackMetadata.copy()
                        .pushTemp(BuiltinTypes.NONE_TYPE)
                        .pushTemp(BuiltinTypes.INT_TYPE)
                        .pushTemp(BuiltinTypes.NONE_TYPE)
                        .pushTemp(PythonTraceback.TRACEBACK_TYPE)
                        .pushTemp(PythonBaseException.BASE_EXCEPTION_TYPE)
                        .pushTemp(BuiltinTypes.TYPE_TYPE));
    }

    @Override
    public void implement(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        ExceptionImplementor.createTryFinallyBlock(functionMetadata.methodVisitor, functionMetadata.className,
                jumpTarget,
                stackMetadata,
                functionMetadata.bytecodeCounterToLabelMap,
                (bytecodeIndex, runnable) -> {
                    functionMetadata.bytecodeCounterToCodeArgumenterList
                            .computeIfAbsent(bytecodeIndex, key -> new ArrayList<>()).add(runnable);
                });
    }
}
