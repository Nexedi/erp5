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

from types import ModuleType

import transaction
import sys

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Base import Base
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from zLOG import LOG, INFO, WARNING

from DateTime import DateTime
DEFAULT_TEST_TEMPLATE_COPYRIGHT = "Copyright (c) 2002-%s Nexedi SA and " \
    "Contributors. All Rights Reserved." % DateTime().year()

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

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ResetDynamicClasses, 'reset')
  def reset(self, force=False, reset_portal_type=False):
    """
    XXX-arnau: global reset
    """
    portal = self.getPortalObject()

    # XXX-arnau: copy/paste from portal_type_class, but is this really
    # necessary as even for Portal Type classes, synchronizeDynamicModules
    # seems to always called with force=True?
    global last_sync
    if force:
      # hard invalidation to force sync between nodes
      portal.newCacheCookie('component_packages')
      last_sync = portal.getCacheCookie('component_packages')
    else:
      cookie = portal.getCacheCookie('component_packages')
      if cookie == last_sync:
        return False
      last_sync = cookie

    LOG("ERP5Type.Tool.ComponentTool", INFO, "Resetting Components")

    type_tool = portal.portal_types

    allowed_content_type_list = type_tool.getTypeInfo(
      self.getPortalType()).getTypeAllowedContentTypeList()

    import erp5.component

    with Base.aq_method_lock:
      for content_type in allowed_content_type_list:
        package_name = content_type.split(' ')[0].lower()

        try:
          package = getattr(erp5.component, package_name)
        # XXX-arnau: not everything is defined yet...
        except AttributeError:
          pass
        else:
          package.reset()

    if reset_portal_type:
      type_tool.resetDynamicDocumentsOnceAtTransactionBoundary()

    return True

  security.declareProtected(Permissions.ResetDynamicClasses,
                            'resetOnceAtTransactionBoundary')
  def resetOnceAtTransactionBoundary(self):
    """
    Schedule a single reset at the end of the transaction, only once.  The
    idea behind this is that a reset is (very) costly and that we want to do
    it as little often as possible.  Moreover, doing it twice in a transaction
    is useless (but still twice as costly).
    """
    tv = getTransactionalVariable()
    key = 'ComponentTool.resetOnceAtTransactionBoundary'
    if key not in tv:
      tv[key] = None
      transaction.get().addBeforeCommitHook(self.reset,
                                            args=(True, True))

  # XXX-arnau: copy/paste from ClassTool
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

  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_01_sampleTest(self):
    """
    A Sample Test

    For the method to be called during the test,
    its name must start with 'test'.
    The '_01_' part of the name is not mandatory,
    it just allows you to define in which order the tests are to be launched.
    Tests methods (self.assert... and self.failIf...)
    are defined in /usr/lib/python/unittest.py.
    """
    self.assertEqual(0, 1)
''' % DEFAULT_TEST_TEMPLATE_COPYRIGHT

  def newContent(self, *args, **kwargs):
    """
    Create new content. If this is a Test Component and no text_content has
    been given, then define a default template to help user, likewise
    ClassTool with filesystem live tests
    """
    if kwargs.get('portal_type') == 'Test Component':
      kwargs.setdefault('text_content', self.__test_text_content_template)

    return super(ComponentTool, self).newContent(*args, **kwargs)
