package org.optaplanner.python.translator.types;

import java.util.Iterator;
import java.util.Map;

import org.optaplanner.python.translator.PythonLikeObject;
import org.optaplanner.python.translator.types.errors.StopIteration;

public class PythonIterator extends AbstractPythonLikeObject implements Iterator {
    public static final PythonLikeType ITERATOR_TYPE = new PythonLikeType("iterator", PythonIterator.class);
    private final Iterator delegate;

    static {
        ITERATOR_TYPE.__dir__.put("__next__",
                new UnaryLambdaReference((self) -> (PythonLikeObject) ((PythonIterator) self).next(), Map.of()));
    }

    public PythonIterator(Iterator delegate) {
        super(ITERATOR_TYPE);
        this.delegate = delegate;
    }

    @Override
    public boolean hasNext() {
        return delegate.hasNext();
    }

    @Override
    public Object next() {
        if (!delegate.hasNext()) {
            throw new StopIteration();
        }
        return delegate.next();
    }
}
