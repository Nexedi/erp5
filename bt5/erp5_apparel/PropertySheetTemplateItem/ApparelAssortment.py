##############################################################################
#
# Copyright (c) 2002, 2009 Nexedi SA and Contributors. All Rights Reserved.
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



class ApparelAssortment:
  """
    Assortment properties and categories
  """

  _properties = (
    { 'id'          : 'ean13_code',
      'description' : 'The EAN 13 code of this apparel model',
      'type'        : 'string',
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
  )

  #_categories = ( 'eip', 'collection', 'destination', 'taille', 'nomenclature_douane', 'specialise' )
  _categories = ( 'tariff_nomenclature', )

  _constraints = (
  )
