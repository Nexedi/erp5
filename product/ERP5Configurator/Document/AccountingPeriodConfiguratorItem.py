##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

class AccountingPeriodConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup an Accounting Period. """

  meta_type = 'ERP5 Accounting Period Configurator Item'
  portal_type = 'Accounting Period Configurator Item'
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
                    , PropertySheet.Task )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    portal = self.getPortalObject()
    business_configuration = self.getBusinessConfigurationValue()
    organisation_id = business_configuration.\
                                 getGlobalConfigurationAttr('organisation_id')
    organisation = portal.organisation_module._getOb(organisation_id)
    if fixit:
      period = organisation.newContent(
                              portal_type='Accounting Period',
                              start_date=self.getStartDate(),
                              stop_date=self.getStopDate(),
                              short_title=self.getShortTitle(),
                              title=self.getTitle())

      if self.portal_workflow.isTransitionPossible(period, 'start'):
        period.start(comment="Started by Configurator")

    # no need to 'install' in the business template, because it's contain as
    # subobject of an organisation we already added.
    return ['Accounting Period %s should be created' % self.getTitle()]
