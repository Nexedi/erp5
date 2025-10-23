class ComponentPackage(ModuleType):
  """
  TODO: Do we really need ComponentVersionPackage?
  """
  __path__ = []

class ComponentVersionPackage(ComponentPackage):
  """
  Component Version package (erp5.component.XXX.VERSION)

  TODO: Do we really need ComponentVersionPackage?
  """
  pass

class ComponentDynamicPackage(ComponentPackage):
  def reset(self, sub_package=None):
    """
    Reset the content of the current package and its version package as well
    recursively. This method must be called within a lock to avoid side
    effects
    """
    if sub_package:
      package = sub_package
    else:
      # Clear the source code dict only once
      self.__fullname_source_code_dict.clear()
      package = self

      # Force reload of ModuleSecurityInfo() as it may have been changed in
      # the source code
      for modsec_dict in _moduleSecurity, _appliedModuleSecurity:
        for k in ensure_list(modsec_dict.keys()):
          if k.startswith(self.__name__):
            del modsec_dict[k]
      for k, v in ensure_list(MNAME_MAP.items()):
        if v.startswith(self.__name__):
          del MNAME_MAP[k]

          # Products import compatibility (module_fullname_filesystem)
          if k.startswith('Products.'):
            del sys.modules[k]

    for name, module in ensure_list(package.__dict__.items()):
      if name[0] == '_' or not isinstance(module, ModuleType):
        continue

      # Reset the content of the version package before resetting it
      elif isinstance(module, ComponentVersionPackage):
        self.reset(sub_package=module)

      module_name = package.__name__ + '.' + name
      LOG("ERP5Type.Tool.ComponentTool", BLATHER, "Resetting " + module_name)

      # The module must be deleted first from sys.modules to avoid imports in
      # the meantime
      del sys.modules[module_name]

      delattr(package, name)

class ToolComponentDynamicPackage(ComponentDynamicPackage):
  def reset(self, *args, **kw):
    """
    Reset CMFCore list of Tools (manage_addToolForm)
    """
    import Products.ERP5
    toolinit = Products.ERP5.__FactoryDispatcher__.toolinit
    reset_tool_set = set()
    for tool in toolinit.tools:
      if not tool.__module__.startswith(self._namespace_prefix):
        reset_tool_set.add(tool)
    toolinit.tools = reset_tool_set

    super(ToolComponentDynamicPackage, self).reset(*args, **kw)

COMPONENT_PACKAGE_NAMESPACE_CLASS_DICT = {
  'erp5.component.module': ComponentDynamicPackage,
  'erp5.component.extension': ComponentDynamicPackage,
  'erp5.component.document': ComponentDynamicPackage,
  'erp5.component.interface': ComponentDynamicPackage,
  'erp5.component.mixin' ComponentDynamicPackage,
  'erp5.component.test': ComponentDynamicPackage,
  'erp5.component.tool': ToolComponentDynamicPackage,
}

_VERSION_SUFFIX_LEN = len('_version')

from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from Products.ERP5.ERP5Site import getSite
from Acquisition import aq_base
class ComponentMetaPathFinder(MetaPathFinder):
  def find_spec(self, fullname, path, target=None):
    if path:
      # Filesystem-based import backward-compatibility
      import erp5.component
      try:
        fullname = erp5.component.filesystem_import_dict.get(fullname, '')
      except AttributeError: # filesystem_import_dict may not exist yet during bootstrap
        return None

    namespace = fullname.rsplit('.', 3)
    if namespace not in COMPONENT_PACKAGE_NAMESPACE_CLASS_DICT:
      return None

    site = getSite()

    namespace_prefix = namespace + '.'
    id_prefix = namespace.rsplit('.', 1)[1]

    # __import__ will first try a relative import, for example
    # erp5.component.XXX.YYY.ZZZ where erp5.component.XXX.YYY is the current
    # Component where an import is done
    name = fullname[len(namespace_prefix):]
    # name=VERSION_version.REFERENCE
    if '.' in name:
      try:
        version, name = name.split('.')
        version = version[:-__VERSION_SUFFIX_LEN]
      except ValueError:
        return None

      id_ = "%s.%s.%s" % (id_prefix, version, name)
      # aq_base() because this should not go up to ERP5Site and trigger
      # side-effects, after all this only check for existence...
      component = getattr(aq_base(site.portal_components), id_, None)
      if component is None or component.getValidationState() not in ('modified',
                                                                     'validated'):
        return None

    # Skip unavailable components, otherwise Products for example could be
    # wrongly considered as importable and thus the actual filesystem class
    # ignored
    #
    # name=VERSION_version
    elif name.endswith('_version'):
      if name[:-__VERSION_SUFFIX_LEN] not in site.getVersionPriorityNameList():
        return None

    # name=REFERENCE
    else:
      component_tool = aq_base(site.portal_components)
      for version in site.getVersionPriorityNameList():
        id_ = "%s.%s.%s" % (id_prefix, version, name)
        component = getattr(component_tool, id_, None)
        if component is not None and component.getValidationState() in ('modified',
                                                                        'validated'):
          break
      else:
        return None

    spec = ModuleSpec(fullname, loader)

    return spec
