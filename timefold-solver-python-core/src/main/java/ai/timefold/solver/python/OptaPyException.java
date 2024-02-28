package ai.timefold.solver.python;

public class OptaPyException extends RuntimeException {

    public OptaPyException(String message) {
        super(message);
    }

    public OptaPyException(String message, Throwable cause) {
        super(message, cause);
    }

}
