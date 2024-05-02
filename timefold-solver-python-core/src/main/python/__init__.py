"""
This module wraps Timefold and allow Python Objects
to be used as the domain and Python functions to be used
as the constraints.

Using any decorators in this module will automatically start
the JVM. If you want to pass custom arguments to the JVM,
use init before decorators and any timefold.solver.types imports.
"""
from ._problem_change import *
from ._solution_manager import *
from ._solver import *
from ._solver_factory import *
from ._solver_manager import *

import timefold.solver.domain as domain
import timefold.solver.config as config
import timefold.solver.score as score
import timefold.solver.test as test

from ._timefold_java_interop import init, set_class_output_directory
