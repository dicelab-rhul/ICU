

from icu.ui import start



from icu.ui import config


from icu.config.utils import read_configpy_file
print(config.__file__)

WINDOW_DEFAULT_CONFIGURATION = read_configpy_file(config.__file__)
print(WINDOW_DEFAULT_CONFIGURATION)


ui_process = start(WINDOW_DEFAULT_CONFIGURATION)
ui_process.join()


