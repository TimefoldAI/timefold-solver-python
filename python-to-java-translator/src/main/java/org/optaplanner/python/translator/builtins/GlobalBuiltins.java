package org.optaplanner.python.translator.builtins;

import static java.lang.StackWalker.Option.RETAIN_CLASS_REFERENCE;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import java.util.stream.IntStream;
import java.util.stream.StreamSupport;

import org.optaplanner.python.translator.PythonBinaryOperators;
import org.optaplanner.python.translator.PythonBytecodeToJavaBytecodeTranslator;
import org.optaplanner.python.translator.PythonInterpreter;
import org.optaplanner.python.translator.PythonLikeObject;
import org.optaplanner.python.translator.PythonUnaryOperator;
import org.optaplanner.python.translator.types.CPythonBackedPythonLikeObject;
import org.optaplanner.python.translator.types.Ellipsis;
import org.optaplanner.python.translator.types.NotImplemented;
import org.optaplanner.python.translator.types.PythonLikeFunction;
import org.optaplanner.python.translator.types.PythonLikeType;
import org.optaplanner.python.translator.types.PythonNone;
import org.optaplanner.python.translator.types.PythonRange;
import org.optaplanner.python.translator.types.PythonSlice;
import org.optaplanner.python.translator.types.PythonString;
import org.optaplanner.python.translator.types.collections.PythonIterator;
import org.optaplanner.python.translator.types.collections.PythonLikeDict;
import org.optaplanner.python.translator.types.collections.PythonLikeFrozenSet;
import org.optaplanner.python.translator.types.collections.PythonLikeList;
import org.optaplanner.python.translator.types.collections.PythonLikeSet;
import org.optaplanner.python.translator.types.collections.PythonLikeTuple;
import org.optaplanner.python.translator.types.errors.AttributeError;
import org.optaplanner.python.translator.types.errors.BufferError;
import org.optaplanner.python.translator.types.errors.GeneratorExit;
import org.optaplanner.python.translator.types.errors.ImportError;
import org.optaplanner.python.translator.types.errors.ModuleNotFoundError;
import org.optaplanner.python.translator.types.errors.NameError;
import org.optaplanner.python.translator.types.errors.NotImplementedError;
import org.optaplanner.python.translator.types.errors.PythonAssertionError;
import org.optaplanner.python.translator.types.errors.PythonBaseException;
import org.optaplanner.python.translator.types.errors.PythonException;
import org.optaplanner.python.translator.types.errors.RecursionError;
import org.optaplanner.python.translator.types.errors.ReferenceError;
import org.optaplanner.python.translator.types.errors.RuntimeError;
import org.optaplanner.python.translator.types.errors.StopAsyncIteration;
import org.optaplanner.python.translator.types.errors.StopIteration;
import org.optaplanner.python.translator.types.errors.TypeError;
import org.optaplanner.python.translator.types.errors.UnboundLocalError;
import org.optaplanner.python.translator.types.errors.ValueError;
import org.optaplanner.python.translator.types.errors.arithmetic.ArithmeticError;
import org.optaplanner.python.translator.types.errors.arithmetic.FloatingPointError;
import org.optaplanner.python.translator.types.errors.arithmetic.OverflowError;
import org.optaplanner.python.translator.types.errors.arithmetic.ZeroDivisionError;
import org.optaplanner.python.translator.types.errors.io.BlockingIOError;
import org.optaplanner.python.translator.types.errors.io.ChildProcessError;
import org.optaplanner.python.translator.types.errors.io.EOFError;
import org.optaplanner.python.translator.types.errors.io.FileExistsError;
import org.optaplanner.python.translator.types.errors.io.FileNotFoundError;
import org.optaplanner.python.translator.types.errors.io.InterruptedError;
import org.optaplanner.python.translator.types.errors.io.IsADirectoryError;
import org.optaplanner.python.translator.types.errors.io.KeyboardInterrupt;
import org.optaplanner.python.translator.types.errors.io.MemoryError;
import org.optaplanner.python.translator.types.errors.io.NotADirectoryError;
import org.optaplanner.python.translator.types.errors.io.OSError;
import org.optaplanner.python.translator.types.errors.io.PermissionError;
import org.optaplanner.python.translator.types.errors.io.ProcessLookupError;
import org.optaplanner.python.translator.types.errors.io.SystemError;
import org.optaplanner.python.translator.types.errors.io.SystemExit;
import org.optaplanner.python.translator.types.errors.io.TimeoutError;
import org.optaplanner.python.translator.types.errors.io.connection.BrokenPipeError;
import org.optaplanner.python.translator.types.errors.io.connection.ConnectionAbortedError;
import org.optaplanner.python.translator.types.errors.io.connection.ConnectionError;
import org.optaplanner.python.translator.types.errors.io.connection.ConnectionRefusedError;
import org.optaplanner.python.translator.types.errors.io.connection.ConnectionResetError;
import org.optaplanner.python.translator.types.errors.lookup.IndexError;
import org.optaplanner.python.translator.types.errors.lookup.KeyError;
import org.optaplanner.python.translator.types.errors.lookup.LookupError;
import org.optaplanner.python.translator.types.errors.syntax.IndentationError;
import org.optaplanner.python.translator.types.errors.syntax.SyntaxError;
import org.optaplanner.python.translator.types.errors.syntax.TabError;
import org.optaplanner.python.translator.types.errors.unicode.UnicodeDecodeError;
import org.optaplanner.python.translator.types.errors.unicode.UnicodeEncodeError;
import org.optaplanner.python.translator.types.errors.unicode.UnicodeError;
import org.optaplanner.python.translator.types.errors.unicode.UnicodeTranslateError;
import org.optaplanner.python.translator.types.errors.warning.BytesWarning;
import org.optaplanner.python.translator.types.errors.warning.DeprecationWarning;
import org.optaplanner.python.translator.types.errors.warning.EncodingWarning;
import org.optaplanner.python.translator.types.errors.warning.FutureWarning;
import org.optaplanner.python.translator.types.errors.warning.ImportWarning;
import org.optaplanner.python.translator.types.errors.warning.PendingDeprecationWarning;
import org.optaplanner.python.translator.types.errors.warning.ResourceWarning;
import org.optaplanner.python.translator.types.errors.warning.RuntimeWarning;
import org.optaplanner.python.translator.types.errors.warning.SyntaxWarning;
import org.optaplanner.python.translator.types.errors.warning.UnicodeWarning;
import org.optaplanner.python.translator.types.errors.warning.UserWarning;
import org.optaplanner.python.translator.types.errors.warning.Warning;
import org.optaplanner.python.translator.types.numeric.PythonBoolean;
import org.optaplanner.python.translator.types.numeric.PythonFloat;
import org.optaplanner.python.translator.types.numeric.PythonInteger;

public class GlobalBuiltins {
    private final static StackWalker stackWalker = getStackWalkerInstance();
    private final static Map<String, PythonLikeObject> builtinConstantMap = new HashMap<>();

    static {
        loadBuiltinConstants();
    }

    private static StackWalker getStackWalkerInstance() {
        return StackWalker.getInstance(RETAIN_CLASS_REFERENCE);
    }

    public static void addBuiltinType(PythonLikeType type) {
        addBuiltinConstant(type.getTypeName(), type);
    }

    public static void addBuiltinConstant(String builtinName, PythonLikeObject value) {
        builtinConstantMap.put(builtinName, value);
    }

    public static List<PythonLikeType> getBuiltinTypes() {
        List<PythonLikeType> out = new ArrayList<>();
        for (PythonLikeObject constant : builtinConstantMap.values()) {
            if (constant instanceof PythonLikeType) {
                out.add((PythonLikeType) constant);
            }
        }
        return out;
    }

    public static void loadBuiltinConstants() {
        // Constants
        addBuiltinConstant("None", PythonNone.INSTANCE);
        addBuiltinConstant("Ellipsis", Ellipsis.INSTANCE);
        addBuiltinConstant("NotImplemented", NotImplemented.INSTANCE);
        addBuiltinConstant("True", PythonBoolean.TRUE);
        addBuiltinConstant("False", PythonBoolean.FALSE);

        // Exceptions
        addBuiltinType(ArithmeticError.ARITHMETIC_ERROR_TYPE);
        addBuiltinType(FloatingPointError.FLOATING_POINT_ERROR_TYPE);
        addBuiltinType(OverflowError.OVERFLOW_ERROR_TYPE);
        addBuiltinType(ZeroDivisionError.ZERO_DIVISION_ERROR_TYPE);

        addBuiltinType(BrokenPipeError.BROKEN_PIPE_ERROR_TYPE);
        addBuiltinType(ConnectionAbortedError.CONNECTION_ABORTED_ERROR_TYPE);
        addBuiltinType(ConnectionError.CONNECTION_ERROR_TYPE);
        addBuiltinType(ConnectionRefusedError.CONNECTION_REFUSED_ERROR_TYPE);
        addBuiltinType(ConnectionResetError.CONNECTION_RESET_ERROR_TYPE);

        addBuiltinType(BlockingIOError.BLOCKING_IO_ERROR_TYPE);
        addBuiltinType(ChildProcessError.CHILD_PROCESS_ERROR_TYPE);
        addBuiltinType(EOFError.EOF_ERROR_TYPE);
        addBuiltinType(FileExistsError.FILE_EXISTS_ERROR_TYPE);
        addBuiltinType(FileNotFoundError.FILE_NOT_FOUND_ERROR_TYPE);
        addBuiltinType(InterruptedError.INTERRUPTED_ERROR_TYPE);
        addBuiltinType(IsADirectoryError.IS_A_DIRECTORY_ERROR_TYPE);
        addBuiltinType(KeyboardInterrupt.KEYBOARD_INTERRUPT_TYPE);
        addBuiltinType(MemoryError.MEMORY_ERROR_TYPE);
        addBuiltinType(NotADirectoryError.NOT_A_DIRECTORY_ERROR_TYPE);
        addBuiltinType(OSError.OS_ERROR_TYPE);
        addBuiltinType(PermissionError.PERMISSION_ERROR_TYPE);
        addBuiltinType(ProcessLookupError.PROCESS_LOOKUP_ERROR_TYPE);
        addBuiltinType(SystemError.SYSTEM_ERROR_TYPE);
        addBuiltinType(SystemExit.SYSTEM_EXIT_TYPE);
        addBuiltinType(TimeoutError.TIMEOUT_ERROR_TYPE);

        addBuiltinType(IndexError.INDEX_ERROR_TYPE);
        addBuiltinType(KeyError.KEY_ERROR_TYPE);
        addBuiltinType(LookupError.LOOKUP_ERROR_TYPE);

        addBuiltinType(IndentationError.INDENTATION_ERROR_TYPE);
        addBuiltinType(SyntaxError.SYNTAX_ERROR_TYPE);
        addBuiltinType(TabError.TAB_ERROR_TYPE);

        addBuiltinType(UnicodeDecodeError.UNICODE_DECODE_ERROR_TYPE);
        addBuiltinType(UnicodeEncodeError.UNICODE_ENCODE_ERROR_TYPE);
        addBuiltinType(UnicodeError.UNICODE_ERROR_TYPE);
        addBuiltinType(UnicodeTranslateError.UNICODE_TRANSLATE_ERROR_TYPE);

        addBuiltinType(BytesWarning.BYTES_WARNING_TYPE);
        addBuiltinType(DeprecationWarning.DEPRECATION_WARNING_TYPE);
        addBuiltinType(EncodingWarning.ENCODING_WARNING_TYPE);
        addBuiltinType(FutureWarning.FUTURE_WARNING_TYPE);
        addBuiltinType(ImportWarning.IMPORT_WARNING_TYPE);
        addBuiltinType(PendingDeprecationWarning.PENDING_DEPRECATION_WARNING_TYPE);
        addBuiltinType(ResourceWarning.RESOURCE_WARNING_TYPE);
        addBuiltinType(RuntimeWarning.RUNTIME_WARNING_TYPE);
        addBuiltinType(SyntaxWarning.SYNTAX_WARNING_TYPE);
        addBuiltinType(UnicodeWarning.UNICODE_WARNING_TYPE);
        addBuiltinType(UserWarning.USER_WARNING_TYPE);
        addBuiltinType(Warning.WARNING_TYPE);

        addBuiltinType(AttributeError.ATTRIBUTE_ERROR_TYPE);
        addBuiltinType(BufferError.BUFFER_ERROR_TYPE);
        addBuiltinType(GeneratorExit.GENERATOR_EXIT_TYPE);
        addBuiltinType(ImportError.IMPORT_ERROR_TYPE);
        addBuiltinType(ModuleNotFoundError.MODULE_NOT_FOUND_ERROR_TYPE);
        addBuiltinType(NameError.NAME_ERROR_TYPE);
        addBuiltinType(NotImplementedError.NOT_IMPLEMENTED_ERROR_TYPE);
        addBuiltinType(PythonAssertionError.ASSERTION_ERROR_TYPE);
        addBuiltinType(PythonBaseException.BASE_EXCEPTION_TYPE);
        addBuiltinType(PythonException.EXCEPTION_TYPE);
        addBuiltinType(RecursionError.RECURSION_ERROR_TYPE);
        addBuiltinType(ReferenceError.REFERENCE_ERROR_TYPE);
        addBuiltinType(RuntimeError.RUNTIME_ERROR_TYPE);
        addBuiltinType(StopAsyncIteration.STOP_ASYNC_ITERATION_TYPE);
        addBuiltinType(StopIteration.STOP_ITERATION_TYPE);
        addBuiltinType(UnboundLocalError.UNBOUND_LOCAL_ERROR_TYPE);
        addBuiltinType(TypeError.TYPE_ERROR_TYPE);
        addBuiltinType(ValueError.VALUE_ERROR_TYPE);
    }

    public static PythonLikeObject lookup(PythonInterpreter interpreter, String builtinName) {
        switch (builtinName) {
            case "abs":
                return UnaryDunderBuiltin.ABS;
            case "all":
                return ((PythonLikeFunction) GlobalBuiltins::all);
            case "any":
                return ((PythonLikeFunction) GlobalBuiltins::any);
            case "ascii":
                return ((PythonLikeFunction) GlobalBuiltins::ascii);
            case "bin":
                return ((PythonLikeFunction) GlobalBuiltins::bin);
            case "bool":
                return PythonBoolean.getBooleanType();
            case "callable":
                return ((PythonLikeFunction) GlobalBuiltins::callable);
            case "chr":
                return ((PythonLikeFunction) GlobalBuiltins::chr);
            case "delattr":
                return ((PythonLikeFunction) GlobalBuiltins::delattr);
            case "divmod":
                return BinaryDunderBuiltin.DIVMOD;
            case "dict":
                return PythonLikeDict.DICT_TYPE;
            case "enumerate":
                return ((PythonLikeFunction) GlobalBuiltins::enumerate);
            case "filter":
                return ((PythonLikeFunction) GlobalBuiltins::filter);
            case "float":
                return PythonFloat.FLOAT_TYPE;
            case "format":
                return ((PythonLikeFunction) GlobalBuiltins::format);
            case "frozenset":
                return PythonLikeFrozenSet.FROZEN_SET_TYPE;
            case "getattr":
                return ((PythonLikeFunction) GlobalBuiltins::getattr);
            case "globals":
                return ((PythonLikeFunction) GlobalBuiltins::globals);
            case "hasattr":
                return ((PythonLikeFunction) GlobalBuiltins::hasattr);
            case "hash":
                return UnaryDunderBuiltin.HASH;
            case "hex":
                return ((PythonLikeFunction) GlobalBuiltins::hex);
            case "id":
                return ((PythonLikeFunction) GlobalBuiltins::id);
            case "input":
                return GlobalBuiltins.input(interpreter);
            case "int":
                return PythonInteger.getIntType();
            case "isinstance":
                return ((PythonLikeFunction) GlobalBuiltins::isinstance);
            case "issubclass":
                return ((PythonLikeFunction) GlobalBuiltins::issubclass);
            case "iter":
                return UnaryDunderBuiltin.ITERATOR; // TODO: Iterator with sentinel value
            case "len":
                return UnaryDunderBuiltin.LENGTH;
            case "list":
                return PythonLikeList.LIST_TYPE;
            case "locals":
                return ((PythonLikeFunction) GlobalBuiltins::locals);
            case "map":
                return ((PythonLikeFunction) GlobalBuiltins::map);
            case "min":
                return ((PythonLikeFunction) GlobalBuiltins::min);
            case "max":
                return ((PythonLikeFunction) GlobalBuiltins::max);
            case "next":
                return UnaryDunderBuiltin.NEXT;
            case "object":
                return PythonLikeType.getBaseType();
            case "oct":
                return ((PythonLikeFunction) GlobalBuiltins::oct);
            case "ord":
                return ((PythonLikeFunction) GlobalBuiltins::ord);
            case "pow":
                return ((PythonLikeFunction) GlobalBuiltins::pow);
            case "print":
                return GlobalBuiltins.print(interpreter);
            case "range":
                return PythonRange.RANGE_TYPE;
            case "repr":
                return UnaryDunderBuiltin.REPRESENTATION;
            case "reversed":
                return ((PythonLikeFunction) GlobalBuiltins::reversed);
            case "round":
                return ((PythonLikeFunction) GlobalBuiltins::round);
            case "set":
                return PythonLikeSet.SET_TYPE;
            case "setattr":
                return ((PythonLikeFunction) GlobalBuiltins::setattr);
            case "slice":
                return PythonSlice.SLICE_TYPE;
            case "sorted":
                return ((PythonLikeFunction) GlobalBuiltins::sorted);
            case "str":
                return PythonString.STRING_TYPE;
            case "sum":
                return ((PythonLikeFunction) GlobalBuiltins::sum);
            case "tuple":
                return PythonLikeTuple.TUPLE_TYPE;
            case "type":
                return PythonLikeType.getTypeType();
            case "vars":
                return ((PythonLikeFunction) GlobalBuiltins::vars);
            case "zip":
                return ((PythonLikeFunction) GlobalBuiltins::zip);
            case "__import__":
                return GlobalBuiltins.importFunction(interpreter);
            default:
                return builtinConstantMap.get(builtinName);
        }
    }

    public static PythonLikeObject lookupOrError(PythonInterpreter interpreter, String builtinName) {
        PythonLikeObject out = lookup(interpreter, builtinName);
        if (out == null) {
            throw new IllegalArgumentException(builtinName + " does not exist in global scope");
        }
        return out;
    }

    public static PythonBoolean all(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        Iterator<PythonLikeObject> iterator;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR.invoke(positionalArgs.get(0));
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("iterable"))) {
            iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR
                    .invoke(keywordArgs.get(PythonString.valueOf("iterable")));
        } else {
            throw new ValueError("all expects 1 argument, got " + positionalArgs.size());
        }

        while (iterator.hasNext()) {
            PythonLikeObject element = iterator.next();
            if (!PythonBoolean.isTruthful(element)) {
                return PythonBoolean.FALSE;
            }
        }

        return PythonBoolean.TRUE;
    }

    public static PythonBoolean any(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        Iterator<PythonLikeObject> iterator;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR.invoke(positionalArgs.get(0));
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("iterable"))) {
            iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR
                    .invoke(keywordArgs.get(PythonString.valueOf("iterable")));
        } else {
            throw new ValueError("any expects 1 argument, got " + positionalArgs.size());
        }

        while (iterator.hasNext()) {
            PythonLikeObject element = iterator.next();
            if (PythonBoolean.isTruthful(element)) {
                return PythonBoolean.TRUE;
            }
        }

        return PythonBoolean.FALSE;
    }

    public static PythonString ascii(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("object"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
        } else {
            throw new ValueError("ascii expects 1 argument, got " + positionalArgs.size());
        }

        PythonString reprString = (PythonString) UnaryDunderBuiltin.REPRESENTATION.invoke(object);
        String asciiString = reprString.value.codePoints().flatMap((character) -> {
            if (character < 128) {
                return IntStream.of(character);
            } else {
                // \Uxxxxxxxx
                IntStream.Builder builder = IntStream.builder().add('\\').add('U');
                String hexString = Integer.toHexString(character);
                for (int i = 8; i > hexString.length(); i--) {
                    builder.add('0');
                }
                hexString.codePoints().forEach(builder);
                return builder.build();
            }
        }).collect(StringBuilder::new,
                StringBuilder::appendCodePoint,
                StringBuilder::append).toString();

        return PythonString.valueOf(asciiString);
    }

    public static PythonString bin(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("x"))) {
            object = keywordArgs.get(PythonString.valueOf("x"));
        } else {
            throw new ValueError("bin expects 1 argument, got " + positionalArgs.size());
        }

        PythonInteger integer;

        if (object instanceof PythonInteger) {
            integer = (PythonInteger) object;
        } else {
            integer = (PythonInteger) UnaryDunderBuiltin.INDEX.invoke(object);
        }

        String binaryString = integer.value.toString(2);

        if (binaryString.startsWith("-")) {
            return PythonString.valueOf("-0b" + binaryString.substring(1));
        } else {
            return PythonString.valueOf("0b" + binaryString);
        }
    }

    public static PythonBoolean callable(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("object"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
        } else {
            throw new ValueError("callable expects 1 argument, got " + positionalArgs.size());
        }

        return PythonBoolean.valueOf(object instanceof PythonLikeFunction);
    }

    public static PythonString chr(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("i"))) {
            object = keywordArgs.get(PythonString.valueOf("i"));
        } else {
            throw new ValueError("chr expects 1 argument, got " + positionalArgs.size());
        }

        PythonInteger integer = (PythonInteger) object;

        if (integer.value.compareTo(BigInteger.valueOf(0x10FFFF)) > 0 || integer.value.compareTo(BigInteger.ZERO) < 0) {
            throw new ValueError("Integer (" + integer + ") outside valid range for chr (0 through 1,114,111)");
        }

        return PythonString.valueOf(Character.toString(integer.value.intValueExact()));
    }

    public static PythonNone delattr(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;
        PythonString name;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 2) {
            object = positionalArgs.get(0);
            name = (PythonString) positionalArgs.get(1);
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("name"))) {
            object = positionalArgs.get(0);
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("object"))
                && keywordArgs.containsKey(PythonString.valueOf("name"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
        } else {
            throw new ValueError("delattr expects 2 argument, got " + positionalArgs.size());
        }

        object.__deleteAttribute(name.value);

        return PythonNone.INSTANCE;
    }

    public static PythonLikeObject enumerate(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject iterable;
        PythonLikeObject start = PythonInteger.valueOf(0);

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 2) {
            iterable = positionalArgs.get(0);
            start = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1) {
            iterable = positionalArgs.get(0);
            if (keywordArgs.containsKey(PythonString.valueOf("start"))) {
                start = keywordArgs.get(PythonString.valueOf("start"));
            }
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("iterable"))) {
            iterable = keywordArgs.get(PythonString.valueOf("iterable"));
            if (keywordArgs.containsKey(PythonString.valueOf("start"))) {
                start = keywordArgs.get(PythonString.valueOf("start"));
            }
        } else {
            throw new ValueError("enumerate expects 1 or 2 argument, got " + positionalArgs.size());
        }

        final PythonLikeObject iterator = UnaryDunderBuiltin.ITERATOR.invoke(iterable);
        final AtomicReference<PythonLikeObject> currentValue = new AtomicReference(null);
        final AtomicReference<PythonLikeObject> currentIndex = new AtomicReference(start);
        final AtomicBoolean shouldCallNext = new AtomicBoolean(true);

        return new PythonIterator(new Iterator<PythonLikeObject>() {
            @Override
            public boolean hasNext() {
                if (shouldCallNext.get()) {
                    try {
                        currentValue.set(UnaryDunderBuiltin.NEXT.invoke(iterator));
                    } catch (StopIteration e) {
                        currentValue.set(null);
                        shouldCallNext.set(false);
                        return false;
                    }
                    shouldCallNext.set(false);
                    return true;
                } else {
                    // we already called next
                    return currentValue.get() != null;
                }
            }

            @Override
            public PythonLikeObject next() {
                PythonLikeObject value;
                if (currentValue.get() != null) {
                    shouldCallNext.set(true);
                    value = currentValue.get();
                    currentValue.set(null);
                } else {
                    value = UnaryDunderBuiltin.NEXT.invoke(iterator);
                    shouldCallNext.set(true);
                }
                PythonLikeObject index = currentIndex.get();
                currentIndex.set(BinaryDunderBuiltin.ADD.invoke(index, PythonInteger.valueOf(1)));
                return PythonLikeTuple.fromList(List.of(index, value));
            }
        });
    }

    public static PythonIterator filter(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject function;
        PythonLikeObject iterable;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 2 && keywordArgs.isEmpty()) {
            function = positionalArgs.get(0);
            iterable = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1) {
            function = positionalArgs.get(0);
            iterable = keywordArgs.get(PythonString.valueOf("iterable"));
            if (iterable == null) {
                throw new ValueError("iterable is None");
            }
        } else if (positionalArgs.size() == 0) {
            function = keywordArgs.get(PythonString.valueOf("function"));
            iterable = keywordArgs.get(PythonString.valueOf("iterable"));
            if (iterable == null) {
                throw new ValueError("iterable is None");
            }

            if (function == null) {
                function = PythonNone.INSTANCE;
            }
        } else {
            throw new ValueError("filter expects 2 argument, got " + positionalArgs.size());
        }

        Iterator iterator;
        if (iterable instanceof Collection) {
            iterator = ((Collection) iterable).iterator();
        } else if (iterable instanceof Iterator) {
            iterator = (Iterator) iterable;
        } else {
            iterator = (Iterator) UnaryDunderBuiltin.ITERATOR.invoke(iterable);
        }

        PythonLikeFunction predicate;

        if (function == PythonNone.INSTANCE) {
            predicate = (pos, keywords) -> pos.get(0);
        } else {
            predicate = (PythonLikeFunction) function;
        }

        return new PythonIterator(StreamSupport.stream(
                Spliterators.spliteratorUnknownSize(iterator, Spliterator.ORDERED),
                false)
                .filter(element -> PythonBoolean.isTruthful(predicate.__call__(List.of((PythonLikeObject) element), null)))
                .iterator());
    }

    public static PythonLikeObject format(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject toFormat;
        PythonLikeObject formatSpec = PythonString.valueOf("");

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 2 && keywordArgs.isEmpty()) {
            toFormat = positionalArgs.get(0);
            formatSpec = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1) {
            toFormat = positionalArgs.get(0);
            if (keywordArgs.containsKey(PythonString.valueOf("format_spec"))) {
                formatSpec = keywordArgs.get(PythonString.valueOf("format_spec"));
            }
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("value"))) {
            toFormat = keywordArgs.get(PythonString.valueOf("value"));
            if (keywordArgs.containsKey(PythonString.valueOf("format_spec"))) {
                formatSpec = keywordArgs.get(PythonString.valueOf("format_spec"));
            }
        } else {
            throw new ValueError("format expects 1 or 2 arguments, got " + positionalArgs.size());
        }

        return ObjectBuiltinOperations.format(toFormat, formatSpec);
    }

    public static PythonLikeObject getattr(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;
        PythonString name;
        PythonLikeObject defaultValue = null;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 3) {
            object = positionalArgs.get(0);
            name = (PythonString) positionalArgs.get(1);
            defaultValue = positionalArgs.get(2);
        } else if (positionalArgs.size() == 2) {
            object = positionalArgs.get(0);
            name = (PythonString) positionalArgs.get(1);
            defaultValue = keywordArgs.get(PythonString.valueOf("default"));
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("name"))) {
            object = positionalArgs.get(0);
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
            defaultValue = keywordArgs.get(PythonString.valueOf("default"));
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("object"))
                && keywordArgs.containsKey(PythonString.valueOf("name"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
            defaultValue = keywordArgs.get(PythonString.valueOf("default"));
        } else {
            throw new ValueError("getattr expects 2 or 3 arguments, got " + positionalArgs.size());
        }

        PythonLikeFunction getAttribute = (PythonLikeFunction) object.__getType().__getAttributeOrError("__getattribute__");

        try {
            return getAttribute.__call__(List.of(object, name), null);
        } catch (AttributeError attributeError) {
            if (defaultValue != null) {
                return defaultValue;
            } else {
                throw attributeError;
            }
        }
    }

    public static PythonLikeDict globals(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (!positionalArgs.isEmpty() && keywordArgs.isEmpty()) {
            throw new ValueError("globals expects 0 arguments, got " + positionalArgs.size());
        }
        Class<?> callerClass = stackWalker.getCallerClass();

        try {
            Map globalsMap =
                    (Map) callerClass.getField(PythonBytecodeToJavaBytecodeTranslator.GLOBALS_MAP_STATIC_FIELD_NAME).get(null);
            return PythonLikeDict.mirror(globalsMap);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new IllegalStateException("Caller is not a generated class");
        }
    }

    public static PythonBoolean hasattr(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        try {
            getattr(positionalArgs, keywordArgs);
            return PythonBoolean.TRUE;
        } catch (AttributeError error) {
            return PythonBoolean.FALSE;
        }
    }

    public static PythonString hex(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("x"))) {
            object = keywordArgs.get(PythonString.valueOf("x"));
        } else {
            throw new ValueError("hex expects 1 argument, got " + positionalArgs.size());
        }

        PythonInteger integer;

        if (object instanceof PythonInteger) {
            integer = (PythonInteger) object;
        } else {
            integer = (PythonInteger) UnaryDunderBuiltin.INDEX.invoke(object);
        }

        String hexString = integer.value.toString(16);

        if (hexString.startsWith("-")) {
            return PythonString.valueOf("-0x" + hexString.substring(1));
        } else {
            return PythonString.valueOf("0x" + hexString);
        }
    }

    public static PythonInteger id(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("object"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
        } else {
            throw new ValueError("id expects 1 argument, got " + positionalArgs.size());
        }

        if (object instanceof CPythonBackedPythonLikeObject) {
            CPythonBackedPythonLikeObject cPythonBackedPythonLikeObject = (CPythonBackedPythonLikeObject) object;
            if (cPythonBackedPythonLikeObject.$cpythonId != null) {
                return cPythonBackedPythonLikeObject.$cpythonId;
            }
        }

        return PythonInteger.valueOf(System.identityHashCode(object));
    }

    public static PythonLikeFunction input(PythonInterpreter interpreter) {
        return (positionalArguments, namedArguments) -> {
            PythonString prompt = null;
            if (positionalArguments.size() == 1) {
                prompt = (PythonString) positionalArguments.get(0);
            } else if (positionalArguments.size() == 0 && namedArguments.containsKey(PythonString.valueOf("prompt"))) {
                prompt = (PythonString) namedArguments.get(PythonString.valueOf("prompt"));
            } else {
                throw new ValueError("input expects 0 or 1 arguments, got " + positionalArguments.size());
            }

            if (prompt != null) {
                interpreter.write(prompt.value);
            }

            String line = interpreter.readLine();

            return PythonString.valueOf(line);
        };
    }

    public static PythonBoolean isinstance(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;
        PythonLikeObject classInfo;

        if (positionalArgs.size() == 2) {
            object = positionalArgs.get(0);
            classInfo = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("classinfo"))) {
            object = positionalArgs.get(0);
            classInfo = keywordArgs.get(PythonString.valueOf("classinfo"));
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("object"))
                && keywordArgs.containsKey(PythonString.valueOf("classinfo"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
            classInfo = keywordArgs.get(PythonString.valueOf("classinfo"));
        } else {
            throw new ValueError("isinstance expects 2 arguments, got " + positionalArgs.size());
        }

        if (classInfo instanceof PythonLikeType) {
            return PythonBoolean.valueOf(((PythonLikeType) classInfo).isInstance(object));
        } else if (classInfo instanceof List) {
            for (PythonLikeObject possibleType : (List<PythonLikeObject>) classInfo) {
                if (isinstance(List.of(object, possibleType), null).getBooleanValue()) {
                    return PythonBoolean.TRUE;
                }
            }
            return PythonBoolean.FALSE;
        } else {
            throw new ValueError("classInfo (" + classInfo + ") is not a tuple of types or a type"); // TODO: Use TypeError
        }
    }

    public static PythonBoolean issubclass(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeType type;
        PythonLikeObject classInfo;

        if (positionalArgs.size() == 2) {
            type = (PythonLikeType) positionalArgs.get(0);
            classInfo = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("classinfo"))) {
            type = (PythonLikeType) positionalArgs.get(0);
            classInfo = keywordArgs.get(PythonString.valueOf("classinfo"));
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("class"))
                && keywordArgs.containsKey(PythonString.valueOf("classinfo"))) {
            type = (PythonLikeType) keywordArgs.get(PythonString.valueOf("class"));
            classInfo = keywordArgs.get(PythonString.valueOf("classinfo"));
        } else {
            throw new ValueError("isinstance expects 2 arguments, got " + positionalArgs.size());
        }

        if (classInfo instanceof PythonLikeType) {
            return PythonBoolean.valueOf(type.isSubclassOf((PythonLikeType) classInfo));
        } else if (classInfo instanceof List) {
            for (PythonLikeObject possibleType : (List<PythonLikeObject>) classInfo) {
                if (issubclass(List.of(type, possibleType), null).getBooleanValue()) {
                    return PythonBoolean.TRUE;
                }
            }
            return PythonBoolean.FALSE;
        } else {
            throw new ValueError("classInfo (" + classInfo + ") is not a tuple of types or a type"); // TODO: Use TypeError
        }
    }

    public static PythonLikeDict locals(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        throw new ValueError("builtin locals is not supported when executed in Java bytecode");
    }

    public static PythonIterator map(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeFunction function;
        List<PythonLikeObject> iterableList = new ArrayList<>();

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() >= 2 && keywordArgs.isEmpty()) {
            function = (PythonLikeFunction) positionalArgs.get(0);
            iterableList = positionalArgs.subList(1, positionalArgs.size());
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("iterable"))) {
            function = (PythonLikeFunction) positionalArgs.get(0);
            iterableList.add(keywordArgs.get(PythonString.valueOf("iterable")));
        } else if (positionalArgs.size() == 0
                && keywordArgs.containsKey(PythonString.valueOf("function"))
                && keywordArgs.containsKey(PythonString.valueOf("iterable"))) {
            function = (PythonLikeFunction) keywordArgs.get(PythonString.valueOf("function"));
            iterableList.add(keywordArgs.get(PythonString.valueOf("iterable")));
        } else {
            throw new ValueError("map expects at least 2 argument, got " + positionalArgs.size());
        }

        final List<Iterator> iteratorList = new ArrayList<>(iterableList.size());

        for (PythonLikeObject iterable : iterableList) {
            Iterator iterator;
            if (iterable instanceof Collection) {
                iterator = ((Collection) iterable).iterator();
            } else if (iterable instanceof Iterator) {
                iterator = (Iterator) iterable;
            } else {
                iterator = (Iterator) UnaryDunderBuiltin.ITERATOR.invoke(iterable);
            }
            iteratorList.add(iterator);
        }

        Iterator<List<PythonLikeObject>> iteratorIterator = new Iterator<List<PythonLikeObject>>() {
            @Override
            public boolean hasNext() {
                return iteratorList.stream().allMatch(Iterator::hasNext);
            }

            @Override
            public List<PythonLikeObject> next() {
                List<PythonLikeObject> out = new ArrayList<>(iteratorList.size());
                for (Iterator iterator : iteratorList) {
                    out.add((PythonLikeObject) iterator.next());
                }
                return out;
            }
        };

        return new PythonIterator(StreamSupport.stream(
                Spliterators.spliteratorUnknownSize(iteratorIterator, Spliterator.ORDERED),
                false)
                .map(element -> function.__call__(element, null))
                .iterator());
    }

    public static PythonLikeObject min(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.isEmpty()) {
            PythonLikeObject defaultValue = keywordArgs.get(PythonString.valueOf("default"));
            if (!keywordArgs.containsKey(PythonString.valueOf("default"))) {
                throw new ValueError("No arguments were passed to min, and no default was provided");
            }
            return defaultValue;
        } else if (positionalArgs.size() == 1) {
            Iterator<Comparable> iterator = (Iterator<Comparable>) ((PythonLikeFunction) (positionalArgs.get(0).__getType()
                    .__getAttributeOrError("__iter__"))).__call__(List.of(positionalArgs.get(0)),
                            Map.of());
            Comparable min = null;
            for (Iterator<Comparable> it = iterator; it.hasNext();) {
                Comparable item = it.next();
                if (min == null) {
                    min = item;
                } else {
                    if (item.compareTo(min) < 0) {
                        min = item;
                    }
                }
            }
            if (min == null) {
                PythonLikeObject defaultValue = keywordArgs.get(PythonString.valueOf("default"));
                if (!keywordArgs.containsKey(PythonString.valueOf("default"))) {
                    throw new ValueError("Iterable is empty, and no default was provided");
                }
                return defaultValue;
            } else {
                return (PythonLikeObject) min;
            }
        } else {
            Comparable min = (Comparable) positionalArgs.get(0);
            for (PythonLikeObject item : positionalArgs) {
                Comparable comparableItem = (Comparable) item;
                if (comparableItem.compareTo(min) < 0) {
                    min = comparableItem;
                }
            }
            return (PythonLikeObject) min;
        }
    }

    public static PythonLikeObject max(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.isEmpty()) {
            PythonLikeObject defaultValue = keywordArgs.get(PythonString.valueOf("default"));
            if (!keywordArgs.containsKey(PythonString.valueOf("default"))) {
                throw new ValueError("No arguments were passed to max, and no default was provided");
            }
            return defaultValue;
        } else if (positionalArgs.size() == 1) {
            Iterator<Comparable> iterator = (Iterator<Comparable>) ((PythonLikeFunction) (positionalArgs.get(0).__getType()
                    .__getAttributeOrError("__iter__"))).__call__(List.of(positionalArgs.get(0)),
                            Map.of());
            Comparable max = null;
            for (Iterator<Comparable> it = iterator; it.hasNext();) {
                Comparable item = it.next();
                if (max == null) {
                    max = item;
                } else {
                    if (item.compareTo(max) > 0) {
                        max = item;
                    }
                }
            }
            if (max == null) {
                PythonLikeObject defaultValue = keywordArgs.get(PythonString.valueOf("default"));
                if (!keywordArgs.containsKey(PythonString.valueOf("default"))) {
                    throw new ValueError("Iterable is empty, and no default was provided");
                }
                return defaultValue;
            } else {
                return (PythonLikeObject) max;
            }
        } else {
            Comparable max = (Comparable) positionalArgs.get(0);
            for (PythonLikeObject item : positionalArgs) {
                Comparable comparableItem = (Comparable) item;
                if (comparableItem.compareTo(max) > 0) {
                    max = comparableItem;
                }
            }
            return (PythonLikeObject) max;
        }
    }

    public static PythonString oct(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            object = positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("x"))) {
            object = keywordArgs.get(PythonString.valueOf("x"));
        } else {
            throw new ValueError("oct expects 1 argument, got " + positionalArgs.size());
        }

        PythonInteger integer;

        if (object instanceof PythonInteger) {
            integer = (PythonInteger) object;
        } else {
            integer = (PythonInteger) UnaryDunderBuiltin.INDEX.invoke(object);
        }

        String octString = integer.value.toString(8);

        if (octString.startsWith("-")) {
            return PythonString.valueOf("-0o" + octString.substring(1));
        } else {
            return PythonString.valueOf("0o" + octString);
        }
    }

    public static PythonInteger ord(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonString character;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 1 && keywordArgs.isEmpty()) {
            character = (PythonString) positionalArgs.get(0);
        } else if (positionalArgs.isEmpty() && keywordArgs.size() == 1
                && keywordArgs.containsKey(PythonString.valueOf("c"))) {
            character = (PythonString) keywordArgs.get(PythonString.valueOf("c"));
        } else {
            throw new ValueError("ord expects 1 argument, got " + positionalArgs.size());
        }

        if (character.length() != 1) {
            throw new ValueError("String \"" + character + "\" does not represent a single character");
        }

        return PythonInteger.valueOf(character.value.charAt(0));
    }

    public static PythonLikeObject pow(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject base;
        PythonLikeObject exp;
        PythonLikeObject mod = null;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 3 && keywordArgs.isEmpty()) {
            base = positionalArgs.get(0);
            exp = positionalArgs.get(1);
            mod = positionalArgs.get(2);
        } else if (positionalArgs.size() == 2) {
            base = positionalArgs.get(0);
            exp = positionalArgs.get(1);
            mod = keywordArgs.get(PythonString.valueOf("mod"));
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("exp"))) {
            base = positionalArgs.get(0);
            exp = keywordArgs.get(PythonString.valueOf("exp"));
            mod = keywordArgs.get(PythonString.valueOf("mod"));
        } else if (positionalArgs.isEmpty() && keywordArgs.containsKey(PythonString.valueOf("base"))
                && keywordArgs.containsKey(PythonString.valueOf("exp"))) {
            base = keywordArgs.get(PythonString.valueOf("base"));
            exp = keywordArgs.get(PythonString.valueOf("exp"));
            mod = keywordArgs.get(PythonString.valueOf("mod"));
        } else {
            throw new ValueError("pow expects 2 or 3 arguments, got " + positionalArgs.size());
        }

        if (mod == null) {
            return BinaryDunderBuiltin.POWER.invoke(base, exp);
        } else {
            return TernaryDunderBuiltin.POWER.invoke(base, exp, mod);
        }
    }

    public static PythonLikeFunction print(PythonInterpreter interpreter) {

        return (positionalArgs, keywordArgs) -> {
            List<PythonLikeObject> objects = positionalArgs;
            String sep;
            if (!keywordArgs.containsKey(PythonString.valueOf("sep"))
                    || keywordArgs.get(PythonString.valueOf("sep")) == PythonNone.INSTANCE) {
                sep = " ";
            } else {
                sep = ((PythonString) keywordArgs.get(PythonString.valueOf("sep"))).value;
            }
            String end;
            if (!keywordArgs.containsKey(PythonString.valueOf("end"))
                    || keywordArgs.get(PythonString.valueOf("end")) == PythonNone.INSTANCE) {
                end = "\n";
            } else {
                end = ((PythonString) keywordArgs.get(PythonString.valueOf("end"))).value;
            }
            // TODO: support file keyword arg

            boolean flush;
            if (!keywordArgs.containsKey(PythonString.valueOf("flush"))
                    || keywordArgs.get(PythonString.valueOf("flush")) == PythonNone.INSTANCE) {
                flush = false;
            } else {
                flush = ((PythonBoolean) keywordArgs.get(PythonString.valueOf("flush"))).getBooleanValue();
            }

            for (int i = 0; i < objects.size() - 1; i++) {
                interpreter.write(UnaryDunderBuiltin.STR.invoke(objects.get(i)).toString());
                interpreter.write(sep);
            }
            if (!objects.isEmpty()) {
                interpreter.write(UnaryDunderBuiltin.STR.invoke(objects.get(objects.size() - 1)).toString());
            }
            interpreter.write(end);

            if (flush) {
                System.out.flush();
            }

            return PythonNone.INSTANCE;
        };
    };

    public static PythonLikeObject reversed(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        PythonLikeObject sequence;
        if (positionalArgs.size() != 1) {
            throw new ValueError("reversed() expects 1 argument, got " + positionalArgs.size());
        }

        sequence = positionalArgs.get(0);
        PythonLikeType sequenceType = sequence.__getType();
        if (sequenceType.__getAttributeOrNull(PythonUnaryOperator.REVERSED.getDunderMethod()) != null) {
            return UnaryDunderBuiltin.REVERSED.invoke(sequence);
        }

        if (sequenceType.__getAttributeOrNull(PythonUnaryOperator.LENGTH.getDunderMethod()) != null &&
                sequenceType.__getAttributeOrNull(PythonBinaryOperators.GET_ITEM.getDunderMethod()) != null) {
            PythonInteger length = (PythonInteger) UnaryDunderBuiltin.LENGTH.invoke(sequence);
            Iterator<PythonLikeObject> reversedIterator = new Iterator<>() {
                PythonInteger current = length.subtract(PythonInteger.ONE);

                @Override
                public boolean hasNext() {
                    return current.compareTo(PythonInteger.ZERO) >= 0;
                }

                @Override
                public PythonLikeObject next() {
                    PythonLikeObject out = BinaryDunderBuiltin.GET_ITEM.invoke(sequence, current);
                    current = current.subtract(PythonInteger.ONE);
                    return out;
                }
            };

            return new PythonIterator(reversedIterator);
        }

        throw new ValueError(sequenceType + " does not has a __reversed__ method and does not implement the Sequence protocol");
    }

    public static PythonLikeObject round(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (!(positionalArgs.size() == 1 || positionalArgs.size() == 2)) {
            throw new ValueError("round() expects 1 or 2 arguments, got " + positionalArgs.size());
        }

        PythonLikeObject number = positionalArgs.get(0);
        PythonLikeType numberType = number.__getType();
        if (numberType.__getAttributeOrNull("__round__") != null) {
            return ((PythonLikeFunction) numberType.__getAttributeOrNull("__round__")).__call__(positionalArgs, keywordArgs);
        }

        throw new ValueError(numberType + " does not has a __round__ method");
    }

    public static PythonLikeObject setattr(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        PythonLikeObject object;
        PythonString name;
        PythonLikeObject value;

        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        if (positionalArgs.size() == 3) {
            object = positionalArgs.get(0);
            name = (PythonString) positionalArgs.get(1);
            value = positionalArgs.get(2);
        } else if (positionalArgs.size() == 2 && keywordArgs.containsKey(PythonString.valueOf("value"))) {
            object = positionalArgs.get(0);
            name = (PythonString) positionalArgs.get(1);
            value = keywordArgs.get(PythonString.valueOf("value"));
        } else if (positionalArgs.size() == 1 && keywordArgs.containsKey(PythonString.valueOf("name")) &&
                keywordArgs.containsKey(PythonString.valueOf("value"))) {
            object = positionalArgs.get(0);
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
            value = keywordArgs.get(PythonString.valueOf("value"));
        } else if (positionalArgs.size() == 0 && keywordArgs.containsKey(PythonString.valueOf("object")) &&
                keywordArgs.containsKey(PythonString.valueOf("name")) &&
                keywordArgs.containsKey(PythonString.valueOf("value"))) {
            object = keywordArgs.get(PythonString.valueOf("object"));
            name = (PythonString) keywordArgs.get(PythonString.valueOf("name"));
            value = keywordArgs.get(PythonString.valueOf("value"));
        } else {
            throw new ValueError("setattr expects 2 or 3 arguments, got " + positionalArgs.size());
        }

        return TernaryDunderBuiltin.SETATTR.invoke(object, name, value);
    }

    public static PythonLikeObject sorted(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        PythonLikeObject iterable = positionalArgs.get(0);

        boolean isReversed = false;
        if (keywordArgs.containsKey(PythonString.valueOf("reverse"))) {
            isReversed = ((PythonBoolean) keywordArgs.get(PythonString.valueOf("reverse"))).getBooleanValue();
        }

        PythonLikeList out = new PythonLikeList();
        if (iterable instanceof Collection) {
            out.addAll((Collection) iterable);
        } else {
            Iterator<PythonLikeObject> iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR.invoke(iterable);
            iterator.forEachRemaining(out::add);
        }

        Comparator keyComparator = isReversed ? Comparator.reverseOrder() : Comparator.naturalOrder();
        List<KeyTuple> decoratedList = null;

        if (keywordArgs.containsKey(PythonString.valueOf("key"))) {
            PythonLikeObject key = keywordArgs.get(PythonString.valueOf("key"));
            if (key != PythonNone.INSTANCE) {
                final PythonLikeFunction keyFunction = (PythonLikeFunction) key;
                final Function keyExtractor = item -> keyFunction.__call__(List.of((PythonLikeObject) item), null);
                decoratedList = new ArrayList<>(out.size());
                for (int i = 0; i < out.size(); i++) {
                    decoratedList.add(
                            new KeyTuple((PythonLikeObject) keyExtractor.apply(out.get(i)), i, (PythonLikeObject) out.get(i)));
                }
            } else {
                keyComparator = isReversed ? Comparator.reverseOrder() : Comparator.naturalOrder();
            }
        } else {
            keyComparator = isReversed ? Comparator.reverseOrder() : Comparator.naturalOrder();
        }

        if (decoratedList != null) {
            Collections.sort(decoratedList, keyComparator);
            out.clear();
            for (KeyTuple keyTuple : decoratedList) {
                out.add(keyTuple.source);
            }
        } else {
            Collections.sort(out, keyComparator);
        }

        return out;
    }

    public static PythonLikeObject sum(List<PythonLikeObject> positionalArgs, Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();

        PythonLikeObject iterable;
        PythonLikeObject start;

        if (positionalArgs.size() == 2) {
            iterable = positionalArgs.get(0);
            start = positionalArgs.get(1);
        } else if (positionalArgs.size() == 1) {
            iterable = positionalArgs.get(0);
            start = keywordArgs.getOrDefault(PythonString.valueOf("start"), PythonInteger.ZERO);
        } else if (positionalArgs.size() == 0) {
            iterable = keywordArgs.get(PythonString.valueOf("iterable"));
            start = keywordArgs.getOrDefault(PythonString.valueOf("start"), PythonInteger.ZERO);
        } else {
            throw new ValueError("sum() expects 1 or 2 arguments, got " + positionalArgs.size());
        }

        PythonLikeObject current = start;

        Iterator<PythonLikeObject> iterator = (Iterator<PythonLikeObject>) UnaryDunderBuiltin.ITERATOR.invoke(iterable);
        while (iterator.hasNext()) {
            PythonLikeObject item = iterator.next();
            current = BinaryDunderBuiltin.ADD.invoke(current, item);
        }

        return current;
    }

    public static PythonLikeObject vars(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        if (positionalArgs.isEmpty()) {
            throw new ValueError("0-argument version of vars is not supported when executed in Java bytecode");
        }

        return positionalArgs.get(0).__getAttributeOrError("__dict__");
    }

    public static PythonIterator zip(List<PythonLikeObject> positionalArgs,
            Map<PythonString, PythonLikeObject> keywordArgs) {
        keywordArgs = (keywordArgs != null) ? keywordArgs : Map.of();
        List<PythonLikeObject> iterableList = positionalArgs;
        boolean isStrict = false;

        if (keywordArgs.containsKey(PythonString.valueOf("strict"))) {
            isStrict = ((PythonBoolean) keywordArgs.get(PythonString.valueOf("strict"))).getBooleanValue();
        }

        final List<Iterator> iteratorList = new ArrayList<>(iterableList.size());

        for (PythonLikeObject iterable : iterableList) {
            Iterator iterator;
            if (iterable instanceof Collection) {
                iterator = ((Collection) iterable).iterator();
            } else if (iterable instanceof Iterator) {
                iterator = (Iterator) iterable;
            } else {
                iterator = (Iterator) UnaryDunderBuiltin.ITERATOR.invoke(iterable);
            }
            iteratorList.add(iterator);
        }

        final boolean isStrictFinal = isStrict;

        if (iteratorList.isEmpty()) {
            // Return an empty iterator if there are no iterators
            return new PythonIterator(iteratorList.iterator());
        }

        Iterator<List<PythonLikeObject>> iteratorIterator = new Iterator<List<PythonLikeObject>>() {
            @Override
            public boolean hasNext() {
                if (isStrictFinal) {
                    int firstWithoutNext = -1;
                    int firstWithNext = -1;
                    for (int i = 0; i < iteratorList.size(); i++) {
                        if (iteratorList.get(i).hasNext() && firstWithNext == -1) {
                            firstWithNext = i;
                        } else if (!iteratorList.get(i).hasNext() && firstWithoutNext == -1) {
                            firstWithoutNext = i;
                        }

                        if (firstWithNext != -1 && firstWithoutNext != -1) {
                            throw new ValueError(
                                    "zip() argument " + firstWithNext + " longer than argument " + firstWithoutNext);
                        }
                    }
                    return firstWithoutNext == -1;
                } else {
                    return iteratorList.stream().allMatch(Iterator::hasNext);
                }
            }

            @Override
            public List<PythonLikeObject> next() {
                PythonLikeTuple out = new PythonLikeTuple();
                for (Iterator iterator : iteratorList) {
                    out.add((PythonLikeObject) iterator.next());
                }
                return out;
            }
        };

        return new PythonIterator(iteratorIterator);
    }

    public static PythonLikeFunction importFunction(PythonInterpreter pythonInterpreter) {
        return (positionalArguments, namedArguments) -> {
            namedArguments = (namedArguments) != null ? namedArguments : Map.of();

            PythonString name;
            PythonLikeDict globals;
            PythonLikeDict locals;
            PythonLikeTuple fromlist;
            PythonInteger level;

            if (positionalArguments.size() == 0) {
                name = (PythonString) namedArguments.get(PythonString.valueOf("name"));
                if (name == null) {
                    throw new ValueError("name is required for __import__()");
                }
                globals = (PythonLikeDict) namedArguments.getOrDefault(PythonString.valueOf("globals"), new PythonLikeDict());
                locals = (PythonLikeDict) namedArguments.getOrDefault(PythonString.valueOf("locals"), new PythonLikeDict());
                fromlist =
                        (PythonLikeTuple) namedArguments.getOrDefault(PythonString.valueOf("fromlist"), new PythonLikeTuple());
                level = (PythonInteger) namedArguments.getOrDefault(PythonString.valueOf("level"), PythonInteger.ZERO);
            } else if (positionalArguments.size() == 1) {
                name = (PythonString) positionalArguments.get(0);
                globals = (PythonLikeDict) namedArguments.getOrDefault(PythonString.valueOf("globals"), new PythonLikeDict());
                locals = (PythonLikeDict) namedArguments.getOrDefault(PythonString.valueOf("locals"), new PythonLikeDict());
                fromlist =
                        (PythonLikeTuple) namedArguments.getOrDefault(PythonString.valueOf("fromlist"), new PythonLikeTuple());
                level = (PythonInteger) namedArguments.getOrDefault(PythonString.valueOf("level"), PythonInteger.ZERO);
            } else if (positionalArguments.size() == 2) {
                name = (PythonString) positionalArguments.get(0);
                globals = (PythonLikeDict) positionalArguments.get(1);
                locals = (PythonLikeDict) namedArguments.getOrDefault(PythonString.valueOf("locals"), new PythonLikeDict());
                fromlist =
                        (PythonLikeTuple) namedArguments.getOrDefault(PythonString.valueOf("fromlist"), new PythonLikeTuple());
                level = (PythonInteger) namedArguments.getOrDefault(PythonString.valueOf("level"), PythonInteger.ZERO);
            } else if (positionalArguments.size() == 3) {
                name = (PythonString) positionalArguments.get(0);
                globals = (PythonLikeDict) positionalArguments.get(1);
                locals = (PythonLikeDict) positionalArguments.get(2);
                fromlist =
                        (PythonLikeTuple) namedArguments.getOrDefault(PythonString.valueOf("fromlist"), new PythonLikeTuple());
                level = (PythonInteger) namedArguments.getOrDefault(PythonString.valueOf("level"), PythonInteger.ZERO);
            } else if (positionalArguments.size() == 4) {
                name = (PythonString) positionalArguments.get(0);
                globals = (PythonLikeDict) positionalArguments.get(1);
                locals = (PythonLikeDict) positionalArguments.get(2);
                fromlist = (PythonLikeTuple) positionalArguments.get(3);
                level = (PythonInteger) namedArguments.getOrDefault(PythonString.valueOf("level"), PythonInteger.ZERO);
            } else if (positionalArguments.size() == 5) {
                name = (PythonString) positionalArguments.get(0);
                globals = (PythonLikeDict) positionalArguments.get(1);
                locals = (PythonLikeDict) positionalArguments.get(2);
                fromlist = (PythonLikeTuple) positionalArguments.get(3);
                level = (PythonInteger) positionalArguments.get(4);
            } else {
                throw new ValueError("__import__ expects 1 to 5 arguments, got " + positionalArguments.size());
            }

            Map<String, PythonLikeObject> stringGlobals = new HashMap<>();
            Map<String, PythonLikeObject> stringLocals = new HashMap<>();

            for (PythonLikeObject key : globals.keySet()) {
                stringGlobals.put(((PythonString) key).value, globals.get(key));
            }

            for (PythonLikeObject key : locals.keySet()) {
                stringLocals.put(((PythonString) key).value, globals.get(key));
            }

            return pythonInterpreter.importModule(level, (List) fromlist, stringGlobals, stringLocals, name.value);
        };
    }

    private final static class KeyTuple implements Comparable<KeyTuple> {
        final PythonLikeObject key;
        final int index;
        final PythonLikeObject source;

        public KeyTuple(PythonLikeObject key, int index, PythonLikeObject source) {
            this.key = key;
            this.index = index;
            this.source = source;
        }

        @Override
        public int compareTo(KeyTuple other) {
            PythonBoolean result = (PythonBoolean) BinaryDunderBuiltin.LESS_THAN.invoke(key, other.key);
            if (result.getBooleanValue()) {
                return -1;
            }

            result = (PythonBoolean) BinaryDunderBuiltin.LESS_THAN.invoke(other.key, key);
            if (result.getBooleanValue()) {
                return 1;
            }

            return index - other.index;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) {
                return true;
            }
            if (o == null || getClass() != o.getClass()) {
                return false;
            }
            KeyTuple keyTuple = (KeyTuple) o;
            return index == keyTuple.index && key.equals(keyTuple.key);
        }

        @Override
        public int hashCode() {
            return Objects.hash(key, index);
        }
    }
}
