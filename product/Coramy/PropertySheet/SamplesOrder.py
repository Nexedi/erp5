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


class SamplesOrder:
  """
    Samples order properties and categories
  """
  
  _properties = (
    { 'id'          : 'buyer_title',
      'description' : 'nom de l acheteur',
      'type'        : 'string',
      'acquisition_base_category' : ('contact',),
      'acquisition_portal_type'   : ('Person',),
      'acquisition_copy_value'    : 0,
      'acquisition_mask_value'    : 0,
      'acquisition_accessor_id'   : 'getTitle',
      'acquisition_depends'       : None,
      'mode'        : 'w' },
    { 'id'          : 'commentaires',
      'description' : 'Commentaires',
      'type'        : 'text',
      'mode'        : 'w' },
    { 'id'          : 'date_rdv',
      'description' : 'Date du rendez-vous',
      'type'        : 'date',
      'mode'        : 'w' },
    { 'id'          : 'rayon',
      'description' : 'Rayon',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'themes',
      'description' : 'Themes',
      'type'        : 'text',
      'mode'        : 'w' },
  )

  _categories = ('contact', 'collection', 'commande_origine', 'samples_order_type')
