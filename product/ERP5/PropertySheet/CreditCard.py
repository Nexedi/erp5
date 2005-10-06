##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Alexandre Boeglin  <alex@boeglin.org>
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

class CreditCard:
  """
      Properties for CreditCard Objects
  """

  _properties = (
    {'id'          : 'card_number',
     'description' : 'The 16 digits card number',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'stop_date',
     'description' : 'The expiry date of the card',
     'type'        : 'date',
     'mode'        : 'w'
    },
    {'id'          : 'cardholder_name',
     'description' : "The cardholder's name as it appears on the card",
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'security_key',
     'description' : 'The 3 digits code at the back of the card (CVV2'\
         ' or CVC)',
     'type'        : 'string',
     'mode'        : 'w'
    },
  )

  _categories = ( 'creditcard_type', )
