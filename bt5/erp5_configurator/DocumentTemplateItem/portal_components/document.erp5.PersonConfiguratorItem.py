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
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from DateTime import DateTime
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem


@zope.interface.implementer(IConfiguratorItem)
class PersonConfiguratorItem(XMLObject, ConfiguratorItemMixin):
  """ Setup user. """

  meta_type = 'ERP5 Person Configurator Item'
  portal_type = 'Person Configurator Item'
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
                    , PropertySheet.Reference
                    , PropertySheet.Person
                    , PropertySheet.Login)

  def _checkConsistency(self, fixit=False, **kw):
    error_list = []
    person_list = self.acl_users.searchUsers(id=self.Person_getUserId(), exact_match=True)
    if not person_list:
      error_list.append(self._createConstraintMessage("Person %s should be created" % self.Person_getUserId()))
      if fixit:
        person_module = self.getPortalObject().person_module
        person = person_module.newContent(portal_type="Person")
        group_id = getattr(aq_base(self), 'group_id', None)
        site_id = getattr(aq_base(self), 'site_id', None)

        business_configuration = self.getBusinessConfigurationValue()
        organisation_id = getattr(aq_base(self), 'organisation_id', None)
        if organisation_id is None:
          organisation_id = business_configuration.\
                              getGlobalConfigurationAttr('organisation_id')
        if organisation_id is not None:
          person.setCareerSubordination('organisation_module/%s' % \
                                         organisation_id)

        # save
        person.edit(**{'default_email_text': self.getDefaultEmailText(),
                      'default_telephone_text': self.getDefaultTelephoneText(),
                      'first_name': self.getFirstName(),
                      'career_function': self.getFunction(),
                      'last_name': self.getLastName(),
                      'reference': self.getReference(),
                        })

        assignment = person.newContent(portal_type="Assignment",
                                      function = self.getFunction(),
                                      group = group_id,
                                      site = site_id)

        login = person.newContent(portal_type='ERP5 Login',
                                  reference=self.getReference(),
                                  password=self.getPassword())

        # Set dates are required to create valid assigments.
        now = DateTime()
        assignment.setStartDate(now)
        # XXX Is it required to set stop date?
        # Define valid for 10 years.
        assignment.setStopDate(now + (365*10))

        # Validate the Person, Assigment and Login
        person.validate(comment=translateString("Validated by Configurator"))
        assignment.open(comment=translateString("Open by Configuration"))
        login.validate(comment=translateString("Validated by Configurator"))
        current_career = person.getDefaultCareerValue()
        current_career.Career_setEmployeeNumber(batch=1)

        ## add to customer template
        business_configuration = self.getBusinessConfigurationValue()
        self.install(person, business_configuration)

    return error_list
