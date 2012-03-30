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
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin
from DateTime import DateTime

class AlarmConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup an Alarm """

  meta_type = 'ERP5 Alarm Configurator Item'
  portal_type = 'Alarm Configurator Item'
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
                    , PropertySheet.Alarm
                    , PropertySheet.Periodicity
                    )

  def _build(self, business_configuration):
    portal_alarms = self.getPortalObject().portal_alarms
    property_dict = {
      "active_sense_method_id" : self.getActiveSenseMethodId(),
      "periodicity_minute_frequency" : self.getPeriodicityMinuteFrequency(),
      "periodicity_hour" : self.getPeriodicityHour(),
      "periodicity_minute": self.getPeriodicityMinute(),
      "periodicity_minute_frequency": self.getPeriodicityMinuteFrequency(),
      "periodicity_month": self.getPeriodicityMonth(),
      "periodicity_month_day": self.getPeriodicityMonthDay(),
      "periodicity_start_date": DateTime() - 1,
      #"periodicity_stop_date": self.getPeriodicityStopDate(),
      "periodicity_week": self.getPeriodicityWeek(),
                        }

    alarm = getattr(portal_alarms, self.getId(), None)
    if alarm is None:
      alarm = portal_alarms.newContent(id=self.getId(),
                                       title=self.getTitle())
    alarm.edit(**property_dict)

    # Always enabled
    alarm.setEnabled(True)

    ## add to customer template
    self.install(alarm, business_configuration)
