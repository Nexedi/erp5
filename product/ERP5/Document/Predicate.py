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
from Products.ERP5Type.Utils import convertToUpperCase

from zLOG import LOG

class Predicate(Folder):
  """
    A Predicate object defines a list of criterions
    which can be applied to test a document or to search for documents.
    
    Predicates are defined by a combination of PropertySheet values
    (ex. membership_criterion_list) and criterion list (ex. quantity 
    is between 0 and 10). An additional script can be associated to 
    extend the standard Predicate semantic with any additional 
    script based test.
    
    The idea between Predicate in ERP5 is to have a simple 
    way of defining simple predicates which can be later
    searched through a simplistic rule based engine and which can 
    still provide complete expressivity through additional scripting.
    
    The approach is intended to provide the expressivity of a rule
    based system without the burden of building a fully expressive 
    rule engine.
  """
  meta_type = 'ERP5 Predicate'
  portal_type = 'Predicate'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isPredicate = 1
  
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

  def test(self, context, **kw):
    """
      A Predicate can be tested on a given context.
      Parameters can passed in order to ignore some conditions.
    """
    self = self.asPredicate()
    result = 1
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
    # LOG('PREDICATE TEST', 0, 'testing %s on context of %s' % (self.getRelativeUrl(), context.getRelativeUrl()))
    for property, value in self._identity_criterion.items():
      result = result and (context.getProperty(property) == value)
      # LOG('predicate test', 0, '%s after prop %s : %s == %s' % (result, property, context.getProperty(property), value))
    for property, (min, max) in self._range_criterion.items():
      value = context.getProperty(property)
      if min is not None:
        result = result and (value >= min)
        # LOG('predicate test', 0, '%s after prop %s : %s >= %s' % (result, property, value, min))
      if max is not None:
        result = result and (value < max)
        # LOG('predicate test', 0, '%s after prop %s : %s < %s' % (result, property, value, max))
    multimembership_criterion_base_category_list = self.getMultimembershipCriterionBaseCategoryList()
    membership_criterion_base_category_list = self.getMembershipCriterionBaseCategoryList()
    tested_base_category = {}
    # LOG('predicate test', 0, 'categories will be tested in multi %s single %s as %s' % (multimembership_criterion_base_category_list, membership_criterion_base_category_list, self.getMembershipCriterionCategoryList()))
    for c in self.getMembershipCriterionCategoryList():
      bc = c.split('/')[0]
      if not bc in tested_base_category.keys() and bc in multimembership_criterion_base_category_list:
        tested_base_category[bc] = 1
      elif not bc in tested_base_category.keys() and bc in membership_criterion_base_category_list:
        tested_base_category[bc] = 0
      if bc in multimembership_criterion_base_category_list:
        tested_base_category[bc] = tested_base_category[bc] and context.isMemberOf(c)
        # LOG('predicate test', 0, '%s after multi membership to %s' % (tested_base_category[bc], c))
      elif bc in membership_criterion_base_category_list:
        tested_base_category[bc] = tested_base_category[bc] or context.isMemberOf(c)
        # LOG('predicate test', 0, '%s after single membership to %s' % (tested_base_category[bc], c))
    result = result and (0 not in tested_base_category.values())
    # LOG('predicate test', 0, '%s after category %s ' % (result, tested_base_category.items()))
    # Test method calls
    test_method_id = self.getTestMethodId()
    if test_method_id is not None and result:
      method = getattr(context,test_method_id)
      result = result and method()
    # LOG('predicate test', 0, '%s after method %s ' % (result, test_method_id))
    # XXX Add here additional method calls
    return result

  def asSqlExpression():
    """
      A Predicate can be rendered as an SQL expression. This
      can be used to generate SQL requests in reports or in
      catalog search queries.
      
      XXX - This method is not implemented yet
    """
    pass

  security.declareProtected( Permissions.AccessContentsInformation, 'getCriterionList' )
  def getCriterionList(self, **kw):
    """
      Returns the list of criteria which are defined by the Predicate.
      
      Each criterion is returned in a TempBase instance intended to be
      displayed in a ListBox.
      
      XXX - It would be better to return criteria in a Criterion class
            instance            
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
    """
      This methods sets parameters of a criterion. There is at most one
      criterion per property. Defined parameters are
      
      identity -- if not None, allows for testing identity of the property
                  with the provided value
    
      min      -- if not None, allows for testing that the property
                  is greater than min
    
      max      -- if not None, allows for testing that the property
                  is greater than max
    
    """
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
    if identity != None :
      self._identity_criterion[property] = identity
    if min != '' or max != '' :
      self._range_criterion[property] = (min, max)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  def edit(self, **kwd):
    """
      The edit method is overriden so that any time a
      criterion_property_list property is defined, a list of criteria
      is created to match the provided criterion_property_list.
    """
    if not hasattr(aq_base(self), '_identity_criterion'):
      self._identity_criterion = {}
      self._range_criterion = {}
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
    """
      This method updates a Predicate by implementing an
      AND operation on all predicates (or categories)
      provided in category_list. Categories behave as a
      special kind of predicate which only acts on category
      membership.
      
      WARNING: this method does not take into account scripts at 
      this point.
    """
    category_tool = aq_inner(self.portal_categories)
    base_category_id_list = category_tool.objectIds()
    membership_criterion_category_list = []
    membership_criterion_base_category_list = []
    multimembership_criterion_base_category_list = []
    test_method_id_list = []
    criterion_property_list = []
    # reset criterions
    self._identity_criterion = {}
    self._range_criterion = {}
    
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
          test_method_id_list += list(predicate_value.getTestMethodIdList() or [])
          for p in predicate_value.getCriterionList():
            self.setCriterion(p.property, identity=p.identity, min=p.min, max=p.max)
    self.setCriterionPropertyList(criterion_property_list)
    self._setMembershipCriterionCategoryList(membership_criterion_category_list)
    self._setMembershipCriterionBaseCategoryList(membership_criterion_base_category_list)
    self._setMultimembershipCriterionBaseCategoryList(multimembership_criterion_base_category_list)
    self._setTestMethodIdList(test_method_id_list)
    self.reindexObject()

  def generatePredicate(self,multimembership_criterion_base_category_list=(),
                        membership_criterion_base_category_list=(),
                        criterion_property_list=()):
    """
    This method generates a new temporary predicate based on an ad-hoc 
    interpretation of local properties of an object. For example,
    a start_range_min property will be interpreted as a way to define 
    a min criterion on start_date.

    The purpose of this method is to be called from 
    a script called PortalType_asPredicate to ease the generation of
    Predicates based on range properties. It should be considered mostly
    as a trick to simplify the development of Predicates and forms.
    """
    new_membership_criterion_category_list = list(self.getMembershipCriterionCategoryList())
    new_multimembership_criterion_base_category_list = list(self.getMultimembershipCriterionBaseCategoryList())
    for base_category in multimembership_criterion_base_category_list:
      category_list = self.getProperty(base_category + '_list')
      if category_list is not None and len(category_list)>0:
        for category in category_list:
          new_membership_criterion_category_list.append(base_category + '/' + category)
        if base_category not in new_multimembership_criterion_base_category_list:
          new_multimembership_criterion_base_category_list.append(base_category)
    for base_category in membership_criterion_base_category_list:
      category_list = self.getProperty(base_category + '_list')
      if category_list is not None and len(category_list)>0:
        for category in category_list:
          new_membership_criterion_category_list.append(base_category + '/' + category)
        if base_category not in new_membership_criterion_base_category_list:
          new_membership_criterion_base_category_list.append(base_category)
    new_criterion_property_list =  list(self.getCriterionPropertyList())
    identity_criterion = getattr(self,'_identity_criterion',{})
    range_criterion = getattr(self,'_range_criterion',{})
    # Look at local properties and make it criterion properties
    for property in criterion_property_list:
      if property not in self.getCriterionPropertyList() \
        and property in self.propertyIds():
          new_criterion_property_list.append(property)
          property_min = property + '_range_min'
          property_max = property + '_range_max'
          if hasattr(self,'get%s' % convertToUpperCase(property)) \
            and self.getProperty(property) is not None:
            identity_criterion[property] = self.getProperty(property)
          elif hasattr(self,'get%s' % convertToUpperCase(property_min)):
            min = self.getProperty(property_min)
            max = self.getProperty(property_max)
            range_criterion[property] = (min,max)
    # Return a new context with new properties, like if
    # we have a predicate with local properties
    new_self = self.asContext(
        membership_criterion_category=new_membership_criterion_category_list,
        multimembership_criterion_base_category=new_multimembership_criterion_base_category_list,
        criterion_property_list=new_criterion_property_list,
        _identity_criterion=identity_criterion,
        _range_criterion=range_criterion)

    return new_self

  # Predicate handling
  security.declareProtected(Permissions.AccessContentsInformation, 'asPredicate')
  def asPredicate(self,script_id=None):
    """
      This method tries to convert the current Document into a predicate
      looking up methods named Class_asPredictae, MetaType_asPredicate, PortalType_asPredicate
    """
    script = self._getTypeBasedMethod('asPredicate', script_id=script_id)
    if script is not None:
      return script()
    return self
