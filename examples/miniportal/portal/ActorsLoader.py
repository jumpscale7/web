import yaml
import glob
import os
import imp

class Actors(object):
    def __init__(self):
        pass

    pass


# all_actors = Actors()


def isValid(dir):
    return dir not in ('__pycache__',)


empty = object()


class Parameter(object):
    def __init__(self, name, type, default=empty):
        self.name = name
        self.type = type
        self.default = default

    def _get_default(self):
        if isinstance(self.default, str):
            return "'%s'" % self.default

        return self.default

    def __str__(self):
        param = self.name
        if self.default != empty:
            param = '%s=%s' % (param, self._get_default())
        return param


method_temple = '''\
from JumpScale import j

def {method}({params}):
    raise NotImplemented()
'''


class ActorsLoader(object):
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path

    def load_actors(self):
        self.all_actors = Actors()
        for namespace in os.listdir(self.path):
            ns_actors = Actors()
            if not isValid(namespace):
                continue
            ns_path = os.path.join(self.path, namespace)
            if not os.path.isdir(ns_path):
                continue
            for object in os.listdir(ns_path):
                if not isValid(object):
                    continue
                obj_path = os.path.join(ns_path, object)
                if not os.path.isdir(obj_path):
                    continue
                actors = self._load_actors(glob.glob(os.path.join(obj_path, '*.yaml')), namespace, object)
                setattr(ns_actors, object, actors)

            setattr(self.all_actors, namespace, ns_actors)

        return self.all_actors

    def _load_actors(self, spec_files, namespace, obj):
        obj_actors = Actors()
        for file in spec_files:
            with open(file) as f:
                specs = yaml.load(f)
                for method in specs.keys():
                    actor = "{method}.py".format(method=method)
                    actor_file = os.path.join(self.path, namespace, obj, actor)
                    if not os.path.isfile(actor_file):
                        self._generate_actor(namespace, obj, method, specs[method])

                    module = self._load_actor(namespace, obj, method)
                    if not hasattr(module, method):
                        raise Exception('file "%s" does not have method "%s"' % (actor_file, method))
                    fn = getattr(module, method)
                    fn.specs = specs[method]
                    setattr(obj_actors, method, fn)
                    # setattr(obj_actors, method, getattr(module, method))
                    # self.generate_route(app, namespace, obj, method, getattr(obj_actors, method))
        return obj_actors

    def _load_actor(self, namespace, obj, method):
        module_name = "{namespace}.{obj}.{method}".format(namespace=namespace, obj=obj, method=method)
        module_path = os.path.join(self.path, namespace, obj, "%s.py" % method)
        return imp.load_source(module_name, module_path)

    def _generate_actor(self, namespace, obj, method, specs):
        self.is_valid_specs(specs)
        parameters = map(lambda p: str(Parameter(**p)), specs.get("parameters", []))
        param = ', '.join(parameters)

        with open(os.path.join(self.path, namespace, obj, '%s.py' % method), 'w') as f:
            templ = method_temple.format(method=method, params=param)
            f.write(templ)

    def generate_route(self, app, namespace, obj, method, view):
        route = "{namespace}/{obj}/{method}".format(namespace=namespace, obj=obj, method=method)
        app.add_url_rule('/{route}'.format(route=route), method, view)

    def is_valid_specs(self, specs):
        params = specs.get("parameters", [])
        has_default = False
        for param in params:
            if not param.get("default") and has_default:
                raise InvalidParamtersExceptions("none-keyword arg after keyword args %s" % params)
            else:
                has_default = True


class InvalidParamtersExceptions(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
