##############################################################################
#
# Copyright (c) 2003-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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

from Products.ERP5.PropertySheet.Path import Path


class Assignment(Path):
  """
    These properties are used by Career and Assignment
  """

  _properties = (
    { 'id'          : 'salary_coefficient'
    , 'description' : 'A coefficient related to the salary classification of the person'
    , 'type'        : 'int'
    , 'mode'        : 'w'
    },
    { 'id'          : 'collective_agreement_title'
    , 'description' : 'A title that identify the collective agreement of this person in the case of employee/employer relation'
    , 'type'        : 'string'
    , 'mode'        : 'w'
    },
  )

  _categories = ( # Career categories
                , 'grade', 'role', 'skill', 'subordination', 'salary_level', 'product_line',
                  # Assignment and Career categories
                , 'group', 'site', 'function', 'activity'
                )