##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from Products.ERP5Type.Base import Base

from Predicate import Predicate

class ComplementPredicate(Base, Predicate):
  """
    The other predicate makes the complement
  """
  meta_type = 'ERP5 Complement Predicate'
  portal_type = 'Complement Predicate'
  add_permission = Permissions.AddERP5Content
  isPortalContent = 1
  isRADContent = 1

  _operators = []

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.Predicate
                    )

  # Declarative interfaces
  __implements__ = ( Interface.Predicate )

  # Factory Type Information
  factory_type_information = \
    {    'id'             : portal_type
       , 'meta_type'      : meta_type
       , 'description'    : """\
A bank account number holds a collection of numbers
and codes (ex. SWIFT, RIB, etc.) which may be used to
identify a bank account."""
       , 'icon'           : 'predicate_icon.gif'
       , 'product'        : 'ERP5'
       , 'factory'        : 'addValuePredicate'
       , 'immediate_view' : 'predicate_view'
       , 'actions'        :
      ( { 'id'            : 'view'
        , 'name'          : 'View'
        , 'category'      : 'object_view'
        , 'action'        : 'predicate_view'
        , 'permissions'   : (
            Permissions.View, )
        }
        ,
      )
    }

  def test(self, context):
    """
      A Predicate can be tested on a given context
    """
    pass

  def asPythonExpression():
    """
      A Predicate can be rendered as a python expression. This
      is the preferred approach within Zope.
    """
    pass

  def asSqlExpression():
    """
      A Predicate can be rendered as a python expression. This
      is the preferred approach within Zope.
    """
    pass
