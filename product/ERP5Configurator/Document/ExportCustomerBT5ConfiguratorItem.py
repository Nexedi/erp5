##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.CMFCore.utils import getToolByName
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class ExportCustomerBT5ConfiguratorItem(XMLObject, ConfiguratorItemMixin):
  """ Create a new bt5 for customer configuration. """
  
  meta_type = 'ERP5 Export Customer BT5 Configurator Item'
  portal_type = 'Export Customer BT5 Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore )

  def build(self, business_configuration):
    portal = self.getPortalObject()
    template_tool = getToolByName(portal, 'portal_templates')
    bt5_obj = business_configuration.getSpecialiseValue()
    if bt5_obj.getBuildingState() != 'built':
      ## build template so it can be exported
      bt5_obj.edit()
      bt5_obj.build()
    bt5_data = template_tool.export(bt5_obj)
    business_configuration.newContent(
                        portal_type='File',
                        title = bt5_obj.getTitle(),
                        data = bt5_data)
