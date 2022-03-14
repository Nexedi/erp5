##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem

@zope.interface.implementer(IConfiguratorItem)
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

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference )

  def _checkConsistency(self, fixit=False, **kw):
    if fixit:
      portal = self.getPortalObject()
      template_id = self.getId()

      if getattr(portal.portal_rules, template_id, None) is not None:
        cb_data = portal.portal_rules.manage_copyObjects([template_id])
        copied, = portal.portal_rules.manage_pasteObjects(cb_data)
        rule = portal.portal_rules[copied["new_id"]]
        if self.getReference() is not None:
          rule.edit(reference=self.getReference())
        rule.setVersion(str(int(rule.getVersion(0)) + 1))
        if len(self.getTradePhaseList()) > 0:
          rule.setTradePhaseList(self.getTradePhaseList())
        rule.validate()
      else:
        raise ValueError("Unable to find rule template with id %s" % template_id)

      business_configuration = self.getBusinessConfigurationValue()
      self.install(rule, business_configuration)
    return [self._createConstraintMessage('Rule should be defined')]
