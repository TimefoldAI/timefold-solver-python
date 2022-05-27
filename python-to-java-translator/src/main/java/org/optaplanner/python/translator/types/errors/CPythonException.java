package org.optaplanner.python.translator.types.errors;

import java.util.List;

import org.optaplanner.python.translator.types.PythonLikeType;

/**
 * Python class for general exceptions. Equivalent to Java's {@link RuntimeException}
 */
public class CPythonException extends PythonException {
    final static PythonLikeType CPYTHON_EXCEPTION_TYPE =
            new PythonLikeType("CPython", CPythonException.class, List.of(PythonException.EXCEPTION_TYPE));

    public CPythonException() {
        super(CPYTHON_EXCEPTION_TYPE);
    }

    public CPythonException(String message) {
        super(CPYTHON_EXCEPTION_TYPE, message);
    }
}
