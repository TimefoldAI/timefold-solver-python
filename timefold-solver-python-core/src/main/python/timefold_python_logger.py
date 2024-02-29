import logging

__original_logging_class = logging.getLoggerClass()


class TimefoldLogger(__original_logging_class):
    def __init__(self, name):
        super().__init__(name)
        subpackage = name[len('timefold.solver'):]
        self.java_logger_name = f'ai.timefold{subpackage}'

    def setLevel(self, level):
        from ai.timefold.solver.python.logging import PythonLoggingToLogbackAdapter
        PythonLoggingToLogbackAdapter.setLevel(self.java_logger_name, level)

    def isEnabledFor(self, level):
        from ai.timefold.solver.python.logging import PythonLoggingToLogbackAdapter
        PythonLoggingToLogbackAdapter.isEnabledFor(self.java_logger_name, level)

    def getEffectiveLevel(self):
        from ai.timefold.solver.python.logging import PythonLoggingToLogbackAdapter
        PythonLoggingToLogbackAdapter.getEffectiveLevel(self.java_logger_name)

    def getChild(self, suffix):
        return TimefoldLogger(f'{self.name}.{suffix}')

    def addFilter(self, filter):
        raise NotImplementedError(f'Cannot add filter to {self.java_logger_name} logger')

    def removeFilter(self, filter):
        raise NotImplementedError(f'Cannot remove filter from {self.java_logger_name} logger')

    def addHandler(self, hdlr):
        raise NotImplementedError(f'Cannot add handler to {self.java_logger_name} logger')

    def removeHandler(self, hdlr):
        raise NotImplementedError(f'Cannot remove handler from {self.java_logger_name} logger')


logging.setLoggerClass(TimefoldLogger)
timefold_logger = logging.getLogger('timefold.solver')
logging.setLoggerClass(__original_logging_class)
