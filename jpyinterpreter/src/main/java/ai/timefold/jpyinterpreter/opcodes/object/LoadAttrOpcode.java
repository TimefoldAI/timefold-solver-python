package ai.timefold.jpyinterpreter.opcodes.object;

import ai.timefold.jpyinterpreter.FunctionMetadata;
import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.StackMetadata;
import ai.timefold.jpyinterpreter.ValueSourceInfo;
import ai.timefold.jpyinterpreter.implementors.ObjectImplementor;
import ai.timefold.jpyinterpreter.opcodes.AbstractOpcode;
import ai.timefold.jpyinterpreter.types.BuiltinTypes;
import ai.timefold.jpyinterpreter.types.PythonLikeType;

public class LoadAttrOpcode extends AbstractOpcode {

    public LoadAttrOpcode(PythonBytecodeInstruction instruction) {
        super(instruction);
    }

    @Override
    protected StackMetadata getStackMetadataAfterInstruction(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        PythonLikeType tosType = stackMetadata.getTOSType();
        return tosType.getInstanceFieldDescriptor(functionMetadata.pythonCompiledFunction.co_names.get(instruction.arg))
                .map(fieldDescriptor -> stackMetadata.pop()
                        .push(ValueSourceInfo.of(this, fieldDescriptor.getFieldPythonLikeType(),
                                stackMetadata.getValueSourcesUpToStackIndex(1))))
                .orElseGet(() -> stackMetadata.pop().push(ValueSourceInfo.of(this, BuiltinTypes.BASE_TYPE,
                        stackMetadata.getValueSourcesUpToStackIndex(1))));
    }

    @Override
    public void implement(FunctionMetadata functionMetadata, StackMetadata stackMetadata) {
        ObjectImplementor.getAttribute(functionMetadata, functionMetadata.methodVisitor, functionMetadata.className,
                stackMetadata,
                instruction);
    }
}