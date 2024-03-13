package ai.timefold.jpyinterpreter.util;

import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonVersion;

public final class JumpUtils {

    private JumpUtils() {
    }

    public static int getInstructionIndexForByteOffset(int byteOffset, PythonVersion pythonVersion) {
        return byteOffset >> 1;
    }

    public static int getAbsoluteTarget(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        if (pythonVersion.isBefore(PythonVersion.PYTHON_3_10)) {
            return instruction.arg() >> 1;
        } else {
            return instruction.arg();
        }
    }

    public static int getRelativeTarget(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        if (pythonVersion.isBefore(PythonVersion.PYTHON_3_10)) {
            return instruction.offset() + (instruction.arg() >> 1) + 1;
        } else {
            return instruction.offset() + instruction.arg() + 1;
        }
    }

    public static int getBackwardRelativeTarget(PythonBytecodeInstruction instruction, PythonVersion pythonVersion) {
        if (pythonVersion.isBefore(PythonVersion.PYTHON_3_10)) {
            return instruction.offset() - (instruction.arg() >> 1) + 1;
        } else {
            return instruction.offset() - instruction.arg() + 1;
        }
    }
}
