##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

class Opposition:
    """Properties for Opposition (Factoring)
    """

    _properties = (
        {   'id'          : 'initial_quantity',
            'description' : 'The initial quantity, before final decision is'\
                            ' made.',
            'type'        : 'float',
            'mode'        : 'w' },
     
        {   'id'          : 'maximal_quantity_per_operation',
            'description' : 'The maximal quantity that can be "opposed" per'\
                            ' operation',
            'type'        : 'float',
            'default'     : None,
            'acquisition_base_category'     : (),
            'acquisition_portal_type'       : (),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_depends'           : None,
            'acquisition_accessor_id'       : 'getMaximalQuantityPerOperation',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('getQuantity', ),
            'mode'        : 'w' },
        
        {   'id'          : 'invoice_reference', # -> NUMFACT
            'description' : 'Reference of the invoice',
            'type'        : 'string',
            'mode'        : 'w' },
    )
    
    _categories = ( 'origin',
                    'market', # market_free_text -> NUMCON
                    'intervention', # intervention_free_text -> CLEPAR
                    'order', # order_free_text -> NOCOMM
                  )
    _constraints = (
      { 'id'            : 'origin_category_existence',
        'description'   : 'Opposition Type must be set',
        'type'          : 'CategoryMembershipArity',
        'min_arity'     : '1',
        'max_arity'     : '1',
        'portal_type'   : ('Category', ),
        'base_category' : ('origin', )
      },
      { 'id'            : 'source_section_existence',
        'description'   : 'Creditor must be set',
        'type'          : 'CategoryMembershipArity',
        'min_arity'     : '1',
        'max_arity'     : '1',
        'portal_type'   : ('Organisation', 'Person' ),
        'base_category' : ('source_section', )
      },
      { 'id'            : 'destination_section_existence',
        'description'   : 'Factor must be set',
        'type'          : 'CategoryMembershipArity',
        'min_arity'     : '1',
        'max_arity'     : '1',
        'portal_type'   : ('Organisation', 'Person' ),
        'base_category' : ('destination_section', )
      },
      { 'id'            : 'destination_account_existence',
        'description'   : 'Destination Account must be set',
        'type'          : 'CategoryMembershipArity',
        'min_arity'     : '1',
        'max_arity'     : '1',
        'portal_type'   : ('Account', ),
        'base_category' : ('destination', )
      },
      { 'id'            : 'quantity_consistency',
        'description'   : 'Quantity must be consistent',
        'type'          : 'TALESConstraint',
        'expression'    : 'python: object.getMaximalQuantityPerOperation()'
                          ' <= object.getQuantity()',
      },
      
    )

