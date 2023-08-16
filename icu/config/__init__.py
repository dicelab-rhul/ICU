

from .utils import read_configpy_file
from . import default

from .distribution import Uniform, Normal

DEFAULT_CONFIGURATION = read_configpy_file(default.__file__)