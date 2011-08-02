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

class SystemPreferenceConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ 
    Setup system preference. 
  """

  meta_type = 'ERP5 System Preference Configurator Item'
  portal_type = 'System Preference Configurator Item'
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
    return ( # CRM
             'preferred_campaign_resource_list',
             'preferred_event_assessment_form_id_list',
             'preferred_event_resource_list',
             'preferred_event_sender_email',
             'preferred_meeting_resource_list',
             'preferred_sale_opportunity_resource_list',
             'preferred_support_request_resource_list',
             # DMS
             'preferred_conversion_cache_factory',
             'preferred_document_email_ingestion_address',
             'preferred_document_reference_method_id',
             'preferred_document_file_name_regular_expression',
             'preferred_document_reference_regular_expression',
             'preferred_document_classification',
             'preferred_synchronous_metadata_discovery',
             'preferred_redirect_to_document',
             'preferred_ooodoc_server_address',
             'preferred_ooodoc_server_port_number',
             # PDM
             'preferred_product_individual_variation_base_category_list',
             'preferred_component_individual_variation_base_category_list',
             'preferred_service_individual_variation_base_category_list',
             # Trade
             'preferred_supplier_role_list',
             'preferred_client_role_list',
             'preferred_sale_use_list',
             'preferred_purchase_use_list',
             'preferred_packing_use_list',
             # Express
             )


  def _build(self, business_configuration):
    portal = self.getPortalObject()
    portal_preferences = portal.portal_preferences
    preference = portal_preferences._getOb(self.object_id, None)
    activated_preference = portal_preferences.getActiveSystemPreference()
    if preference is None:
      preference = portal.portal_preferences.newContent(
                               portal_type = 'System Preference',
                               id=self.object_id,
                               title=self.title,
                               description=self.description,
                               priority=1)

    # XXX this have to be translated in user language.
    preference_dict = {}

    for preference_name in self._getPreferenceNameList():
      preference_value = getattr(self, preference_name,
                     preference.getProperty(preference_name))
      if preference_value is None and activated_preference is not None:
        preference_value = activated_preference.getProperty(preference_name)
      preference_dict[preference_name] = preference_value

    preference.edit(**preference_dict)
    bt5_obj = business_configuration.getSpecialiseValue()
    current_template_preference_list = list(bt5_obj.getTemplatePreferenceList())
    if preference.getId() not in current_template_preference_list:
      current_template_preference_list.append(preference.getId())
      bt5_obj.edit(template_preference_list=current_template_preference_list,)

