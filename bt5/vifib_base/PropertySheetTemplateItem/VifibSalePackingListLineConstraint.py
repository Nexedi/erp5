##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
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

message = 'There should be exactly one ${portal_type} present in Items'
class VifibSalePackingListLineConstraint:
  """Constraints for Sale Packing List Line in Vifib"""
  _constraints = (
    { 'id'            : 'sale_packing_list_line_aggregate_computer_partition',
      'condition'     : 'python: object.getResourceValue() is not None and object.getResource() in [object.portal_preferences.getPreferredInstanceSetupResource(), object.portal_preferences.getPreferredInstanceHostingResource(), object.portal_preferences.getPreferredInstanceCleanupResource()]',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Computer Partition', 'Slave Partition'),
      'base_category' : ('aggregate'),
      'message_arity_with_portal_type_too_small': message,
      'message_arity_with_portal_type_not_in_range': message,
    },
    { 'id'            : 'sale_packing_list_line_aggregate_hosting_subscription',
      'condition'     : 'python: object.getResourceValue() is not None and object.getResource() in [object.portal_preferences.getPreferredInstanceSetupResource(), object.portal_preferences.getPreferredInstanceHostingResource(), object.portal_preferences.getPreferredInstanceCleanupResource()]',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : 'Hosting Subscription',
      'base_category' : ('aggregate'),
      'message_arity_with_portal_type_too_small': message,
      'message_arity_with_portal_type_not_in_range': message,
    },
    { 'id'            : 'sale_packing_list_line_aggregate_software_instance',
      'condition'     : 'python: object.getResourceValue() is not None and object.getResource() in [object.portal_preferences.getPreferredInstanceSetupResource(), object.portal_preferences.getPreferredInstanceHostingResource(), object.portal_preferences.getPreferredInstanceCleanupResource()]',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : 'Software Instance',
      'base_category' : ('aggregate'),
      'message_arity_with_portal_type_too_small': message,
      'message_arity_with_portal_type_not_in_range': message,
    },
    { 'id'            : 'sale_packing_list_line_aggregate_software_release',
      'condition'     : 'python: object.getResourceValue() is not None and object.getResource() in [object.portal_preferences.getPreferredInstanceSetupResource(), object.portal_preferences.getPreferredInstanceHostingResource(), object.portal_preferences.getPreferredInstanceCleanupResource()]',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : 'Software Release',
      'base_category' : ('aggregate'),
      'message_arity_with_portal_type_too_small': message,
      'message_arity_with_portal_type_not_in_range': message,
    },
  )
