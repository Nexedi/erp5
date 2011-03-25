##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class RuleConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup Rules. """

  meta_type = 'ERP5 Rule Configurator Item'
  portal_type = 'Rule Configurator Item'
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
                    , PropertySheet.DublinCore )

  def build(self, business_configuration):
    portal = self.getPortalObject()
    simulation_rule_dict = portal.ERPSite_getConfiguratorSimulationRuleDict()
    for key, value in simulation_rule_dict.iteritems():
      reference = value.get('default_reference')
      result = portal.portal_rules.searchFolder(sort_on='version',
                                                sort_order='descending',
                                                reference=reference)
      if len(result):
        value['version'] = int(result[0].getVersion(0)) + 1
      rule = portal.portal_rules.newContent(**value)

      content_list = value.pop('content_list')
      for content_dict in content_list:
        rule.newContent(**content_dict)

      self.install(rule, business_configuration)
