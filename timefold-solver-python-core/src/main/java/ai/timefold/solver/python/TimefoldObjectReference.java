package ai.timefold.solver.python;

import java.util.Objects;

import ai.timefold.jpyinterpreter.PythonLikeObject;
import ai.timefold.jpyinterpreter.types.PythonLikeType;

public class TimefoldObjectReference implements PythonLikeObject {
    final long id;

    public TimefoldObjectReference(long id) {
        this.id = id;
    }

    public long getId() {
        return id;
    }

    @Override
    public PythonLikeObject __getAttributeOrNull(String attributeName) {
        return null;
    }

    @Override
    public void __setAttribute(String attributeName, PythonLikeObject value) {

    }

    @Override
    public void __deleteAttribute(String attributeName) {

    }

    @Override
    public PythonLikeType __getType() {
        return null;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        TimefoldObjectReference that = (TimefoldObjectReference) o;
        return id == that.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "TimefoldObjectReference{" +
                "id=" + id +
                '}';
    }
}
