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
