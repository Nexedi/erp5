##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#          Thierry Faucher <Thierry_Faucher@coramy.com>
# Copyright (c) 2004 - 2009 Nexedi SA and Contributors. All Rights Reserved.
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


class ApparelCloth:
  """
    ApparelCloth properties and categories
  """

  _properties = (
        {   'id'          : 'cad_library',
            'description' : 'library name containing the lectra files',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'base_size',
            'description' : 'size by default',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'apparel_shape_title',
            'description' : 'Titles of the compatibles apparel shapes ',
            'type'        : 'lines',
            'acquisition_base_category' : ('specialise',),
            'acquisition_portal_type'   : ('Apparel Shape',),
            'acquisition_copy_value'    : 0,
            'acquisition_mask_value'    : 0,
            'acquisition_accessor_id'   : 'getTitle',
            'acquisition_depends'       : None,
            'mode'        : 'w' },
        {   'id'          : 'apparel_measurement_title',
            'description' : 'Titles of the apparel measurement associated',
            'type'        : 'lines',
            'acquisition_base_category' : ('specialise',),
            'acquisition_portal_type'   : ('Apparel Measurement',),
            'acquisition_copy_value'    : 0,
            'acquisition_mask_value'    : 0,
            'acquisition_accessor_id'   : 'getTitle',
            'acquisition_depends'       : None,
            'mode'        : 'w' },
      )
