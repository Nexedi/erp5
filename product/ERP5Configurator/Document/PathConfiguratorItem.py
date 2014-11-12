##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    TAHARA Yusei <yusei@nexedi.com>
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

from warnings import warn
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class PathConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Create documents of given portal type in given path."""

  meta_type = 'ERP5 Path Configurator Item'
  portal_type = 'Path Configurator Item'
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
                    , PropertySheet.ConfiguratorItem )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    portal = self.getPortalObject()
    error_list = []
    for container_path, transition_method, document_dict in iter(self.getConfigurationListList()):
      document_dict = document_dict.copy()
      document_id = document_dict.pop('id')
      portal_type = document_dict.pop('portal_type')
      container = portal.unrestrictedTraverse(container_path, None)
      if container is not None:
        document = getattr(container, document_id, None)
        if document is None:
          error_list.append(self._createConstraintMessage(
            "%s %s should be created" %(portal_type, document_id)))
          if fixit:
            document_init_dict = { 'portal_type' : portal_type,
                                   'id': document_id }
            if 'title' in document_dict:
              document_init_dict['title'] = document_dict.pop('title')
            document = container.newContent(**document_init_dict)
            document.edit(**document_dict)
            if transition_method is not None:
              getattr(document, transition_method) (
                comment=translateString("Transition executed by Configurator"))

        if document:
          ## add to customer template
          business_configuration = self.getBusinessConfigurationValue()
          self.install(document, business_configuration)

    return error_list
