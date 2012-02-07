# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Jean-Paul Smets <jp@nexedi.com>
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

import transaction

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Base import Base
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from zLOG import LOG, INFO, WARNING

_last_sync = -1
class ComponentTool(BaseTool):
  """
    This tool provides methods to load the the different types 
    of components of the ERP5 framework: Document classes, interfaces,
    mixin classes, fields, accessors, etc.
  """
  id = "portal_components"
  meta_type = "ERP5 Component Tool"
  portal_type = "Component Tool"

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'reset')
  def reset(self, force=True):
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
      portal.newCacheCookie('component_classes')
      last_sync = portal.getCacheCookie('component_classes')
    else:
      cookie = portal.getCacheCookie('component_classes')
      if cookie == last_sync:
        type_tool.resetDynamicDocumentsOnceAtTransactionBoundary()
        return
      last_sync = cookie

    LOG("ERP5Type.Tool.ComponentTool", INFO, "Resetting Components")

    type_tool = portal.portal_types

    allowed_content_type_list = type_tool.getTypeInfo(
      self.getPortalType()).getTypeAllowedContentTypeList()

    import erp5.component

    with Base.aq_method_lock:
      for content_type in allowed_content_type_list:
        module_name = content_type.split(' ')[0].lower()

        try:
          module = getattr(erp5.component, module_name)
        # XXX-arnau: not everything is defined yet...
        except AttributeError:
          pass
        else:
          for name in module.__dict__.keys():
            if name[0] != '_':
              LOG("ERP5Type.Tool.ComponentTool", INFO,
                  "Resetting erp5.component.%s.%s" % (module_name, name))

              delattr(module, name)

    type_tool.resetDynamicDocumentsOnceAtTransactionBoundary()

  security.declareProtected(Permissions.ModifyPortalContent,
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
      transaction.get().addBeforeCommitHook(self.reset)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'createAllComponentFromFilesystem')
  def createAllComponentFromFilesystem(self, erase_existing=False,
                                       REQUEST=None):
    """
    XXX-arnau: only bt5 Extensions and Documents for now
    """
    portal = self.getPortalObject()

    import erp5.portal_type
    type_tool = portal.portal_types
    failed_import_dict = {}
    for content_portal_type in getattr(type_tool,
                                       self.portal_type).getTypeAllowedContentTypeList():
      try:
        failed_import_dict.update(
          getattr(erp5.portal_type,
                  content_portal_type).importAllFromFilesystem(self,
                                                               erase_existing=erase_existing))
      # XXX-arnau: NotImplementedErrror only until everything has been
      # implemented
      except (NotImplementedError, AttributeError):
        LOG("ERP5Type.Tool.ComponentTool", WARNING, "Could not import %ss" % \
              content_portal_type)

    if REQUEST:
      if failed_import_dict:
        failed_import_formatted_list = []
        for name, error in failed_import_dict.iteritems():
          failed_import_formatted_list.append("%s (%s)" % (name, error))

        message = "The following component could not be imported: %s" % \
            ', '.join(failed_import_formatted_list)
      else:
        message = "All components were successfully imported " \
            "from filesystem to ZODB."

      return self.Base_redirect('view',
                                keep_items={'portal_status_message': message})
