##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface

from Products.ERP5.Document.Predicate import Predicate

class Domain(Predicate):
  """
    An abstract class subclassed by reports and mapped values

    Structure is:
       - base domain (like base category)
       - sub domain (like category)
       
    Allows to define ranges:
       - price between X and Y
       - portal_type in (a, b, c)
       - price between X and Y and region in (a, b, c)
       
    Reports:
       - listbox allows to produce reports
         - output to html, pdf or ooffice
         - definition through the web (ie. which field in which column, which statistics)
         - definition of selection (to list)
         - ability for use to "save" favourite report (user reports)
         - library of favourite reports (global reports)
       - matrixbox allows to produce reports       
         - output to html, pdf or ooffice
         - definition through the web (ie. which base_category or base_domain in which axis)
         - definition of selection (to map to matrix)
         - ability for use to "save" favourite report (user reports)
         - library of favourite reports (global reports)
  """
  meta_type = 'ERP5 Domain'
  portal_type = 'Domain'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 0
  isRADContent = 0

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  __implements__ = ( Interface.Predicate, )
