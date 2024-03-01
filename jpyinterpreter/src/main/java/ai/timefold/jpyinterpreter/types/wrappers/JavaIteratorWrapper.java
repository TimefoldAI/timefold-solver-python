package ai.timefold.jpyinterpreter.types.wrappers;

import java.util.Iterator;

final class JavaIteratorWrapper implements Iterator<JavaObjectWrapper> {
    final Iterator<?> delegate;

    JavaIteratorWrapper(Iterator<?> delegate) {
        this.delegate = delegate;
    }

    @Override
    public boolean hasNext() {
        return delegate.hasNext();
    }

    @Override
    public JavaObjectWrapper next() {
        return new JavaObjectWrapper(delegate.next());
    }
}
