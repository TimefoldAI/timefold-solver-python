"""
This module wraps Timefold and allow Python Objects
to be used as the domain and Python functions to be used
as the constraints.

Using any decorators in this module will automatically start
the JVM. If you want to pass custom arguments to the JVM,
use init before decorators and any timefold.solver.types imports.
"""
import timefold.solver.api as api
import timefold.solver.annotation as annotation
import timefold.solver.config as config
import timefold.solver.constraint as constraint
import timefold.solver.test as test
import timefold.solver.valuerange as valuerange

from .timefold_java_interop import init, set_class_output_directory

__all__ = [# Subpackages
           'api', 'annotation', 'config', 'constraint', 'test', 'valuerange',
           # Setup Functions
           'init', 'set_class_output_directory']
