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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem


@zope.interface.implementer(IConfiguratorItem)
class PreferenceConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup preference. """

  meta_type = 'ERP5 Preference Configurator Item'
  portal_type = 'Preference Configurator Item'
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

  def _getPreferenceNameList(self):
    """Return names of preference properties.
    """
    property_id_list = []
    portal = self.getPortalObject()
    for property_sheet_id in portal.portal_types.Preference.getTypePropertySheetList():
      property_sheet = portal.portal_property_sheets[property_sheet_id]
      for prop in property_sheet.contentValues():
        if prop.getProperty('preference'):
          list_prefix = ''
          if prop.getProperty('multivalued') or (
               prop.getProperty('elementary_type') in (
                 'lines', 'multiple selection', 'tokens')):
            list_prefix = '_list'
          property_id_list.append('%s%s' % (prop.getReference(), list_prefix))
    return property_id_list

  def _checkConsistency(self, fixit=False, **kw):
    error_list = []
    portal = self.getPortalObject()
    preference = portal.portal_preferences._getOb(self.object_id, None)
    if preference is None:
      error_list.append(self._createConstraintMessage(
        "Preference %s should be created" % self.object_id))
      if fixit:
        preference = portal.portal_preferences.newContent(
                                portal_type = 'Preference',
                                id = self.object_id,
                                title = self.title,
                                description = self.description,
                                priority = 1)
      else:
        return error_list

    preference_dict = {}

    marker = []
    for preference_name in self._getPreferenceNameList():
      preference_value = getattr(self, preference_name,
                     preference.getProperty(preference_name, marker))
      if preference_value is not marker and preference_value is not None:
        preference_dict[preference_name] = preference_value

    if self.portal_workflow.isTransitionPossible(preference, 'enable'):
      preference.enable()

    business_configuration = self.getBusinessConfigurationValue()
    organisation_id = business_configuration.\
                                 getGlobalConfigurationAttr('organisation_id')
    organisation_path = 'organisation_module/%s' % organisation_id
    preference_dict['preferred_accounting_transaction_source_section'] = \
                                                          organisation_path
    preference_dict['preferred_section'] = organisation_path
    preference.edit(**preference_dict)
    bt5_obj = business_configuration.getSpecialiseValue()
    current_template_preference_list = list(bt5_obj.getTemplatePreferenceList())
    if preference.getId() not in current_template_preference_list:
      current_template_preference_list.append(preference.getId())
      bt5_obj.edit(template_preference_list=current_template_preference_list,)

    return error_list
