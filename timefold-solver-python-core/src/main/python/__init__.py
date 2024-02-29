"""
This module wraps Timefold and allow Python Objects
to be used as the domain and Python functions to be used
as the constraints.

Using any decorators in this module will automatically start
the JVM. If you want to pass custom arguments to the JVM,
use init before decorators and any timefold.solver.types imports.
"""

from .annotations import *
from .timefold_api_wrappers import *
from .timefold_java_interop import init, _planning_clone, set_class_output_directory
from .constraint_stream import BytecodeTranslation
