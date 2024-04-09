from ..timefold_java_interop import get_class
from typing import TYPE_CHECKING, Type, TypeVar, cast
if TYPE_CHECKING:
    import jpype.imports  # noqa
    from ai.timefold.solver.core.api.score.stream import ConstraintFactory as _JavaConstraintFactory
    from ai.timefold.solver.core.api.score.stream.bi import BiJoiner


class ConstraintFactory:
    delegate: '_JavaConstraintFactory'
    A_ = TypeVar('A_')
    B_ = TypeVar('B_')
    C_ = TypeVar('C_')
    D_ = TypeVar('D_')
    E_ = TypeVar('E_')

    def __init__(self, delegate: '_JavaConstraintFactory'):
        self.delegate = delegate

    def get_default_constraint_package(self) -> str:
        """This is ConstraintConfiguration.constraintPackage() if available,
        otherwise the module of the @constraint_provider function

        :return:
        """
        return self.delegate.getDefaultConstraintPackage()

    def for_each(self, source_class: Type[A_]) -> 'UniConstraintStream[A_]':
        """Start a ConstraintStream of all instances of the source_class that are known as problem facts or
        planning entities.

        :param source_class:

        :return:
        """
        source_class = get_class(source_class)
        return UniConstraintStream(self.delegate.forEach(source_class), self.get_default_constraint_package(),
                                   cast(Type['A_'], source_class))

    def for_each_including_unassigned(self, source_class: Type[A_]) -> 'UniConstraintStream[A_]':
        """Start a ConstraintStream of all instances of the source_class that are known as problem facts or planning
        entities, without filtering of entities with unassigned planning variables.

        :param source_class:

        :return:
        """
        source_class = get_class(source_class)
        return UniConstraintStream(self.delegate.forEachIncludingUnassigned(source_class),
                                   self.get_default_constraint_package(),
                                   cast(Type['A_'], source_class))

    def for_each_unique_pair(self, source_class: Type[A_], *joiners: 'BiJoiner[A_, A_]') -> \
            'BiConstraintStream[A_, A_]':
        """Create a new BiConstraintStream for every unique combination of A and another A with a higher @planning_id
        that satisfies all specified joiners.

        :param source_class:

        :param joiners:

        :return:
        """
        source_class = get_class(source_class)
        return BiConstraintStream(self.delegate.forEachUniquePair(source_class,
                                                                  extract_joiners(joiners, source_class, source_class)),
                                  self.get_default_constraint_package(),
                                  cast(Type['A_'], source_class),
                                  cast(Type['A_'], source_class))


from .constraint_stream import *
from .joiners import extract_joiners

__all__ = [
    'ConstraintFactory'
]
