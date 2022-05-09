# -*- coding: utf-8 -*-
#
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from __future__ import absolute_import
import sys

# TODO: make sure that trying to use it does not import isort, because the
#       latter hacks Python in order to execute:
#           sys.setdefaultencoding('utf-8')
#       This changes the behaviour of some ERP5 code.
sys.modules.setdefault('isort', None)

## All arguments are passed as arguments and this needlessly outputs a 'No
## config file found, using default configuration' message on stderr.
try:
    from logilab.common.configuration import OptionsManagerMixIn
except ImportError:
    # pylint 2.x (python3)
    from pylint.config import OptionsManagerMixIn
OptionsManagerMixIn.read_config_file = lambda *args, **kw: None

## Pylint transforms and plugin to generate AST for ZODB Components
from astroid.builder import AstroidBuilder
from astroid.exceptions import AstroidBuildingException
from astroid import MANAGER, node_classes

try:
  from astroid.builder import _guess_encoding
except ImportError:
  # XXX: With python3, tokenize.detect_encoding() is used instead. This
  # should do the same instead of copying/pasting legacy code...
  import re
  _ENCODING_RGX = re.compile(r"\s*#+.*coding[:=]\s*([-\w.]+)")
  def _guess_encoding(string):
      """get encoding from a python file as string or return None if not found"""
      # check for UTF-8 byte-order mark
      if string.startswith('\xef\xbb\xbf'):
          return 'UTF-8'
      for line in string.split('\n', 2)[:2]:
          # check for encoding declaration
          match = _ENCODING_RGX.match(line)
          if match is not None:
              return match.group(1)
def string_build(self, data, modname='', path=None):
    """
    build astroid from source code string and return rebuilded astroid

    Monkey patched to check encoding properly, as `file_build()` does:
      # `data` can only be an str (not unicode)
      module = self._data_build(data, modname, path)
      # But here it tries to `encode()` which will fails if there is any
      # non-ASCII character...
      module.file_bytes = data.encode('utf-8')
      return self._post_build(module, 'utf-8')
    """
    if isinstance(data, unicode):
	# When called internally by pylint/astroid and if the source code imports
	# `unicode_literals`, the source code may end up being an unicode object
	# (example: `infer_named_tuple()`)
        data = data.encode('utf-8')
    encoding = _guess_encoding(data)
    if encoding is None:
        # Encoding not defined in the source file, assuming utf-8...
        encoding = 'utf-8'
    try:
        # BytesIO() does not handle unicode:
        #   TypeError: 'unicode' does not have the buffer interface
        if isinstance(data, unicode):
            data = data.encode(encoding)
        else:
            # Just to avoid error later on...
            data.decode(encoding)
    except Exception as exc:
        from zLOG import LOG, WARNING
        LOG("Products.ERP5Type.patches.pylint", WARNING,
            "%s: Considered as not importable: Wrong encoding? (%r)" %
            (modname, exc))
        raise AstroidBuildingException(exc)
    module = self._data_build(data, modname, path)
    module.file_bytes = data
    module.source_code = data
    return self._post_build(module, encoding)
AstroidBuilder.string_build = string_build

# patch node_classes.const_factory not to fail on LazyModules that e.g.
# pygolang installs for pytest and ipython into sys.modules dict:
#
#   https://lab.nexedi.com/nexedi/pygolang/blob/pygolang-0.1-0-g7b72d41/golang/_patch/__init__.py
#   https://lab.nexedi.com/nexedi/pygolang/blob/pygolang-0.1-0-g7b72d41/golang/_patch/pytest_py2.py#L48-51
#   https://lab.nexedi.com/nexedi/pygolang/blob/pygolang-0.1-0-g7b72d41/golang/_patch/ipython_py2.py#L45-48
#
# if we don't patch and the module is not available, upon checking sys->sys.modules
# const_factory will fail with ImportError when accessing value.__class__.
node_classes_const_factory = node_classes.const_factory
def const_factory(value):
    typ = type(value)
    typename = ('%s.%s' % (typ.__module__, typ.__name__))
    if typename == 'peak.util.imports.LazyModule':
        # lazy module installed by Importing
        # see if we can load it, and return empty placehoder if the module is not available
        try:
            value.__class__
        except ImportError:
            node = node_classes.EmptyNode()
            node.object = None # not value
            return node
        # ok the module is available and is now loaded - continue via normal const_factory path
    return node_classes_const_factory(value)
node_classes.const_factory = const_factory

from astroid import nodes
def erp5_package_transform(node):
    """'
    erp5/' directory on the filesystem is different from 'erp5' module when
    running ERP5, so replace entirely this node completely to avoid pylint
    checking erp5/ directory structure for module and returns errors...
    """
    # Cannot call string_build() as this would be called again and again
    erp5_package_node = nodes.Module('erp5', None)
    erp5_package_node.package = True
    return erp5_package_node
MANAGER.register_transform(nodes.Module,
                           erp5_package_transform,
                           lambda n: n.name == 'erp5')

def _buildAstroidModuleFromComponentModuleName(modname):
    from Products.ERP5.ERP5Site import getSite
    from Acquisition import aq_base
    portal = getSite()
    component_tool = aq_base(portal.portal_components)
    component_obj = None
    component_id = modname[len('erp5.component.'):]
    if '_version' in modname:
        try:
            obj = getattr(component_tool,
                          component_id.replace('_version', '', 1))
        except AttributeError:
            raise AstroidBuildingException()
        if obj.getValidationState() in ('modified', 'validated'):
            component_obj = obj
        else:
            raise AstroidBuildingException()

    else:
        try:
            package, reference = component_id.split('.', 1)
        except ValueError:
            raise AstroidBuildingException()
        for version in portal.getVersionPriorityNameList():
            try:
                obj = getattr(component_tool,
                              '%s.%s.%s' % (package, version, reference))
            except AttributeError:
                continue

            if obj.getValidationState() in ('modified', 'validated'):
                version_modname = 'erp5.component.%s.%s_version.%s' % (package,
                                                                       version,
                                                                       reference)
                module = MANAGER.astroid_cache.get(
                    version_modname,
                    _buildAstroidModuleFromComponentModuleName(version_modname))
                MANAGER.astroid_cache[modname] = module
                return module

    if component_obj is None:
        raise AstroidBuildingException()

    # module_build() could also be used but this requires importing
    # the ZODB Component and also monkey-patch it to support PEP-302
    # for __file__ starting with '<'
    module = AstroidBuilder(MANAGER).string_build(
        component_obj.getTextContent(validated_only=True),
        modname)
    return module

def fail_hook_erp5_component(modname):
    if not modname.startswith('erp5.'):
        raise AstroidBuildingException()

    if (modname in ('erp5.portal_type',
                    'erp5.component',
                    'erp5.component.module',
                    'erp5.component.extension',
                    'erp5.component.document',
                    'erp5.component.tool',
                    'erp5.component.interface',
                    'erp5.component.mixin',
                    'erp5.component.test') or
        (modname.startswith('erp5.component.') and modname.endswith('_version'))):
        module = AstroidBuilder(MANAGER).string_build('', modname)
        if modname.startswith('erp5.component'):
            module.package = True
    else:
        module = _buildAstroidModuleFromComponentModuleName(modname)

    return module
MANAGER.register_failed_import_hook(fail_hook_erp5_component)

## Patch to handle 'no-name-in-module' for attributes added by monkey
## patches in Products/XXX/patches.
##
## Instead of monkey patching, an alternative would be to use Pylint
## transforms but this would require either checking dynamically which
## attributes has been added (much more complex than the current approach)
## or listing them statically (inconvenient).
from astroid.exceptions import NotFoundError
from astroid.scoped_nodes import Module
Module_getattr = Module.getattr
def _getattr(self, name, *args, **kw):
    try:
        return Module_getattr(self, name, *args, **kw)
    except NotFoundError as e:
        if self.name.startswith('erp5.'):
            raise

        real_module = __import__(self.name, fromlist=[self.name], level=0)
        try:
            attr = getattr(real_module, name)
        except AttributeError:
            raise e

        # REQUEST object (or any object non acquisition-wrapped)
        if (isinstance(attr, str) and
            attr == '<Special Object Used to Force Acquisition>'):
            raise e

        try:
            origin_module_name = attr.__module__
        except AttributeError:
            from astroid import nodes
            if isinstance(attr, dict):
                ast = nodes.Dict(attr)
            elif isinstance(attr, list):
                ast = nodes.List(attr)
            elif isinstance(attr, tuple):
                ast = nodes.Tuple(attr)
            elif isinstance(attr, set):
                ast = nodes.Set(attr)
            else:
                try:
                    ast = nodes.Const(attr)
                except Exception:
                    raise e
        else:
            if self.name == origin_module_name:
                raise

            # ast_from_class() actually works for any attribute of a Module
            try:
                ast = MANAGER.ast_from_class(attr)
            except AstroidBuildingException:
                raise e

        self.locals[name] = [ast]
        return [ast]
Module.getattr = _getattr


from astroid import register_module_extender
def AccessControl_PermissionRole_transform():
    return AstroidBuilder(MANAGER).string_build('''
def rolesForPermissionOn(perm, object, default=_default_roles, n=None):
    return None

class PermissionRole(object):
    def __init__(self, name, default=('Manager',)):
        return None
    def __of__(self, parent):
        return None
    def rolesForPermissionOn(self, value):
        return None

class imPermissionRole(object):
    def __of__(self, value):
        return None
    def rolesForPermissionOn(self, value):
        return None
    def __getitem__(self, i):
        return None
    def __len__(self):
        return None

_what_not_even_god_should_do = []
''')
register_module_extender(MANAGER, 'AccessControl.PermissionRole',
                         AccessControl_PermissionRole_transform)

## Package dynamically extending the namespace of their modules with C
## extension symbols
# astroid/brain/ added dynamically to sys.path by astroid __init__
try:
    from brain_gi import _gi_build_stub as build_stub
except ImportError: # BBB: old version of astroid
    from py2gi import _gi_build_stub as build_stub
def _register_module_extender_from_live_module(module_name, module):
    def transform():
        return AstroidBuilder(MANAGER).string_build(build_stub(module))
    register_module_extender(MANAGER, module_name, transform)

# No name 'OOBTree' in module 'BTrees.OOBTree' (no-name-in-module)
#
# When the corresponding C Extension (BTrees._Foo) is available, update
# BTrees.Foo namespace from the C extension, otherwise use Python definitions
# by dropping the `Py` suffix in BTrees.Foo symbols.
import BTrees
import inspect
for module_name, module in inspect.getmembers(BTrees, inspect.ismodule):
    if module_name[0] != '_':
        continue
    try:
        extended_module = BTrees.__dict__[module_name[1:]]
    except KeyError:
        continue
    else:
        _register_module_extender_from_live_module(extended_module.__name__,
                                                   module)

# No name 'ElementMaker' in module 'lxml.builder' (no-name-in-module)
#
# imp.load_dynamic() on .so file
import lxml
import os
for filename in os.listdir(os.path.dirname(lxml.__file__)):
    if filename.endswith('.so'):
        module_name = 'lxml.' + filename.split('.', 1)[0]
        _register_module_extender_from_live_module(
            module_name,
            __import__(module_name, fromlist=[module_name], level=0))

# Wendelin is special namespace package which pylint fails to recognize, and so
# complains about things like `from wendelin.bigarray.array_zodb import ZBigArray`
# with `No name 'bigarray' in module 'wendelin' (no-name-in-module)`.
#
# -> Teach pylint to properly understand wendelin package nature.
try:
    import wendelin
except ImportError:
    pass
else:
    def wendelin_transform(node):
        m = AstroidBuilder(MANAGER).string_build('__path__ = %r' % wendelin.__path__)
        m.package = True
        return m
    MANAGER.register_transform(Module, wendelin_transform, lambda node: node.name == 'wendelin')

# Properly search for namespace packages: original astroid (as of 1.3.8) only
# checks at top-level and it doesn't work for Shared.DC.ZRDB (defined in
# Products.ZSQLMethods; Shared and Shared.DC being a namespace package defined
# in Zope2) as Shared (rather than Shared.DC) is considered...
from astroid import modutils
try: # BBB
    modutils__module_file = modutils._module_file
except AttributeError:
    pass # recent astroid, anything to do ?
else:
    def _module_file(modpath, path=None):
        if modutils.pkg_resources is not None:
            i = len(modpath) - 1
            while i > 0:
                package = '.'.join(modpath[0:i])
                if (package in modutils.pkg_resources._namespace_packages and
                        package in sys.modules):
                    modpath = modpath[i:]
                    path = sys.modules[package].__path__
                    break
                i -= 1
        return modutils__module_file(modpath, path)
    modutils._module_file = _module_file

if sys.modules['isort'] is None:
    del sys.modules['isort']
