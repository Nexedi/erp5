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
from Products.ERP5.Document.SetMappedValue import SetMappedValue as ERP5SetMappedValue

from zLOG import LOG

class SetMappedValue(ERP5SetMappedValue):
  """
    A SetMappedValue allows to associate a value to a domain
    just like a MappedValue but uses a Set predicate instead of
    a PredicateGroup

    It implements apparel specific methods
  """
  meta_type = 'CORAMY Set Mapped Value'
  portal_type = 'Set Mapped Value'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  __implements__ = ( Interface.Predicate )


  # Declarative properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Predicate
                      , PropertySheet.Domain
                      , PropertySheet.Price
                      , PropertySheet.MappedValue
                    )  # We must add price for backwards compatibility (price was r
                       # defined in ERP5 Set Mapped Value

  # Factory Type Information
  factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A bank account number holds a collection of numbers
and codes (ex. SWIFT, RIB, etc.) which may be used to
identify a bank account."""
         , 'icon'           : 'transformed_resource_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addSetMappedValue'
         , 'immediate_view' : 'mapped_value_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'mapped_value_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'mapped_value_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

  def test(self, context):
    """
      A Predicate can be tested on a given context
      Includes id equivalence for certain categories (only
        the trailer id is taken into account)
    """
    result = 1
    for c in self.getPredicateValueList():
      base_category =  c.split('/')[0]
      if base_category in ('coloris', 'morphologie', 'variante'):
        # Classes of equivalences
        category_id = c.split('/')[-1]
        for context_category in context._getCategoryMembershipList(base_category, base=1):
          #result = result and (context_category.find(category_id) >= 0)
          result = result and (context_category.split('/')[-1] == category_id)
      else:
        result = result and self.portal_categories.isMemberOf(context, c)
      #LOG("Test set membership",0, str((c, result)))
    return result

  def asPythonExpression(self):
    """
      A Predicate can be rendered as a python expression. This
      is the preferred approach within Zope.

      XXX BAD
    """
    return "self.portal_categories.isMemberOf(context, '%s')" % self.getCategoryName()

  def asSqlExpression(self):
    """
      A Predicate can be rendered as an sql expression. This
      can be useful to create reporting trees based on the
      ZSQLCatalog

      XXX BAD
    """
    sql_text = '(category_uid = %s AND base_category_uid = %s)' % (self.uid, self.getBaseCategory().uid)
    # Now useless since we precompute the mapping
    #for o in self.objectValues():
    #  sql_text += ' OR %s' % o.asSqlExpression()
    return sql_text


