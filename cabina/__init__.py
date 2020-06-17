from ._computed import computed
from ._core import Config, MetaBase, Section
from ._environment import Environment
from ._future_value import FutureValue
from ._version import version

__version__ = version
__all__ = ("Config", "Section", "computed",
           "env", "Environment", "FutureValue",
           "MetaBase",)

env: Environment = Environment()
