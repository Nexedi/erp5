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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

from zLOG import LOG, INFO, WARNING

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

  security.declareProtected(Permissions.ManagePortal, 'reset')
  def reset(self, is_sync=False):
    """
    XXX-arnau: global reset
    """
    LOG("ERP5Type.Tool.ComponentTool", INFO, "Global reset")

    import erp5.component

    portal = self.getPortalObject()

    if not is_sync:
      portal.newCacheCookie('component_classes')
      erp5.component._last_reset = portal.getCacheCookie('component_classes')

    container_type_info = portal.portal_types.getTypeInfo(self.getPortalType())

    for content_type in container_type_info.getTypeAllowedContentTypeList():
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
                "Global reset of %s.%s" % (module_name, name))

            delattr(module, name)

  security.declareProtected(Permissions.ManagePortal,
                            'createAllComponentFromFilesystem')
  def createAllComponentFromFilesystem(self, erase_existing=False,
                                       REQUEST=None):
    """

    XXX-arnau: only Extensions for now
    """
    portal = self.getPortalObject()

    import erp5.portal_type
    type_tool = portal.portal_types
    failed_import_dict = {}
    for content_portal_type in getattr(type_tool,
                                       self.portal_type).getTypeAllowedContentTypeList():
      try:
        failed_import_dict.update(getattr(erp5.portal_type,
                                          content_portal_type).importAllFromFilesystem(self))
      except AttributeError:
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
