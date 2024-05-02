from typing import Callable, TypeVar
from .._timefold_java_interop import ensure_init, register_java_class

Origin_ = TypeVar('Origin_')
Destination_ = TypeVar('Destination_')


def nearby_distance_meter(distance_function: Callable[[Origin_, Destination_], float], /) \
        -> Callable[[Origin_, Destination_], float]:
    ensure_init()
    from jpyinterpreter import translate_python_bytecode_to_java_bytecode, generate_proxy_class_for_translated_function
    from ai.timefold.solver.core.impl.heuristic.selector.common.nearby import NearbyDistanceMeter  # noqa
    java_class = generate_proxy_class_for_translated_function(NearbyDistanceMeter,
                                                              translate_python_bytecode_to_java_bytecode(
                                                                  distance_function,
                                                                  NearbyDistanceMeter))
    return register_java_class(distance_function, java_class)


__all__ = ['nearby_distance_meter']
