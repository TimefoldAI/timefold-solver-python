from .conftest import verifier_for

def test_function_traceback():
    def my_function_1():
        my_function_2()

    def my_function_2():
        raise Exception('Message')

    def check_traceback(error: Exception):
        from traceback import format_exception
        traceback = '\n'.join(format_exception(type(error), error, error.__traceback__))
        if 'test_traceback.py", line 5, in my_function_1\n' not in traceback:
            return False

        if 'test_traceback.py", line 8, in my_function_2\n' not in traceback:
            return False

        if not traceback.strip().endswith('Exception: Message'):
            return False

        if 'File "PythonException.java"' in traceback:
            return False

        return True

    verifier = verifier_for(my_function_1)
    verifier.verify_error_property(predicate=check_traceback)
