import importlib


def get_python_path(klass):
    return '%s.%s' % (klass.__module__, klass.__name__)


def get_object_from_python_path(python_path):
    parts = python_path.split('.')
    class_name = parts.pop(-1)
    mod_path = '.'.join(parts)
    mod = importlib.import_module(mod_path)
    return getattr(mod, class_name)
