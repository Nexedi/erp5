##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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

from Products.CMFCore.Expression import Expression

class PaySheetModelLine:
  """
    Properties for Pay Sheet Model Lines.
  """
  _properties = (
    { 'id'          : 'editable',
      'description' : 'If set to 1, the Pay Sheet Line values could be edited'
                      ' at the Pay Sheet calculation step',
      'type'        : 'boolean',
      'mode'        : 'w' 
    },
    { 'id'          : 'create_paysheet_line',
      'description' : 'A flag indicating if the corresponding paysheet line will'
                      ' be created',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : True,
    },
    { 'id'          : 'calculation_script_id',
      'description' : 'If no script found on Pay Sheet Model Lines, this'
                      ' script is used to do localised calculs',
      'type'        : 'string',
      'mode'        : 'w',
    },
    { 'id'          : 'source_annotation_line_reference',
      'description' : 'The Payroll Service Provider will be the one defined in'
                      ' the Annotation Line with this reference.',
      'type'        : 'string',
      'mode'        : 'w',
    },
  )


  _categories = ( 'tax_category', 'grade', 'base_amount', 'salary_range')
