package ai.timefold.jpyinterpreter.opcodes.dunder;

import java.util.Optional;

import ai.timefold.jpyinterpreter.PythonBinaryOperator;
import ai.timefold.jpyinterpreter.PythonBytecodeInstruction;
import ai.timefold.jpyinterpreter.PythonUnaryOperator;
import ai.timefold.jpyinterpreter.PythonVersion;
import ai.timefold.jpyinterpreter.opcodes.Opcode;

public class DunderOpcodes {
    public static Optional<Opcode> lookupOpcodeForInstruction(PythonBytecodeInstruction instruction,
            PythonVersion pythonVersion) {
        switch (instruction.opcode) {
            case COMPARE_OP: {
                return Optional.of(new CompareOpcode(instruction));
            }
            case UNARY_NOT: {
                return Optional.of(new NotOpcode(instruction));
            }

            case UNARY_POSITIVE: {
                return Optional.of(new UniDunerOpcode(instruction, PythonUnaryOperator.POSITIVE));
            }
            case UNARY_NEGATIVE: {
                return Optional.of(new UniDunerOpcode(instruction, PythonUnaryOperator.NEGATIVE));
            }
            case UNARY_INVERT: {
                return Optional.of(new UniDunerOpcode(instruction, PythonUnaryOperator.INVERT));
            }

            case BINARY_OP: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.lookup(instruction.arg)));
            }
            case BINARY_POWER: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.POWER));
            }
            case BINARY_MULTIPLY: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.MULTIPLY));
            }
            case BINARY_MATRIX_MULTIPLY: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.MATRIX_MULTIPLY));
            }
            case BINARY_FLOOR_DIVIDE: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.FLOOR_DIVIDE));
            }
            case BINARY_TRUE_DIVIDE: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.TRUE_DIVIDE));
            }
            case BINARY_MODULO: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.MODULO));
            }
            case BINARY_ADD: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.ADD));
            }
            case BINARY_SUBTRACT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.SUBTRACT));
            }
            case BINARY_SUBSCR: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.GET_ITEM));
            }
            case BINARY_LSHIFT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.LSHIFT));
            }
            case BINARY_RSHIFT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.RSHIFT));
            }
            case BINARY_AND: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.AND));
            }
            case BINARY_XOR: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.XOR));
            }
            case BINARY_OR: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.OR));
            }

            // **************************************************
            // In-place Dunder Operations
            // **************************************************
            case INPLACE_POWER: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_POWER));
            }
            case INPLACE_MULTIPLY: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_MULTIPLY));
            }
            case INPLACE_MATRIX_MULTIPLY: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_MATRIX_MULTIPLY));
            }
            case INPLACE_FLOOR_DIVIDE: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_FLOOR_DIVIDE));
            }
            case INPLACE_TRUE_DIVIDE: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_TRUE_DIVIDE));
            }
            case INPLACE_MODULO: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_MODULO));
            }
            case INPLACE_ADD: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_ADD));
            }
            case INPLACE_SUBTRACT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_SUBTRACT));
            }
            case INPLACE_LSHIFT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_LSHIFT));
            }
            case INPLACE_RSHIFT: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_RSHIFT));
            }
            case INPLACE_AND: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_AND));
            }
            case INPLACE_XOR: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_XOR));
            }
            case INPLACE_OR: {
                return Optional.of(new BinaryDunderOpcode(instruction, PythonBinaryOperator.INPLACE_OR));
            }

            default:
                return Optional.empty();
        }
    }
}
