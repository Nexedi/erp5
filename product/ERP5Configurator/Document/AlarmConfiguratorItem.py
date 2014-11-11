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

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    portal_alarms = self.getPortalObject().portal_alarms
    error_list = []
    property_dict = {
      "active_sense_method_id" : self.getActiveSenseMethodId(),
      "destination_list" : self.getDesitnationList(),
      "periodicity_hour_list" : self.getPeriodicityHourList(),
      "periodicity_minute_list": self.getPeriodicityMinuteList(),
      "periodicity_minute_frequency": self.getPeriodicityMinuteFrequency(),
      "periodicity_week_list": self.getPeriodicityWeekList(),
      "periodicity_week_day_list": self.getPeriodicityWeeDaykList(),
      "periodicity_week_frequency": self.getPeriodicityWeekFrequency(),
      "periodicity_month_list": self.getPeriodicityMonthList(),
      "periodicity_month_day_list": self.getPeriodicityMonthDayList(),
      "periodicity_start_date": DateTime() - 1,
      #"periodicity_stop_date": self.getPeriodicityStopDate(),
      "periodicity_week_list": self.getPeriodicityWeekList(),
      "report_method_id": self.getReportMethodId(),
                        }

    alarm_id = self.getId()
    alarm = getattr(portal_alarms, alarm_id, None)
    if alarm is None:
      error_list.append(self._createConstraintMessage(
        "Alarm %s should be created" % alarm_id))
      if fixit:
        alarm = portal_alarms.newContent(id=alarm_id,
                                        title=self.getTitle())
        alarm.edit(**property_dict)

        # Always enabled
        alarm.setEnabled(True)

    if alarm and fixit:
      ## add to customer template
      business_configuration = self.getBusinessConfigurationValue()
      self.install(alarm, business_configuration)

    return error_list
