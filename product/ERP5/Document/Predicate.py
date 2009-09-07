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

import zope.interface
from warnings import warn
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner

from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Cache import getReadOnlyTransactionCache, enableReadOnlyTransactionCache, disableReadOnlyTransactionCache
from Products.ZSQLCatalog.SQLCatalog import SQLQuery
from Globals import PersistentMapping

from zLOG import LOG

class Predicate(XMLObject, Folder):
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
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.Predicate
                    , PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    )

  # Declarative interfaces
  zope.interface.implements( interfaces.IPredicate, )

  security.declareProtected( Permissions.AccessContentsInformation, 'test' )
  def test(self, context, tested_base_category_list=None, 
           strict_membership=0, **kw):
    """
      A Predicate can be tested on a given context.
      Parameters can passed in order to ignore some conditions.

      - tested_base_category_list:  this is the list of category that we do
        want to test. For example, we might want to test only the
        destination or the source of a predicate.
      - if strict_membership is specified, we should make sure that we
        are strictly a member of tested categories
    """
    self = self.asPredicate()
    result = 1
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = PersistentMapping()
      self._range_criterion = PersistentMapping()
#    LOG('PREDICATE TEST', 0,
#        'testing %s on context of %s' % \
#        (self.getRelativeUrl(), context.getRelativeUrl()))
    for property, value in self._identity_criterion.iteritems():
      if isinstance(value, (list, tuple)):
        result = result and (context.getProperty(property) in value)
      else:
        result = result and (context.getProperty(property) == value)
#      LOG('predicate test', 0,
#          '%s after prop %s : %s == %s' % \
#          (result, property, context.getProperty(property), value))
    for property, (min, max) in self._range_criterion.iteritems():
      value = context.getProperty(property)
      if min is not None:
        result = result and (value >= min)
#        LOG('predicate test', 0,
#            '%s after prop %s : %s >= %s' % \
#            (result, property, value, min))
      if max is not None:
        result = result and (value < max)
#        LOG('predicate test', 0,
#            '%s after prop %s : %s < %s' % \
#            (result, property, value, max))
    multimembership_criterion_base_category_list = \
        self.getMultimembershipCriterionBaseCategoryList()
    membership_criterion_base_category_list = \
        self.getMembershipCriterionBaseCategoryList()
    tested_base_category = {}
#    LOG('predicate test', 0,
#        'categories will be tested in multi %s single %s as %s' % \
#        (multimembership_criterion_base_category_list,
#        membership_criterion_base_category_list,
#        self.getMembershipCriterionCategoryList()))
    membership_criterion_category_list = \
                            self.getMembershipCriterionCategoryList()
    if tested_base_category_list is not None:
      membership_criterion_category_list = [x for x in \
          membership_criterion_category_list if x.split('/', 1)[0] in \
          tested_base_category_list]

    # Test category memberships. Enable the read-only transaction cache
    # temporarily, if not enabled, because this part is strictly read-only,
    # and context.isMemberOf is very expensive, when the category list has
    # many items.
    enabled = (getReadOnlyTransactionCache(self) is not None)
    try:
      if not enabled:
        enableReadOnlyTransactionCache(self)
      for c in membership_criterion_category_list:
        bc = c.split('/', 1)[0]
        if (bc not in tested_base_category) and \
           (bc in multimembership_criterion_base_category_list):
          tested_base_category[bc] = 1
        elif (bc not in tested_base_category) and \
             (bc in membership_criterion_base_category_list):
          tested_base_category[bc] = 0
        if (bc in multimembership_criterion_base_category_list):
          tested_base_category[bc] = tested_base_category[bc] and \
                                     context.isMemberOf(c, 
                                         strict_membership=strict_membership)
#        LOG('predicate test', 0,
#            '%s after multi membership to %s' % \
#            (tested_base_category[bc], c))
        elif (bc in membership_criterion_base_category_list):
          tested_base_category[bc] = tested_base_category[bc] or \
                                     context.isMemberOf(c,
                                         strict_membership=strict_membership)
    finally:
      if not enabled:
        disableReadOnlyTransactionCache(self)

#        LOG('predicate test', 0,
#            '%s after single membership to %s' % \
#            (tested_base_category[bc], c))
    result = result and (0 not in tested_base_category.values())
#    LOG('predicate test', 0,
#        '%s after category %s ' % (result, tested_base_category.items()))
    # Test method calls
    test_method_id_list = self.getTestMethodIdList()
    if test_method_id_list is not None :
      for test_method_id in test_method_id_list :
        if (test_method_id is not None) and result:
          method = getattr(context,test_method_id)
          try:
            result = result and method(self)
          except TypeError:
            if method.func_code.co_argcount != 0:
              raise
            # backward compatibilty with script that takes no argument
            warn('Predicate %s uses an old-style method (%s) that does not'
                 ' take the predicate as argument' % (
               self.getRelativeUrl(), method.__name__), DeprecationWarning)
            result = result and method()
#        LOG('predicate test', 0,
#            '%s after method %s ' % (result, test_method_id))
    return result

  security.declareProtected( Permissions.AccessContentsInformation,
                             'buildSQLQuery' )
  def buildSQLQuery(self, strict_membership=0, table='category',
                          join_table='catalog', join_column='uid',
                          **kw):
    """
      A Predicate can be rendered as an SQL expression. This
      can be used to generate SQL requests in reports or in
      catalog search queries.

      XXX - This method is not implemented yet
    """
    # Build the identity criterion
    catalog_kw = {}
    catalog_kw.update(kw) # query_table, REQUEST, ignore_empty_string, **kw
    for criterion in self.getCriterionList():
      if criterion.min and criterion.max:
        catalog_kw[criterion.property] = { 'query' : (criterion.min, criterion.max),
                                           'range' : 'minmax'
                                         }
      elif criterion.min:
        catalog_kw[criterion.property] = { 'query' : criterion.min,
                                           'range' : 'min'
                                         }
      elif criterion.max:
        catalog_kw[criterion.property] = { 'query' : criterion.max,
                                           'range' : 'max'
                                         }
      else:
        catalog_kw[criterion.property] = criterion.identity

    portal_catalog = getToolByName(self, 'portal_catalog')
    portal_categories = getToolByName(self, 'portal_categories')

    from_table_dict = {}

    # First build SQL for membership criteria
    # It would be much nicer if all this was handled by the catalog in a central place
    membership_dict = {}
    for base_category in self.getMembershipCriterionBaseCategoryList():
      membership_dict[base_category] = [] # Init dict with valid base categories
    for category in self.getMembershipCriterionCategoryList():
      base_category = category.split('/')[0] # Retrieve base category
      if membership_dict.has_key(base_category):
        category_value = portal_categories.resolveCategory(category, None)
        if category_value is not None:
          table_alias = "single_%s_%s" % (table, base_category)
          from_table_dict[table_alias] = 'category'
          membership_dict[base_category].append(category_value.asSQLExpression(
                                          strict_membership=strict_membership,
                                          table=table_alias,
                                          base_category=base_category))
    membership_select_list = []
    for expression_list in membership_dict.values():
      or_expression = ' OR '.join(expression_list)
      if or_expression:
        membership_select_list.append('( %s )' % or_expression)

    # Then build SQL for multimembership_dict criteria
    multimembership_dict = {}
    for base_category in self.getMultimembershipCriterionBaseCategoryList():
      multimembership_dict[base_category] = [] # Init dict with valid base categories
    join_count = 0
    for category in self.getMembershipCriterionCategoryList():
      base_category = category.split('/')[0] # Retrieve base category
      if multimembership_dict.has_key(base_category):
        category_value = portal_categories.resolveCategory(category)
        if category_value is not None:
          join_count += 1
          table_alias = "multi_%s_%s" % (table, join_count)
          from_table_dict[table_alias] = 'category'
          multimembership_dict[base_category].append(category_value.asSQLExpression(
                                          strict_membership=strict_membership,
                                          table=table_alias,
                                          base_category=base_category))
    multimembership_select_list = []
    for expression_list in multimembership_dict.values():
      and_expression = ' AND '.join(expression_list)
      if and_expression:
        multimembership_select_list.append(and_expression)

    # Build the join where expression
    join_select_list = []
    for k in from_table_dict.iterkeys():
      join_select_list.append('%s.%s = %s.uid' % (join_table, join_column, k))

    sql_text = ' AND '.join(join_select_list + membership_select_list +
                            multimembership_select_list)

    # Now merge identity and membership criteria
    if len(sql_text):
      catalog_kw['where_expression'] = SQLQuery(sql_text)
    else:
      catalog_kw['where_expression'] = ''
    sql_query = portal_catalog.buildSQLQuery(**catalog_kw)
    for alias, table in sql_query['from_table_list']:
      if from_table_dict.has_key(alias):
        raise KeyError, "The same table is used twice for an identity criterion and for a membership criterion"
      from_table_dict[alias] = table
    sql_query['from_table_list'] = from_table_dict.items()
    return sql_query

  # Compatibililty SQL Sql
  security.declareProtected( Permissions.AccessContentsInformation, 'buildSqlQuery' )
  buildSqlQuery = buildSQLQuery

  security.declareProtected( Permissions.AccessContentsInformation, 'asSQLExpression' )
  def asSQLExpression(self, strict_membership=0, table='category'):
    """
      A Predicate can be rendered as an SQL expression. This
      can be used to generate SQL requests in reports or in
      catalog search queries.
    """
    return self.buildSQLQuery(strict_membership=strict_membership, table=table)['where_expression']

  # Compatibililty SQL Sql
  security.declareProtected( Permissions.AccessContentsInformation, 'asSqlExpression' )
  asSqlExpression = asSQLExpression

  security.declareProtected( Permissions.AccessContentsInformation, 'asSQLJoinExpression' )
  def asSQLJoinExpression(self, strict_membership=0, table='category', join_table='catalog', join_column='uid'):
    """
    """
    table_list = self.buildSQLQuery(strict_membership=strict_membership, table=table)['from_table_list']
    sql_text_list = map(lambda (a,b): '%s AS %s' % (b,a), filter(lambda (a,b): a != join_table, table_list))
    return ' , '.join(sql_text_list)

  # Compatibililty SQL Sql
  security.declareProtected( Permissions.AccessContentsInformation, 'asSqlJoinExpression' )
  asSqlJoinExpression = asSQLJoinExpression

  def searchResults(self, **kw):
    """
    """
    portal_catalog = getToolByName(self, 'portal_catalog')
    return portal_catalog.searchResults(build_sql_query_method=self.buildSQLQuery,**kw)

  def countResults(self, REQUEST=None, used=None, **kw):
    """
    """
    portal_catalog = getToolByName(self, 'portal_catalog')
    return portal_catalog.countResults(build_sql_query_method=self.buildSQLQuery,**kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getCriterionList' )
  def getCriterionList(self, **kw):
    """
      Returns the list of criteria which are defined by the Predicate.

      Each criterion is returned in a TempBase instance intended to be
      displayed in a ListBox.

      XXX - It would be better to return criteria in a Criterion class
            instance
    """
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
      identity_criterion = {}
      range_criterion = {}
      for criterion in self._identity_criterion.iterkeys() :
        if criterion in criterion_property_list :
          identity_criterion[criterion] = self._identity_criterion[criterion]
      for criterion in self._range_criterion.iterkeys() :
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
    identity_criterion = getattr(self,'_identity_criterion',{})
    range_criterion = getattr(self,'_range_criterion',{})
    # Look at local properties and make it criterion properties
    for property in criterion_property_list:
      if property not in self.getCriterionPropertyList() \
        and property in self.propertyIds():
          new_criterion_property_list.append(property)
          property_min = property + '_range_min'
          property_max = property + '_range_max'
          if getattr(self, 'get%s' % convertToUpperCase(property), None) is not None\
            and self.getProperty(property) is not None:
            identity_criterion[property] = self.getProperty(property)
          elif getattr(self, 'get%s' % convertToUpperCase(property_min), None) is not None:
            min = self.getProperty(property_min)
            max = self.getProperty(property_max)
            range_criterion[property] = (min,max)
    # Return a new context with new properties, like if
    # we have a predicate with local properties
    new_self = self.asContext(
        membership_criterion_category=new_membership_criterion_category_list,
        membership_criterion_base_category=new_membership_criterion_base_category_list,
        multimembership_criterion_base_category=new_multimembership_criterion_base_category_list,
        criterion_property_list=new_criterion_property_list,
        _identity_criterion=identity_criterion,
        _range_criterion=range_criterion)

    return new_self

  # Predicate handling
  security.declareProtected(Permissions.AccessContentsInformation,
                            'asPredicate')
  def asPredicate(self, script_id=None):
    """
      This method tries to convert the current Document into a predicate
      looking up methods named ${PortalType}_asPredicate,
      ${MetaType}_asPredicate, ${Class}_asPredicate     
    """
    if script_id is not None:
      script = getattr(self, script_id, None)
    else:
      script = self._getTypeBasedMethod('asPredicate')
    if script is not None:
      return script()
    return self

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
