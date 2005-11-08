##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.CMFCore.Expression import Expression

class SupplyLine:
  """
    Properties which allow to define a generic Price.
  """
  _properties = (
    {  'id'          : 'base_price',
       'description' : 'A typical per unit base price',
       'type'        : 'float',
       'mode'        : 'w' },
    {  'id'          : 'additional_price',
       'description' : 'A per unit additional price',
       'type'        : 'float',
       'mode'        : 'w' },
    {  'id'          : 'discount_ratio',
       'description' : 'A discount ratio',
       'type'        : 'float',
       'mode'        : 'w' },
    {  'id'          : 'exclusive_discount_ratio',
       'description' : 'A exclusive discount ratio',
       'type'        : 'float',
       'mode'        : 'w' },
    {  'id'          : 'surcharge_ratio',
       'description' : 'A surcharge ratio',
       'type'        : 'float',
       'mode'        : 'w' },
    # Pricing calculation
    # Matrix definition
    # Quantity step
    {  'id'          : 'quantity_step',
       'description' : 'A list of quantity values which define ' \
                       'acceptable ranges',
       'type'        : 'float',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'additional_price_quantity_step',
       'description' : 'A list of quantity values which define ' \
                       'acceptable ranges',
       'type'        : 'float',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'discount_ratio_quantity_step',
       'description' : 'A list of quantity values which define ' \
                       'acceptable ranges',
       'type'        : 'float',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'exclusive_discount_ratio_quantity_step',
       'description' : 'A list of quantity values which define ' \
                       'acceptable ranges',
       'type'        : 'float',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'surcharge_ratio_quantity_step',
       'description' : 'A list of quantity values which define ' \
                       'acceptable ranges',
       'type'        : 'float',
       'multivalued' : 1,
       'mode'        : 'w' },
    # Base category
    {  'id'          : 'p_variation_base_category',
       # XXX Compatibility
       'description' : 'Base category range of matrix',
       'type'        : 'lines',
       'default'     : [],
       'multivalued' : 1,
       'mode'        : 'w' },
#     {  'id'          : 'additional_price_variation_base_category',
#        'description' : 'Base category range of matrix',
#        'type'        : 'float',
#        'multivalued' : 1,
#        'mode'        : 'w' },
    {  'id'          : 'discount_ratio_variation_base_category',
       'description' : 'Base category range of matrix',
       'type'        : 'lines',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'exclusive_discount_ratio_variation_base_category',
       'description' : 'Base category range of matrix',
       'type'        : 'lines',
       'multivalued' : 1,
       'mode'        : 'w' },
    {  'id'          : 'surcharge_ratio_variation_base_category',
       'description' : 'Base category range of matrix',
       'type'        : 'lines',
       'multivalued' : 1,
       'mode'        : 'w' },
#     # Option Matrix
#     {  'id'          : 'optional_additional_price_quantity_step',
#        'description' : 'A list of quantity values which define ' \
#                        'acceptable ranges',
#        'type'        : 'float',
#        'multivalued' : 1,
#        'mode'        : 'w' },
#     {  'id'          : 'optional_discount_ratio_quantity_step',
#        'description' : 'A list of quantity values which define ' \
#                        'acceptable ranges',
#        'type'        : 'float',
#        'multivalued' : 1,
#        'mode'        : 'w' },
#     {  'id'          : 'optional_exclusive_discount_ratio_quantity_step',
#        'description' : 'A list of quantity values which define ' \
#                        'acceptable ranges',
#        'type'        : 'float',
#        'multivalued' : 1,
#        'mode'        : 'w' },
#     {  'id'          : 'optional_surcharge_ratio_quantity_step',
#        'description' : 'A list of quantity values which define ' \
#                        'acceptable ranges',
#        'type'        : 'float',
#        'multivalued' : 1,
#        'mode'        : 'w' },
  )

