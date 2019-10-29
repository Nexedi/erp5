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
from astroid import MANAGER

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
    return self._post_build(module, encoding)
AstroidBuilder.string_build = string_build

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
    erp5_package_node._absolute_import_activated = True
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
            raise AstroidBuildingException
        if obj.getValidationState() in ('modified', 'validated'):
            component_obj = obj
        else:
            raise AstroidBuildingException

    else:
        try:
            package, reference = component_id.split('.', 1)
        except ValueError:
            raise AstroidBuildingException
        for version in portal.getVersionPriorityNameList():
            try:
                obj = getattr(component_tool,
                              '%s.%s.%s' % (package, version, reference))
            except AttributeError:
                continue

            if obj.getValidationState() in ('modified', 'validated'):
                component_obj = obj
                break

    if component_obj is None:
        raise AstroidBuildingException

    # module_build() could also be used but this requires importing
    # the ZODB Component and also monkey-patch it to support PEP-302
    # for __file__ starting with '<'
    module = AstroidBuilder(MANAGER).string_build(
        component_obj.getTextContent(validated_only=True),
        modname)
    return module

def fail_hook_erp5_component(modname):
    if not modname.startswith('erp5.'):
        raise AstroidBuildingException

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

    module._absolute_import_activated = True
    return module
MANAGER.register_failed_import_hook(fail_hook_erp5_component)

## Patch to handle 'no-name-in-module' for attributes added by monkey
## patches in Products/XXX/patches.
##
## Instead of monkey patching, an alternative would be to use Pylint
## transforms but this would require either checking dynamically which
## attributes has been added (much more complex than the current approach)
## or listing them statically (inconvenient).
from pylint.checkers import BaseChecker
from pylint.interfaces import UNDEFINED
BaseChecker_add_message = BaseChecker.add_message
def add_message(self, msg_descr, line=None, node=None, args=None,
                confidence=UNDEFINED):
    """
    Monkey patched to dynamically ignore some error/warning messages
    """
    if msg_descr == 'no-name-in-module':
        name, module_name = args
        if not module_name.startswith('erp5.'):
            # Do not call __import__ as this may load ZODB Component which
            # should use 'version' and not use monkey patches...
            try:
                getattr(sys.modules[module_name], name)
            except (KeyError, AttributeError):
                pass
            else:
                # Do nothing as this does exist
                return
    BaseChecker_add_message(self, msg_descr, line=line, node=node,
                            args=args, confidence=confidence)
BaseChecker.add_message = add_message

if sys.modules['isort'] is None:
    del sys.modules['isort']
