package ai.timefold.jpyinterpreter.util;

import java.util.List;

public record ComparableFixedList<T extends Comparable<T>>(List<T> items) implements Comparable<ComparableFixedList<T>> {
    @SafeVarargs
    public ComparableFixedList(T... items) {
        this(List.of(items));
    }

    @Override
    public int compareTo(ComparableFixedList<T> other) {
        int commonSize = Math.min(items.size(), other.items.size());
        for (int i = 0; i < commonSize; i++) {
            var result = items.get(i).compareTo(other.items.get(i));
            if (result != 0) {
                return result;
            }
        }
        return items.size() - other.items.size();
    }
}
