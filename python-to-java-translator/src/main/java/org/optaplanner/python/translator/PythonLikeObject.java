package org.optaplanner.python.translator;

import org.optaplanner.python.translator.types.PythonLikeType;
import org.optaplanner.python.translator.types.errors.AttributeError;

/**
 * Represents an Object that can be interacted with like a Python Object.
 * A PythonLikeObject can refer to a Java Object, a CPython Object, or
 * be an Object constructed by the Java Python Interpreter.
 */
public interface PythonLikeObject {

    /**
     * Gets an attribute by name.
     *
     * @param attributeName Name of the attribute to get
     * @return The attribute of the object that corresponds with attributeName
     * @throws AttributeError if the attribute does not exist
     */
    PythonLikeObject __getAttributeOrNull(String attributeName);

    /**
     * Gets an attribute by name.
     *
     * @param attributeName Name of the attribute to get
     * @return The attribute of the object that corresponds with attributeName
     * @throws AttributeError if the attribute does not exist
     */
    default PythonLikeObject __getAttributeOrError(String attributeName) {
        PythonLikeObject out = this.__getAttributeOrNull(attributeName);
        if (out == null) {
            throw new AttributeError("object '" + this + "' does not have attribute '" + attributeName + "'");
        }
        return out;
    }

    /**
     * Sets an attribute by name.
     *
     * @param attributeName Name of the attribute to set
     * @param value Value to set the attribute to
     */
    void __setAttribute(String attributeName, PythonLikeObject value);

    /**
     * Delete an attribute by name.
     *
     * @param attributeName Name of the attribute to delete
     */
    void __deleteAttribute(String attributeName);

    /**
     * Returns the type describing the object
     *
     * @return the type describing the object
     */
    PythonLikeType __getType();
}
