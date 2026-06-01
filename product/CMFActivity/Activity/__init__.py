import importlib, sys

_SUB_PROXIES = ('SQLBase', 'SQLDict', 'SQLJoblib')

def _install(module_name):
    def configure(backend_path):
        backend = importlib.import_module(backend_path)
        m = sys.modules[module_name]
        for k, v in vars(backend).items():
            if not k.startswith('_'):
                setattr(m, k, v)
    sys.modules[module_name].configure = configure

def configure(backend):
    # backend: full subpackage path, e.g. 'Products.CMFActivity.Activity.MySQL'.
    # SQLBase must be populated first because SQLQueue imports from it at
    # module load (and _SUB_PROXIES lists it first).
    for sub in _SUB_PROXIES:
        importlib.import_module(__name__ + '.' + sub).configure(backend + '.' + sub)
    from . import SQLDict, SQLJoblib, SQLQueue
    import Products.CMFActivity.ActivityTool as ActivityTool
    ActivityTool.activity_dict = {
        k: getattr(v, k)()
        for k, v in {'SQLDict': SQLDict, 'SQLQueue': SQLQueue, 'SQLJoblib': SQLJoblib}.items()}
