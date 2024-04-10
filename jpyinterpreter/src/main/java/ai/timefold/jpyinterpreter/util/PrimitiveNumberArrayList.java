package ai.timefold.jpyinterpreter.util;

import java.lang.reflect.Array;
import java.util.AbstractList;

public class PrimitiveNumberArrayList<T extends Comparable<T>> extends AbstractList<T> {
    final Object backingArray;

    public PrimitiveNumberArrayList(Object backingArray) {
        this.backingArray = backingArray;
    }

    @Override
    @SuppressWarnings("unchecked")
    public T get(int i) {
        return (T) Array.get(backingArray, i);
    }

    @Override
    public int size() {
        return Array.getLength(backingArray);
    }
}
