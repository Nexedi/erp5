##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#
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


class SampleOrderLine:
  """
    Sample order line properties and categories
  """
  
  _properties = (
        {   'id'          : 'destination_reference',
            'storage_id'  : 'default_destination_reference', # Compatibility
            'description' : 'The references of the resource for default destinations',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'coef_marge',
            'description' : 'Coefficient de marge',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'coef_majoration',
            'description' : 'Coefficient de majoration de prix',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'cout_additionnel',
            'description' : 'Cout additionnel en euros',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'theme',
            'description' : 'Theme',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'sort_index',
            'description' : 'sort_index',
            'type'        : 'int',
            'mode'        : 'w' },
        {   'id'          : 'theme_index',
            'description' : 'theme_index',
            'type'        : 'int',
            'mode'        : 'w' },
  )

  _categories = ('tarif',)
