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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class OrganisationConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ This class install a Organisation."""

  meta_type = 'ERP5 Organisation Configurator Item'
  portal_type = 'Organisation Configurator Item'
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
                    , PropertySheet.Organisation )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    """ Setup organisation. """
    if fixit:
      portal = self.getPortalObject()
      organisation = portal.organisation_module.newContent(portal_type="Organisation")

      org_dict = {'price_currency': 'currency_module/%s' % self.getPriceCurrency(),
                  'group': self.getGroup(),
                  'title': self.getTitle(),
                  'corporate_name': self.getCorporateName(),
                  'default_address_city': self.getDefaultAddressCity(),
                  'default_email_text': self.getDefaultEmailText(),
                  'default_telephone_text': self.getDefaultTelephoneText(),
                  'default_address_zip_code': self.getDefaultAddressZipCode(),
                  'default_address_region': self.getDefaultAddressRegion(),
                  'default_address_street_address': self.getDefaultAddressStreetAddress(),
                  'site':'main', # First customer's organisation is always main site.
                  }
      organisation.edit(**org_dict)

      business_configuration = self.getBusinessConfigurationValue()
      # store globally organization_id
      business_configuration.setGlobalConfigurationAttr(organisation_id=organisation.getId())
      business_configuration.setGlobalConfigurationAttr(\
        organisation_path='organisation_module/%s' %organisation.getId())

      if self.portal_workflow.isTransitionPossible(organisation, 'validate'):
        organisation.validate(comment=translateString("Validated by Configurator"))

      ## add to customer template
      self.install(organisation, business_configuration)
    return ['Organisation should be created',]
