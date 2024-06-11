package ai.timefold.solver.python;

import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;

public class DaemonThreadFactory implements ThreadFactory {
    private static final ThreadFactory THREAD_FACTORY = Executors.defaultThreadFactory();

    @Override
    public Thread newThread(Runnable runnable) {
        Thread out = THREAD_FACTORY.newThread(runnable);
        out.setDaemon(true);
        return out;
    }
}
