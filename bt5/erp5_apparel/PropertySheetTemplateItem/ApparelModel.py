##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
#          Romain Courteaud <romain@nexedi.com>
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



class ApparelModel:
  """
    Apparel model properties and categories
  """

  _properties = (
    { 'id'          : 'accessory_description', # XXX
      'description' : 'accessories description',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'apparel_colour_range_title',
      'description' : 'the apparel pallet of the model',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Colour Range',),
      'acquisition_copy_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'apparel_shape_title',
      'description' : 'the apparel shape of the model',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Shape',),
      'acquisition_copy_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'apparel_cloth_title',
      'description' : 'title of the apparel clothes used',
      'type'        : 'lines',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Cloth',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'margin_ratio', ### XXX
      'description' : 'Margin coefficient',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'price_increase_coefficient', # XXX ratio
      'description' : 'Price increase coefficient',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'extra_cost',
      'description' : 'Extra cost in euros',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'ean13_code',
      'description' : 'The EAN 13 code of this apparel model',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'quilting_time',
      'description' : 'quilting time for the apparel model',
      'type'        : 'float',
      'mode'        : 'w' },
    { 'id'          : 'apparel_model_template_title',
      'description' : 'Apparel model template title',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Model',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'apparel_size_title',
      'description' : 'Title of the apparel correspondence sizes used',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Size',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'apparel_measurement_title',
      'description' : 'Title of the apparel measurement used',
      'type'        : 'string',
      'acquisition_base_category' : ('specialise',),
      'acquisition_portal_type'   : ('Apparel Measurement',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    # Override default value XXX
    {   'id'          : 'p_variation_base_category',
        'description' : 'A list of base categories which define possible discrete variations. '\
                        'Price ranges are stored as category membership. '\
                        '(prev. variation_category_list).',
        'type'        : 'lines',
        'default'     : ['colour'],
        'mode'        : 'w' },
  )

  _categories = ( 'composition', 'transformation_state', 'pricing', 'origin', 'brand', 'tariff_nomenclature' )
  #_categories = ( 'transformation_state', 'apparel_pricing', 'apparel_creation_type', 'brand', 'tariff_nomenclature' )
                  #     XXXXXXX              XXXX                XXXX   apparel_model_creation_type                        (As in Brussels Tariff Nomenclature)               

  _constraints = (
    { 'id'            : 'apparel_shape',
      'description'   : 'There must at most one Apparel Shape',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '0',
      'max_arity'     : '1',
      'portal_type'   : ('Apparel Shape',),
      'base_category' : ('specialise',)
     },
    { 'id'            : 'apparel_pallet',
      'description'   : 'There must at most one Apparel Colour Range',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '0',
      'max_arity'     : '1',
      'portal_type'   : ('Apparel Colour Range',),
      'base_category' : ('specialise',)
     },
  )
