##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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

class BusinessTemplate:
  """
    Organisation properties and categories
  """

  _properties = (
    { 'id'          : 'template_portal_type_id',
      'description' : 'A list of ids of portal types used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_module_id',
      'description' : 'A list of ids of modules used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_skin_id',
      'description' : 'A list of ids of skins used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_workflow_id',
      'description' : 'A list of ids of skins used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_product_id',
      'description' : 'A list of ids of products used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_document_id',
      'description' : 'A list of ids of documents used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_property_sheet_id',
      'description' : 'A list of ids of property sheets used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_role',
      'description' : 'A list of ids of roles used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_catalog_method_id',
      'description' : 'A list of ids of catalog methods used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_catalog_result_key',
      'description' : 'A list of ids of catalog result keys used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_catalog_result_table',
      'description' : 'A list of ids of catalog result tables used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_site_property_id',
      'description' : 'A list of ids of site properties used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_base_category',
      'description' : 'A list of ids of base categories used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_action_path',
      'description' : 'A list of ids of actions used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_extension_id',
      'description' : 'A list of ids of extensions used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_path',
      'description' : 'A list of object paths used by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'template_message_translation',
      'description' : 'A list of message translations by this module',
      'type'        : 'lines',
      'mode'        : 'w',
      'default'     : () },
    { 'id'          : 'publication_url',
      'description' : 'A url on a webdav server which contains the business template source',
      'type'        : 'string',
      'mode'        : 'w', },
    { 'id'          : 'version',
      'description' : 'A version number',
      'type'        : 'string',
      'mode'        : 'w',
      'default'     : '' },
    { 'id'          : 'change_log',
      'description' : 'A change log',
      'type'        : 'text',
      'mode'        : 'w',
      'default'     : '' },
 )

  _categories = ( )
