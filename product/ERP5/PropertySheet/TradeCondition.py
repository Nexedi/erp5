##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#          Thierry Faucher <Thierry_Faucher@coramy.com>
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


class TradeCondition:
  """
    Trade Conditions are used to store the conditions (payment, logistic,...)
    which should be applied (and used in the orders) when two companies make
    business together
  """

  _properties = (
        {   'id'          : 'source_decision_destination_reference',
            'description' : 'The reference of the source_decision for'+
                            ' default destination',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'destination_decision_source_reference',
            'description' : 'The reference of the destination_decision'+
                            ' for default source',
            'type'        : 'string',
            'mode'        : 'w' },

        # Subordination properties
        { 'id'          : 'payment_condition',
          'storage_id'  : 'default_payment_condition',
          'description' : 'The current payment condition.',
          'type'        : 'content',
          'portal_type' : ('Payment Condition',),
          'acquired_property_id' : ( 'payment_mode', 'payment_mode_title',
                                     'trade_date', 'trade_date_title',
                                     'payment_term', 'payment_additional_term',
                                     'payment_end_of_month', 'payment_date',
                                     'quantity', 'efficiency',
                                     'source_payment',
                                     'source_payment_value',
                                     'source_payment_title',
                                     'destination_payment',
                                     'destination_payment_value',
                                     'destination_payment_title',
                                   ),
          'mode'        : 'w' },
  )

  _categories = ( 'group', 'activity', 'incoterm',
                  'price_currency', 'delivery_mode',
                  'trade_condition_type',  )

