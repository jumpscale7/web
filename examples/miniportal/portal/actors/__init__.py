class Actors(object):
    def __init__(self):
        pass
    pass

# Load actors
import os
import importlib.util

path = os.path.dirname(os.path.abspath(__file__))

all_actors = Actors()
for subdir, dirs, files in os.walk(path):
    for file in files:
        mod = file[:-3]
        if not file.endswith("py") or file == "__init__.py":
            continue
        spec = importlib.util.spec_from_file_location(mod, os.path.join(subdir, file))

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        setattr(all_actors, mod, module)
