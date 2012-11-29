import AccessControl.SecurityInfo
from AccessControl.SecurityInfo import ModuleSecurityInfo


def allow_module(module_name):
    """Allow a module and all its contents to be used from a
    restricted Script. The argument module_name may be a simple
    or dotted module or package name. Note that if a package
    path is given, all modules in the path will be available."""
    ModuleSecurityInfo(module_name).setDefaultAccess(1)
    ModuleSecurityInfo(module_name).declarePrivate('allow_module')
    dot = module_name.find('.')
    while dot > 0:
        ModuleSecurityInfo(module_name[:dot]).setDefaultAccess(1)
        ModuleSecurityInfo(module_name).declarePrivate('allow_module')
        dot = module_name.find('.', dot + 1)
AccessControl.allow_module = AccessControl.SecurityInfo.allow_module = allow_module
