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
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

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

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore )

  def _getPreferenceNameList(self):
    """Returns all existing preference names.

    TODO: this should be done by introspecting property sheet.
    """
    return ( 'preferred_category_child_item_list_method_id',
             'preferred_accounting_transaction_from_date',
             'preferred_accounting_transaction_at_date',
             'preferred_section_category',
             'preferred_section',
             'preferred_accounting_transaction_section_category',
             'preferred_accounting_transaction_source_section',
             'preferred_accounting_transaction_currency',
             'preferred_accounting_transaction_gap',
             'preferred_accounting_transaction_simulation_state_list',
             'preferred_text_format',
             'preferred_text_editor',
             'preferred_date_order',
             'preferred_listbox_view_mode_line_count',
             'preferred_listbox_list_mode_line_count',
             'preferred_string_field_width',
             'preferred_textarea_width',
             'preferred_textarea_height',
             'preferred_money_quantity_field_width',
             'preferred_quantity_field_width',
             'preferred_report_style',
             'preferred_report_format',
             'preferred_html_style_access_tab',
             )


  def build(self, business_configuration):
    portal = self.getPortalObject()
    organisation_id = business_configuration.\
                                 getGlobalConfigurationAttr('organisation_id')
    organisation_path = 'organisation_module/%s' % organisation_id

    preference = portal.portal_preferences._getOb(self.object_id, None)
    if preference is None:
      preference = portal.portal_preferences.newContent(
                              portal_type='Preference',
                              id=self.object_id,
                              title = self.title,
                              description = self.description,
                              priority = 1)

    # XXX this have to be translated in user language.
    preference_dict = {}

    marker = []
    for preference_name in self._getPreferenceNameList():
      preference_value = getattr(self, preference_name,
                     preference.getProperty(preference_name, marker))
      if preference_value is not marker:
        preference_dict[preference_name] = preference_value

    preference_dict['preferred_accounting_transaction_source_section'] = \
                                                             organisation_path
    preference_dict['preferred_section'] = organisation_path
    preference.edit(**preference_dict)
    bt5_obj = business_configuration.getSpecialiseValue()
    current_template_preference_list = list(bt5_obj.getTemplatePreferenceList())
    if preference.getId() not in current_template_preference_list:
      current_template_preference_list.append(preference.getId())
      bt5_obj.edit(template_preference_list=current_template_preference_list,)

