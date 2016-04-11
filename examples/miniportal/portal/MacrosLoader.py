import os
import glob
import imp
from portal import Page

class Macro(object):
    pass

class MacrosLoader(object):
    def __init__(self, path):
        self.path = path
        self.macros = None

    def load_macros(self, blueprint, actors):
        self.actors = actors
        for macro in os.listdir(self.path):
            if not self.is_valid(macro):
                continue
            macro_path = os.path.join(self.path, macro)
            module = imp.load_source(macro[:-3], macro_path)
            blueprint.add_app_template_global(self.getCallback(getattr(module, macro[:-3])), macro[:-3])
            # app.add_template_global(getattr(module, macro[:-3]), macro[:-3])
    def is_valid(self, macro):
        if macro.startswith("__"):
            return False
        return True


    def getCallback(self, fn):
        def wrapper(*args, **kwargs):
            return fn(self.actors, *args, **kwargs)
        return wrapper