##############################################################################
#
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.skin_configurator_item import \
                                       SkinConfiguratorItemMixin

class SecurityCategoryMappingConfiguratorItem(SkinConfiguratorItemMixin,
                                              XMLObject):
  """ Setup the ERP5Type_getSecurityCategoryMapping Python Script which
      is the onde that defines the Security Mapping for the user login. """

  meta_type = 'ERP5 Security Category Mapping Configurator Item'
  portal_type = 'Security Category Mapping Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )
  def _checkConsistency(self, fixit=False, filter=None, **kw):
    script_id = 'ERP5Type_getSecurityCategoryMapping'
    error_list = ['%s should be created' % script_id,]
    if fixit:
      portal_alarms = self.getPortalObject().portal_alarms
      script_content = """return (
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function']),
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['follow_up']),
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function', 'follow_up']),
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['group']),
  ('ERP5Type_getSecurityCategoryRoot', ['group']),
  )"""

      folder = self._createSkinFolder()
      self._createZODBPythonScript(folder,
                                   script_id,
                                    '', script_content)

      ## add to customer template
      business_configuration = self.getBusinessConfigurationValue()
      self.install(folder, business_configuration)

    return error_list
