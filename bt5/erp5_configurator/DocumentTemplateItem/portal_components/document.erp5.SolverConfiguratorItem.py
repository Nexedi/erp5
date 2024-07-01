##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                   Rafael Monnerat <rafael@nexedi.com>
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
import six


@zope.interface.implementer(IConfiguratorItem)
class SolverConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup Solvers. """

  meta_type = 'ERP5 Solver Configurator Item'
  portal_type = 'Solver Configurator Item'
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
    if fixit:
      portal = self.getPortalObject()
      business_configuration = self.getBusinessConfigurationValue()

      solver = getattr(portal.portal_solvers, self.getId(), None)
      if solver is None:
        solver_property_dict = \
            business_configuration.BusinessConfiguration_getSolverPropertyDict()
        property_dict = solver_property_dict.get(self.getId())
        argument_dict = {}

        for k, v in six.iteritems(property_dict):
          if k not in ("content_list",) and k in self.showDict():
            argument_dict[k] = v

        solver = portal.portal_solvers.newContent(portal_type="Solver Type",
                                                  id=argument_dict.pop('id'))
        solver.edit(**argument_dict)

        for information_dict in self.content_list:
          portal_type = information_dict.pop('portal_type')
          action = solver.newContent(portal_type=portal_type, id=information_dict.pop('id'))
          action.edit(**information_dict)

      self.install(solver, business_configuration)

    return [self._createConstraintMessage('Solvers should be created')]
