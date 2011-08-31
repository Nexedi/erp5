##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
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

class MagentoTestPerson:
  """
      MagentoTestPerson properties for all ERP5 objects
  """

  _properties = (
      {   'id'          : 'email',
          'type'        : 'string',
          'mode'        : 'w' },
      {	  'id'		: 'firstname',
          'type'	: 'string',
          'mode'        : 'w' },
      {	  'id'		: 'lastname',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'customer_id',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'relation',
          'type'	: 'string',
          'mode'	: 'w' },
     {    'id'		: 'telephone',
          'type'	: 'string',
          'mode'	: 'w' },
     {    'id'		: 'fax',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'category',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'customer_address_id',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'street',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'city',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'country_id',
          'type'	: 'string',
          'mode'	: 'w' },
     {	  'id'		: 'postcode',
          'type'	: 'string',
          'mode'	: 'w' },

  )


