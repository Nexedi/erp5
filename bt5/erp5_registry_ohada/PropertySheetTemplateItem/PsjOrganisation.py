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



class PsjOrganisation:
  """
    Organisation properties and categories
  """

  _properties = (
   
    # Amortisation
      { 'id'          : 'creation',
      'description' : 'Préciser si l origine du fonds de commerce est la création',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : 0 },  
      { 'id'         : 'org_modification_date',
      'description': 'date de modification',
      'type'       : 'date',
      'mode'       : 'w',
      },
      { 'id'          : 'purchase',
      'description' : 'Préciser si l origine du fonds de commerce est l achat ',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : 0 },
      { 'id'          : 'contribution',
      'description' : 'Préciser si l origine du fonds de commerce est l apport ',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : 0 },
      { 'id'          : 'other',
      'description' : 'Préciser si l origine du fonds de commerce est une quelconque autre raison',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : 0 },
      { 'id'          : 'other_reason',
      'description' : 'Donner une description de l autre raison de l origine du fonds de commerce  ',
      'type'        : 'string',
      'mode'        : 'w'},
      { 'id'          : 'social_capital',
      'description' : 'Capital Social',
      'type'        : 'string',
      'mode'        : 'w'},
      { 'id'          : 'sign',
      'description' : 'Sign',
      'type'        : 'string',
      'mode'        : 'w'},
      { 'id'          : 'acronym',
      'description' : 'Acronym',
      'type'        : 'string',
      'mode'        : 'w'},
   )

  _categories = ( 'role', 'group', 'activity', 'skill', 'market_segment', 
                  'region', 'social_form', 'function', 'price_currency', 
                  'economical_class', 'site', )
