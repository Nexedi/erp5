##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
class CatalogKeywordKeyConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Set up catalog keyword keys."""

  meta_type = 'ERP5 Catalog Keyword Key Configurator Item'
  portal_type = 'Catalog Keyword Key Configurator Item'
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

  def _checkConsistency(self, fixit=False, **kw):
    error_list = []
    portal = self.getPortalObject()
    catalog = portal.portal_catalog.getSQLCatalog()
    key_list = list(catalog.getSqlCatalogSearchKeysList())
    for k in self.key_list:
      if k not in key_list:
        error_list.append(self._createConstraintMessage(
          "%s should be in sql_catalog_keyword_search_keys" % k))
        key_list.append(k)
    key_list = tuple(key_list)
    if fixit:
      catalog._setPropValue('sql_catalog_keyword_search_keys', key_list)
      business_configuration = self.getBusinessConfigurationValue()
      bt = business_configuration.getSpecialiseValue()
      bt.edit(template_catalog_keyword_key_list=key_list)

    return error_list
