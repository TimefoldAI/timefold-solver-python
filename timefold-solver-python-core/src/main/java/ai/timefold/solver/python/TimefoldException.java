package ai.timefold.solver.python;

public class TimefoldException extends RuntimeException {

    public TimefoldException(String message) {
        super(message);
    }

    public TimefoldException(String message, Throwable cause) {
        super(message, cause);
    }

}
