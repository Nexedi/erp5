##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                         Fabien Morin <fabien@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

class CredentialOrganisationProperties:
  """
    Used to store properties related to organisation
  """

  _properties = (
    # Acquisition
    { 'id'          : 'organisation_default_address',
      'storage_id'  : 'organisation_default_address',
      'description' : 'The organisation address of the person',
      'type'        : 'content',
      'portal_type' : ('Address'),
      'acquired_property_id'      : ( 'text', 'street_address', 'city',
                                     'zip_code', 'region', 'region_title',
                                     'prefecture'),
      'acquisition_base_category' : ('region', ),
      'acquisition_portal_type'   : ('Category',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 1,
      'acquisition_sync_value'    : 0,
      'acquisition_accessor_id'   : 'getDefaultAddressValue',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'organisation_default_telephone',
      'storage_id'  : 'organisation_default_telephone',
      'description' : 'The organisation phone of the person',
      'type'        : 'content',
      'portal_type' : ('Telephone'),
      'acquired_property_id'      : ( 'text', 'telephone_number' ),
      'acquisition_base_category' : ('region', ),
      'acquisition_portal_type'   : ('Category',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 1,
      'acquisition_sync_value'    : 0,
      'acquisition_accessor_id'   : 'getDefaultTelephoneValue',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'organisation_title',
      'description' : '',
      'type'        : 'string',
      'translatable'  : 1,
      'translation_domain' : 'erp5_content',
      'default'     : '',
      'acquisition_base_category': (),
      'acquisition_portal_type': (),
      'acquisition_copy_value': 0,
      'acquisition_mask_value': 1,
      'acquisition_accessor_id': 'getTitle',
      'acquisition_depends': None,
      'mode'        : 'w' },
    { 'id'          : 'organisation_description',
      'description' : '',
      'default'     : '',
      'type'        : 'text',
      'mode'        : 'w' },
  )


  _categories = ('question', )
