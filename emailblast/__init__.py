VERSION = (0, 0, 2,)
__version__ = '.'.join(map(str, VERSION))

def get_version():
    """
    Returns string with digit parts only.
    """
    return __version__ 

# Do not use Django settings at module level as recommended
try:
    from django.utils.functional import LazyObject
except ImportError:
    pass
else:
    class LazySettings(LazyObject):
        def _setup(self):
            from emailblast import default_settings
            self._wrapped = Settings(default_settings)

    class Settings(object):
        def __init__(self, settings_module):
            for setting in dir(settings_module):
                if setting == setting.upper():
                    setattr(self, setting, getattr(settings_module, setting))

    settings = LazySettings()
