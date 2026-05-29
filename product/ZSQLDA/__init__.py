from contextlib import contextmanager
import importlib, sys

_SUB_PROXIES = ('db', 'DA')

def _install(module_name):
    def configure(backend_path):
        backend = importlib.import_module(backend_path)
        m = sys.modules[module_name]
        for k, v in vars(backend).items():
            if not k.startswith('_'):
                setattr(m, k, v)
    sys.modules[module_name].configure = configure

def configure(backend):
    # backend: full module path, e.g. 'Products.ZMySQLDA', 'Products.ZSQLiteDA'
    for sub in _SUB_PROXIES:
        importlib.import_module(__name__ + '.' + sub).configure(backend + '.' + sub)

@contextmanager
def configured(backend):
    saved = []
    for sub in _SUB_PROXIES:
        m = importlib.import_module(__name__ + '.' + sub)
        saved.append((m, dict(vars(m))))
    configure(backend)
    try:
        yield
    finally:
        for m, saved_dict in saved:
            d = vars(m)
            for k in list(d):
                if k not in saved_dict:
                    del d[k]
            d.update(saved_dict)
