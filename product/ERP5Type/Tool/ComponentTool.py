# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011-2012 Nexedi SA and Contributors. All Rights Reserved.
#                         Jean-Paul Smets <jp@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from six import string_types as basestring
from types import ModuleType

import transaction
import sys

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from AccessControl.Permission import Permission
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.dynamic import aq_method_lock
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from zLOG import LOG, INFO, WARNING
import six

global_stream = None

from DateTime import DateTime
DEFAULT_TEST_TEMPLATE_COPYRIGHT = "Copyright (c) 2002-%s Nexedi SA and " \
    "Contributors. All Rights Reserved." % DateTime().year()

live_test_running = False
last_sync = -1
class ComponentTool(BaseTool):
  """
  This tool provides methods to load the the different types of components of
  the ERP5 framework: Document classes, interfaces, mixin classes, fields,
  accessors, etc.
  """
  id = "portal_components"
  meta_type = "ERP5 Component Tool"
  portal_type = "Component Tool"
  title = "Components"

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @classmethod
  def _applyAllStaticSecurity(cls):
    """
    Apply static security on portal_components to ensure that nobody can
    change Permissions, only 'ghost' Developer Role has Permissions to
    add/modify/delete Components. Also, make these permissions read-only
    thanks to 'property'.

    cls is erp5.portal_type.Component Tool and not this class as this function
    is called on Portal Type class when loading Componet Tool Portal Type
    class
    """
    from AccessControl.Permission import getPermissions, pname
    for permission_name, _, _ in getPermissions():
      if permission_name == 'Reset dynamic classes':
        permission_function = lambda self: ('Manager',)
      elif permission_name in ('Change permissions', 'Define permissions'):
        permission_function = lambda self: ()
      elif (permission_name.startswith('Access ') or
            permission_name.startswith('View') or
            permission_name == 'WebDAV access'):
        permission_function = lambda self: ('Developer', 'Manager')
      else:
        permission_function = lambda self: ('Developer',)

      setattr(cls, pname(permission_name), property(permission_function))

  def _isBootstrapRequired(self):
    """
    Required by synchronizeDynamicModules() to bootstrap an empty site and
    thus create portal_components

    XXX-arnau: Only bt5 items for now
    """
    return False

  def _bootstrap(self):
    """
    Required by synchronizeDynamicModules() to bootstrap an empty site and
    thus create portal_components

    XXX-arnau: Only bt5 items for now
    """
    pass

  security.declareProtected(Permissions.ResetDynamicClasses, 'reset')
  def reset(self,
            force=False,
            reset_portal_type_at_transaction_boundary=False):
    """
    Reset all ZODB Component packages. A cache cookie is used to check whether
    the reset is necessary when force is not specified. This allows to make
    sure that all ZEO clients get reset (checked in __of__ on ERP5Site) when
    one given ZEO client gets reset when Component(s) are modified or
    invalidated.

    Also, as resetting ZODB Components Package usually implies to reset Portal
    Type as Classes (because the former are used as bases), perform the reset
    by default.

    XXX-arnau: for now, this is a global reset but it might be improved in the
    future if required...
    """
    portal = self.getPortalObject()

    global last_sync
    if force:
      # Hard invalidation to force sync between nodes
      portal.newCacheCookie('component_packages')
      last_sync = portal.getCacheCookie('component_packages')
    else:
      cookie = portal.getCacheCookie('component_packages')
      if cookie == last_sync:
        return False

      last_sync = cookie

    LOG("ERP5Type.Tool.ComponentTool", INFO, "Resetting Components")

    # Make sure that it is not possible to load Components or load Portal Type
    # class when Components are reset through aq_method_lock
    import erp5.component
    from Products.ERP5Type.dynamic.component_package import ComponentDynamicPackage
    with aq_method_lock:
      component_package_list = []
      for package in six.itervalues(erp5.component.__dict__):
        if isinstance(package, ComponentDynamicPackage):
          package.reset()
          component_package_list.append(package.__name__)

      erp5.component.filesystem_import_dict = None
      erp5.component.ref_manager.gc()

      # Clear astroid (pylint) cache
      if six.PY2:
        from astroid.builder import MANAGER
      else:
        from astroid.astroid_manager import MANAGER
      astroid_cache = MANAGER.astroid_cache
      for k in list(astroid_cache.keys()):
        if k.startswith('erp5.component.') and k not in component_package_list:
          del astroid_cache[k]

    if reset_portal_type_at_transaction_boundary:
      portal.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
    else:
      from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
      synchronizeDynamicModules(self, force)

    return True

  security.declareProtected(Permissions.ResetDynamicClasses,
                            'resetOnceAtTransactionBoundary')
  def resetOnceAtTransactionBoundary(self):
    """
    Schedule a single reset at the end of the transaction. The idea behind
    this is that a reset is (very) costly and that we want to do it as little
    often as possible.  Moreover, doing it twice in a transaction is useless
    (but still twice as costly).
    """
    tv = getTransactionalVariable()
    key = 'ComponentTool.resetOnceAtTransactionBoundary'
    if key not in tv:
      tv[key] = None
      transaction.get().addBeforeCommitHook(self.reset,
                                            args=(True, True))

  __test_text_content_template = '''\
##############################################################################
#
# %s
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_sampleTest(self):
    """
    A Sample Test

    For the method to be called during the test,
    its name must start with 'test'.

    See https://docs.python.org/2/library/unittest.html for help with available
    assertion methods.
    """
    self.assertEqual(0, 1)
''' % DEFAULT_TEST_TEMPLATE_COPYRIGHT

  def newContent(self, *args, **kwargs):
    """
    Create new content. If this is a Test Component and no text_content has
    been given, then define a default template to help user, likewise
    ClassTool with filesystem live tests

    XXX-arnau: should include more templates like ClassTool
    """
    if kwargs.get('portal_type') == 'Test Component':
      kwargs.setdefault('text_content', self.__test_text_content_template)

    return super(ComponentTool, self).newContent(*args, **kwargs)

  security.declarePrivate('_getCommaSeparatedParameterList')
  def _getCommaSeparatedParameterList(self, parameter_list):
    # clean parameter_list and split it by commas if necessary
    if not parameter_list:
      parameter_list = ()
    elif isinstance(parameter_list, basestring):
      parameter_list = tuple(parameter_name.strip()
                             for parameter_name in parameter_list.split(',')
                             if parameter_name.strip())
    return parameter_list

  security.declareProtected(Permissions.ManagePortal, 'runLiveTest')
  def runLiveTest(self, test_list=None, run_only=None, debug=False,
                  verbose=False, warnings='default'):
    """
    Launch live tests

    run_only=STRING      Run only specified test methods delimited with
                         commas (e.g. testFoo,testBar). This can be regular
                         expressions.
    debug=boolean        Invoke debugger on errors / failures.
    verbose=boolean      Display more information when running tests
    """
    from six import StringIO
    global global_stream
    global live_test_running
    self.serialize()
    if live_test_running:
      LOG('ComponentTool', INFO, 'Live test already running')
      return ''

    global_stream = StringIO()
    test_list = self._getCommaSeparatedParameterList(test_list)
    if not test_list:
      # no test to run
      return ''

    # Allow having strings for verbose and debug
    verbose = int(verbose) and True or False
    debug = int(debug) and True or False
    run_only = self._getCommaSeparatedParameterList(run_only)
    verbosity = verbose and 2 or 1
    request_server_url = self.REQUEST.get('SERVER_URL')

    try:
      live_test_running = True
      from Products.ERP5Type.tests.ERP5TypeLiveTestCase import runLiveTest
      try:
        result = runLiveTest(test_list,
                             run_only=run_only,
                             debug=debug,
                             stream=global_stream,
                             request_server_url=request_server_url,
                             verbosity=verbosity,
                             warnings=warnings)
      except ImportError:
        import traceback
        traceback.print_exc(file=global_stream)
      global_stream.seek(0)
      return global_stream.read()
    finally:
      live_test_running = False

  security.declareProtected(Permissions.ManagePortal, 'readTestOutput')
  def readTestOutput(self, position=0):
    """
    Return unread part of the test result
    """
    result = ''
    position = int(position)
    global global_stream
    if global_stream is not None:
      global_stream.seek(position)
      result = global_stream.read()
    return result
