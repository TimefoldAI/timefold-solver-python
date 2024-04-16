from .._jpype_type_conversions import PythonBiFunction
from typing import Awaitable, TypeVar, TYPE_CHECKING
from asyncio import Future, get_event_loop, CancelledError

if TYPE_CHECKING:
    from java.util.concurrent import (Future as JavaFuture,
                                      CompletableFuture as JavaCompletableFuture)


Result = TypeVar('Result')


def wrap_future(future: 'JavaFuture[Result]') -> Awaitable[Result]:
    async def get_result() -> Result:
        nonlocal future
        return future.get()

    return get_result()


def wrap_completable_future(future: 'JavaCompletableFuture[Result]') -> Future[Result]:
    loop = get_event_loop()
    out = loop.create_future()

    def result_handler(result, error):
        nonlocal out
        if error is not None:
            out.set_exception(error)
        else:
            out.set_result(result)

    def cancel_handler(python_future: Future):
        nonlocal future
        if isinstance(python_future.exception(), CancelledError):
            future.cancel(True)

    future.handle(PythonBiFunction(result_handler))
    out.add_done_callback(cancel_handler)
    return out


__all__ = ['wrap_future', 'wrap_completable_future']
