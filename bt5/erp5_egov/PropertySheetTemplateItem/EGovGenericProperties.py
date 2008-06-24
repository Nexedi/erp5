#############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
#                         Fabien Morin <fabien@nexedi.com> 
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


class EGovGenericProperties:
  """
    Autorisation properties and categories
  """

  _properties = (
    # Autorisation properties
    { 'id'         : 'corporate_registration_code'
    , 'description': 'The corporate registration code of this organisation'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'                       : 'birthplace'
    , 'storage_id'               : 'default_birthplace'
    , 'description'              : 'The current address of the person'
    , 'type'                     : 'content'
    , 'portal_type'              : ( 'Address', )
    , 'acquired_property_id'     : ( 'text', 'street_address', 'city',
                                     'zip_code', 'region', 'region_title')
    , 'acquisition_base_category': ( 'subordination', )
    , 'acquisition_portal_type'  : ( 'Organisation', )
    , 'acquisition_copy_value'   : 0
    , 'acquisition_mask_value'   : 1
    , 'acquisition_sync_value'   : 0
    , 'acquisition_accessor_id'  : 'getDefaultBirthplaceValue'
    , 'acquisition_depends'      : None
    , 'mode'                     : 'w'
    },
  )
