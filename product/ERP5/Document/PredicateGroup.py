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
from Acquisition import aq_base, aq_inner

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type.Document import newTempBase

from Products.ERP5.Document.Predicate import Predicate
from zLOG import LOG

class PredicateGroup(Folder, Predicate):
  """
    A predicate group allows to combine simple predicates
  """
  meta_type = 'ERP5 Predicate Group'
  portal_type = 'Predicate Group'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  is_predicate = 1

  _operators = (
    {
      'id':               'AND',
      'title':            'And',
      'description':      'All predicates must be true',
      'sql_operator':     '=',
      'python_operator':  '==',
    },
    {
      'id':               'OR',
      'title':            'OR',
      'description':      'Some predicate must be true',
      'sql_operator':     '<>',
      'python_operator':  '!=',
    },
    {
      'id':               'NOR',
      'title':            'NOR',
      'description':      'All predicates must be false',
      'sql_operator':     '>',
      'python_operator':  '>',
    },
    {
      'id':               'NAND',
      'title':            'NAND',
      'description':      'Some predicate must be false',
      'sql_operator':     '<',
      'python_operator':  '<',
    },
    {
      'id':               'XOR',
      'title':            'XOR',
      'description':      'Only one predicate can be true',
      'sql_operator':     '>=',
      'python_operator':  '>=',
    },
  )

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.Predicate
                    , PropertySheet.SortIndex
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
       , 'factory'        : 'addPredicateGroup'
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
    result = 1
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
    for property, value in self._identity_criterion.items():
      result = result and (context.getProperty(property) == value)
    for property, (min, max) in self._range_criterion.items():
      value = context.getProperty(property)
      if min is not None:
        result = result and (value >= min)
      if max is not None:
        result = result and (value < max)
    multimembership_criterion_base_category_list = self.getMultimembershipCriterionBaseCategoryList()
    membership_criterion_base_category_list = self.getMembershipCriterionBaseCategoryList()
    tested_base_category = {}
    for c in self.getMembershipCriterionCategoryList():
      bc = c.split('/')[0]
      if not bc in tested_base_category.keys() :
        tested_base_category[bc] = 0
      if bc in multimembership_criterion_base_category_list:
        tested_base_category[bc] = tested_base_category[bc] and context.isMemberOf(c)
      elif bc in membership_criterion_base_category_list:
        tested_base_category[bc] = tested_base_category[bc] or context.isMemberOf(c)
    result = result and (0 not in tested_base_category.values())
    # Test method calls
    test_method_id = self.getTestMethodId()
    if test_method_id is not None and result:
      method = getattr(context,method)
      result = result and method()
    # XXX Add here additional method calls
    return result

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

  security.declareProtected( Permissions.AccessContentsInformation, 'getCriterionList' )
  def getCriterionList(self, **kw):
    """
      Returns a list of criterion
    """
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
    criterion_dict = {}
    for p in self.getCriterionPropertyList():
      criterion_dict[p] = newTempBase(self, 'new_%s' % p)
      criterion_dict[p].identity = self._identity_criterion.get(p, None)
      criterion_dict[p].uid = 'new_%s' % p
      criterion_dict[p].property = p
      criterion_dict[p].min = self._range_criterion.get(p, (None, None))[0]
      criterion_dict[p].max = self._range_criterion.get(p, (None, None))[1]
    criterion_list = criterion_dict.values()
    criterion_list.sort()
    return criterion_list

  security.declareProtected( Permissions.ModifyPortalContent, 'setCriterion' )
  def setCriterion(self, property, identity=None, min=None, max=None, **kw):
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
    if identity != [] :
      self._identity_criterion[property] = identity
    if min != '' or max != '' :
      self._range_criterion[property] = (min, max)

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  def edit(self, **kwd) :
    if 'criterion_property_list' in kwd.keys() :
      criterion_property_list = kwd['criterion_property_list']
      identity_criterion = {}
      range_criterion = {}
      for criterion in self._identity_criterion.keys() :
        if criterion in criterion_property_list :
          identity_criterion[criterion] = self._identity_criterion[criterion]
      for criterion in self._range_criterion.keys() :
        if criterion in criterion_property_list :
          range_criterion[criterion] = self._range_criterion[criterion]
      self._identity_criterion = identity_criterion
      self._range_criterion = range_criterion
    return self._edit(**kwd)

  # Predicate fusion method
  def setPredicateCategoryList(self, category_list):
    category_tool = aq_inner(self.portal_categories)
    base_category_id_list = category_tool.objectIds()
    membership_criterion_category_list = []
    membership_criterion_base_category_list = []
    multimembership_criterion_base_category_list = []
    criterion_property_list = []
    for c in category_list:
      bc = c.split('/')[0]
      if bc in base_category_id_list:
        # This is a category
        membership_criterion_category_list.append(c)
        membership_criterion_base_category_list.append(bc)
      else:
        predicate_value = category_tool.resolveCategory(c)
        if predicate_value is not None:
          criterion_property_list.extend(predicate_value.getCriterionPropertyList())
          membership_criterion_category_list.extend(
                      predicate_value.getMembershipCriterionCategoryList())
          membership_criterion_base_category_list.extend(
                      predicate_value.getMembershipCriterionBaseCategoryList())
          multimembership_criterion_base_category_list.extend(
                      predicate_value.getMultimembershipCriterionBaseCategoryList())
          for p in predicate_value.getCriterionList():
            self.setCriterion(p.property, identity=p.identity, min=p.min, max=p.max)
    self.setCriterionPropertyList(criterion_property_list)
    self.setMembershipCriterionCategoryList(membership_criterion_category_list)
    self.setMembershipCriterionBaseCategoryList(membership_criterion_base_category_list)
    self.setMultimembershipCriterionBaseCategoryList(multimembership_criterion_base_category_list)
    self.reindexObject()

  # Predicate handling
  security.declareProtected(Permissions.AccessContentsInformation, 'asPredicate')
  def asPredicate(self):
    """
    Returns a temporary Predicate based on the Resource properties
    """
    return self

