# -*- coding: utf-8 -*-
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

import itertools
from types import MethodType
import zope.interface
from warnings import warn
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Cache import readOnlyTransactionCache
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply
from Products.CMFCore.Expression import Expression
import six

@zope.interface.implementer( interfaces.IPredicate,)
class Predicate(XMLObject):
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
  isPredicate = ConstantGetter('isPredicate', value=True)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.Predicate
                    , PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    )

  security.declareProtected( Permissions.AccessContentsInformation, 'test' )
  def test(self, context, tested_base_category_list=None,
           strict_membership=0, isMemberOf=None, **kw):
    """
      A Predicate can be tested on a given context.
      Parameters can passed in order to ignore some conditions.

      - tested_base_category_list:  this is the list of category that we do
        want to test. For example, we might want to test only the
        destination or the source of a predicate.
      - if strict_membership is specified, we should make sure that we
        are strictly a member of tested categories
      - isMemberOf can be a function caching results for
        CategoryTool.isMemberOf: it is always called with given 'context' and
        'strict_membership' values, and different categories.
    """
    self = self.asPredicate()
    if self is None:
      # asPredicate returned None, so this predicate never applies.
      # But if we reach this it is because catalog is not up to date.
      return False

    result = 1
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = PersistentMapping()
      self._range_criterion = PersistentMapping()
#    LOG('PREDICATE TEST', 0,
#        'testing %s on context of %s' % \
#        (self.getRelativeUrl(), context.getRelativeUrl()))
    for property, value in six.iteritems(self._identity_criterion):
      if not value:
        continue
      if isinstance(value, (list, tuple)):
        result = context.getProperty(property) in value
      else:
        result = context.getProperty(property) == value
#      LOG('predicate test', 0,
#          '%s after prop %s : %s == %s' % \
#          (result, property, context.getProperty(property), value))
      if not result:
        return result
    for property, (min, max) in six.iteritems(self._range_criterion):
      value = context.getProperty(property)
      if min is not None:
        result = value >= min
#        LOG('predicate test', 0,
#            '%s after prop %s : %s >= %s' % \
#            (result, property, value, min))
        if not result:
          return result
      if max is not None:
        result = value < max
#        LOG('predicate test', 0,
#            '%s after prop %s : %s < %s' % \
#            (result, property, value, max))
        if not result:
          return result
    # Test category memberships. Enable the read-only transaction cache
    # because this part is strictly read-only, and context.isMemberOf
    # is very expensive when the category list has many items.
    membership_criterion_category_list = self.getMembershipCriterionCategoryList()
    if membership_criterion_category_list:
      multimembership_criterion_base_category_list = \
        self.getMultimembershipCriterionBaseCategoryList()
      membership_criterion_base_category_list = \
        self.getMembershipCriterionBaseCategoryList()
      tested_base_category = {}
#      LOG('predicate test', 0,
#          'categories will be tested in multi %s single %s as %s' % \
#         (multimembership_criterion_base_category_list,
#         membership_criterion_base_category_list,
#         self.getMembershipCriterionCategoryList()))
      if isMemberOf is None:
        isMemberOf = context._getCategoryTool().isMemberOf
      with readOnlyTransactionCache():
        for c in membership_criterion_category_list:
          bc = c.split('/', 1)[0]
          if tested_base_category_list is None or bc in tested_base_category_list:
            if bc in multimembership_criterion_base_category_list:
              if not isMemberOf(context, c, strict_membership=strict_membership):
                return 0
            elif bc in membership_criterion_base_category_list and \
                 not tested_base_category.get(bc):
              tested_base_category[bc] = \
                isMemberOf(context, c, strict_membership=strict_membership)
      if 0 in six.itervalues(tested_base_category):
        return 0

    # Test method calls
    test_method_id_list = self.getTestMethodIdList()
    if test_method_id_list is not None :
      for test_method_id in test_method_id_list :
        if test_method_id is not None:
          method = getattr(context,test_method_id)
          try:
            result = method(self)
          except TypeError:
            func_code = method.__code__
            if func_code is None: # BBB Zope2
              func_code = method.func_code
            if func_code.co_argcount != isinstance(method, MethodType):
              raise
            # backward compatibilty with script that takes no argument
            warn('Predicate %s uses an old-style method (%s) that does not'
                 ' take the predicate as argument' % (
               self.getRelativeUrl(), method.__name__), DeprecationWarning)
            result = method()
#          LOG('predicate test', 0,
#              '%s after method %s ' % (result, test_method_id))
          if not result:
            return result
    test_tales_expression = self.getTestTalesExpression()
    if test_tales_expression != 'python: True':
      expression = Expression(test_tales_expression)
      from Products.ERP5Type.Utils import createExpressionContext
      # evaluate a tales expression with the tested value as context
      result = expression(createExpressionContext(context))
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'asQuery')
  def asQuery(self, strict_membership=False):
    """
    A Predicate can be rendered as a set of catalog conditions. This
    can be useful to create reporting trees based on the
    ZSQLCatalog. This condition set is however partial since
    python scripts which are used by the test method of the predicate
    cannot be converted to catalog conditions. If a python script is defined to
    implement test, results obtained through asQuery must be additionnaly
    tested by invoking test().
    """
    portal_catalog = self.getPortalObject().portal_catalog
    buildSingleQuery = portal_catalog.getSQLCatalog().buildSingleQuery
    getCategoryParameterDict = portal_catalog.getCategoryParameterDict
    def filterCategoryList(base_category_set, category_list):
      return [
        x for x in category_list
        if x.split('/', 1)[0] in base_category_set
      ]
    if six.PY2:
      next_join_counter = itertools.count().next
    else:
      next_join_counter = itertools.count().__next__
    def buildSeparateJoinQuery(name, value):
      query = buildSingleQuery(name, value)
      suffix = str(next_join_counter())
      # XXX: using a deprecated API and accessing properties which are not part
      # of the API. Of course this will never break !
      query.setTableAliasList([
        (x, x + suffix) for x in query.search_key.table_list
      ])
      return query

    query_list = []
    append = query_list.append

    for buildQuery, getBaseCategorySet, getCategoryList in (
      ( # Single-membership criterion
        lambda name, value: buildSingleQuery(name, value),
        self.getMembershipCriterionBaseCategoryList,
        self.getMembershipCriterionCategoryList,
      ),
      ( # Multi-membership criterion
        buildSeparateJoinQuery,
        self.getMultimembershipCriterionBaseCategoryList,
        self.getMembershipCriterionCategoryList,
      ),
    ):
      filtered_category_list = filterCategoryList(
        getBaseCategorySet(),
        getCategoryList(),
      )
      if filtered_category_list:
        append(
          getCategoryParameterDict(
            filtered_category_list,
            strict_membership=strict_membership,
            onMissing=lambda category: False,
          ),
        )

    # Value criterion
    for criterion in self.getCriterionList():
      if not criterion.min and not criterion.max:
        append(buildSingleQuery(criterion.property, criterion.identity))
        continue
      if criterion.min:
        append(SimpleQuery(
          comparison_operator='>=',
          **{criterion.property: criterion.min}
        ))
      if criterion.max:
        append(SimpleQuery(
          comparison_operator='<=',
          **{criterion.property: criterion.max}
        ))

    if query_list:
      return ComplexQuery(query_list, logical_operator='AND')
    elif not getattr(self, 'isEmptyCriterionValid', lambda: True)():
      # By catalog definition, no object has uid 0, so this condition forces an
      # empty result.
      return SimpleQuery(uid=0)
    return SimpleQuery(uid=0, comparison_operator='>')

  security.declareProtected(Permissions.AccessContentsInformation, 'searchResults')
  def searchResults(self, **kw):
    """
    """
    return self.getPortalObject().portal_catalog.searchResults(
      predicate_internal_query=self.asQuery(),
      **kw
    )

  security.declareProtected(Permissions.AccessContentsInformation, 'countResults')
  def countResults(self, REQUEST=None, used=None, **kw):
    """
    """
    return self.getPortalObject().portal_catalog.countResults(
      predicate_internal_query=self.asQuery(),
      **kw
    )

  security.declareProtected( Permissions.AccessContentsInformation, 'getCriterionList' )
  def getCriterionList(self, **kw):
    """
      Returns the list of criteria which are defined by the Predicate.

      Each criterion is returned in a TempBase instance intended to be
      displayed in a ListBox.

      XXX - It would be better to return criteria in a Criterion class
            instance
    """
    # We do not create PersistentMappings first time we *see* Predicate_view.
    # Instead, we create them first time we modify Predicate document.
    if not self.getCriterionPropertyList():
      return []
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = PersistentMapping()
      self._range_criterion = PersistentMapping()
    criterion_dict = {}
    for p in self.getCriterionPropertyList():
      criterion_dict[p] = newTempBase(self, 'new_%s' % p)
      criterion_dict[p].identity = self._identity_criterion.get(p, None)
      criterion_dict[p].uid = 'new_%s' % p
      criterion_dict[p].property = p
      criterion_dict[p].min = self._range_criterion.get(p, (None, None))[0]
      criterion_dict[p].max = self._range_criterion.get(p, (None, None))[1]
    return sorted(criterion_dict.values())

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
    # XXX 'min' and 'max' are built-in functions.
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = PersistentMapping()
      self._range_criterion = PersistentMapping()
    if identity is not None :
      self._identity_criterion[property] = identity
    if min == '':
      min = None
    if max == '':
      max = None
    if min is None and max is None:
      try:
        del self._range_criterion[property]
      except KeyError:
        pass
    else:
      self._range_criterion[property] = (min, max)
    self.reindexObject()

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  def edit(self, **kwd):
    """
      The edit method is overriden so that any time a
      criterion_property_list property is defined, a list of criteria
      is created to match the provided criterion_property_list.
    """
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = PersistentMapping()
      self._range_criterion = PersistentMapping()
    if 'criterion_property_list' in kwd:
      criterion_property_list = kwd['criterion_property_list']
      identity_criterion = PersistentMapping()
      range_criterion = PersistentMapping()
      for criterion in six.iterkeys(self._identity_criterion) :
        if criterion in criterion_property_list :
          identity_criterion[criterion] = self._identity_criterion[criterion]
      for criterion in six.iterkeys(self._range_criterion) :
        if criterion in criterion_property_list :
          range_criterion[criterion] = self._range_criterion[criterion]
      self._identity_criterion = identity_criterion
      self._range_criterion = range_criterion
    kwd['reindex_object'] = 1
    return self._edit(**kwd)

  # Predicate fusion method
  security.declareProtected( Permissions.ModifyPortalContent, 'setPredicateCategoryList' )
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
    self._identity_criterion = PersistentMapping()
    self._range_criterion = PersistentMapping()

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

  security.declareProtected(Permissions.AccessContentsInformation, 'generatePredicate')
  def generatePredicate(self, multimembership_criterion_base_category_list=(),
                        membership_criterion_base_category_list=(),
                        criterion_property_list=(),
                        identity_criterion=None,
                        range_criterion=None,):
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
    new_membership_criterion_base_category_list = list(self.getMembershipCriterionBaseCategoryList())
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

    # We need to build new criteria for asContext, and we should not
    # modify the original, so we always make copies. Since the usage is
    # temporary, use dicts instead of persistent mappings.
    new_identity_criterion = dict(getattr(self, '_identity_criterion', None) or
                                  {})
    new_identity_criterion.update(identity_criterion or {})
    new_range_criterion = dict(getattr(self, '_range_criterion', None) or {})
    new_range_criterion.update(range_criterion or {})

    # Look at local properties and make it criterion properties
    for property in criterion_property_list:
      if property not in self.getCriterionPropertyList() \
        and property in self.propertyIds():
          new_criterion_property_list.append(property)
          property_min = property + '_range_min'
          property_max = property + '_range_max'
          if getattr(self, 'get%s' % convertToUpperCase(property), None) is not None\
            and self.getProperty(property) is not None:
            new_identity_criterion[property] = self.getProperty(property)
          elif getattr(self, 'get%s' % convertToUpperCase(property_min), None) is not None:
            min = self.getProperty(property_min)
            max = self.getProperty(property_max)
            new_range_criterion[property] = (min,max)
    # Return a new context with new properties, like if
    # we have a predicate with local properties
    new_self = self.asContext(
        membership_criterion_category=new_membership_criterion_category_list,
        membership_criterion_base_category=new_membership_criterion_base_category_list,
        multimembership_criterion_base_category=new_multimembership_criterion_base_category_list,
        criterion_property_list=new_criterion_property_list,
        _identity_criterion=new_identity_criterion,
        _range_criterion=new_range_criterion)

    return new_self

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asPredicate')
  def asPredicate(self):
    """
      This method tries to convert the current Document into a predicate
      looking up methods named Class_asPredicate, MetaType_asPredicate, PortalType_asPredicate
    """
    cache = getTransactionalVariable()
    key = 'asPredicate', self
    try:
      return cache[key]
    except KeyError:
      self = unrestricted_apply(self._getTypeBasedMethod("asPredicate", "_asPredicate"))
      cache[key] = self
      return self

  def _asPredicate(self):
    return self

  security.declareProtected(Permissions.AccessContentsInformation, 'searchPredicate')
  def searchPredicate(self, **kw):
    """
      Returns a list of documents matching the predicate

      TO BE IMPLEMENTED using portal_catalog(**kw)
    """
    pass

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMembershipCriterionCategoryList')
  def getMembershipCriterionCategoryList(self, filter=None, **kw):
    """
    If filter is specified, return category only or document only
    in membership_criterion_category values.
    """
    all_list = self._baseGetMembershipCriterionCategoryList()
    if filter in ('category', 'document'):
      portal_categories = self.getPortalObject().portal_categories
      result_dict = {'category':[], 'document':[]}
      for x in all_list:
        try:
          if portal_categories.restrictedTraverse(x).getPortalType() == \
             'Category':
            result_dict['category'].append(x)
          else:
            result_dict['document'].append(x)
        except KeyError:
          result_dict['document'].append(x)
      return result_dict[filter]
    else:
      return all_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setMembershipCriterionDocumentList' )
  def setMembershipCriterionDocumentList(self, document_list):
    """
    Appends to membership_criterion_category values.
    """
    return self.setMembershipCriterionCategoryList(
      (self.getMembershipCriterionCategoryList() + document_list))
