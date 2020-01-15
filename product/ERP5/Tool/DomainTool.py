##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Sebastien Robin <seb@nexedi.com>
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

from collections import defaultdict
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
from zLOG import LOG
from DateTime import DateTime

_MARKER = []

class DomainTool(BaseTool):
    """
        A tool to define reusable ranges and subranges through
        predicate trees
    """
    id = 'portal_domains'
    meta_type = 'ERP5 Domain Tool'
    portal_type     = 'Domain Tool'
    allowed_types   = ('ERP5 Domain', )

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected(Permissions.ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('explainDomainTool', _dtmldir)

    # XXX FIXME method should not be public
    # (some users are not able to see resource's price)
    security.declarePublic('searchPredicateList')
    def searchPredicateList(self, *args, **kw):
      return self._searchPredicateList(restricted=True, *args, **kw)

    def _searchPredicateList(self, context, test=1, sort_method=None,
                             ignored_category_list=None,
                             tested_base_category_list=None,
                             filter_method=None, acquired=1,
                             sort_key_method=None, query=None,
                             restricted=False, **kw):
      """
      Search all predicates which corresponds to this particular
      context.

      - sort_method parameter should not be used, if possible, because
        it can be very slow. Use sort_key_method instead.

      - sort_key_method parameter is passed to list.sort as key parameter if it
        is not None. This allows to sort the list of predicates found. The most
        important predicate is the first one in the list.

      - ignored_category_list:  this is the list of category that we do
        not want to test. For example, we might want to not test the
        destination or the source of a predicate.

      - tested_base_category_list:  this is the list of category that we do
        want to test. For example, we might want to test only the
        destination or the source of a predicate.

      - the acquired parameter allows to define if we want to use
        acquisition for categories. By default we want.
      """
      if not kw.pop('strict', True):
        raise ValueError('"strict" mode cannot be disabled anymore')
      portal = self.getPortalObject()
      portal_catalog = portal.portal_catalog
      portal_categories = portal.portal_categories
      # Search the columns of the predicate table
      query_list = [] if query is None else [query]
      for column in portal_catalog.getSQLCatalog().getTableColumnList('predicate'):
        # Arbitrary suffix choice, this code expects COLUMN, COLUMN_range_min
        # and COLUMN_range_max to be simultaneously present for ranged
        # properties. Only checking one suffix simplifies the code flow.
        if column.endswith('_range_min'):
          property_name = column[:-10]
          # We have to check a range property
          equality = 'predicate.' + property_name
          range_min = equality + '_range_min'
          range_max = equality + '_range_max'

          value = context.getProperty(property_name)

          query = ComplexQuery(
              SimpleQuery(**{equality: None}),
              SimpleQuery(**{range_min: None}),
              SimpleQuery(**{range_max: None}),
              logical_operator='AND')

          if value is not None:
            query = ComplexQuery(
              query,
              SimpleQuery(**{equality: value}),
              ComplexQuery(
                SimpleQuery(comparison_operator='<=', **{range_min: value}),
                SimpleQuery(**{range_max: None}),
                logical_operator='AND',
              ),
              ComplexQuery(
                SimpleQuery(**{range_min: None}),
                SimpleQuery(comparison_operator='>=', **{range_max: value}),
                logical_operator='AND',
              ),
              ComplexQuery(
                SimpleQuery(comparison_operator='<=', **{range_min: value}),
                SimpleQuery(comparison_operator='>=', **{range_max: value}),
                logical_operator='AND',
              ),
              logical_operator='OR',
            )

          query_list.append(query)

      if tested_base_category_list != []:
        # Add category selection
        if tested_base_category_list is None:
          if acquired:
            category_list = context.getAcquiredCategoryList()
          else:
            category_list = context.getCategoryList()
        else:
          if acquired:
            getter = context.getAcquiredCategoryMembershipList
          else:
            getter = context.getCategoryMembershipList
          category_list = []
          extend = category_list.extend
          for tested_base_category in tested_base_category_list:
            if portal_categories.get(tested_base_category) is None:
              raise ValueError('Unknown base category: %r' % (tested_base_category, ))
            tested_category_list = getter(tested_base_category, base=1)
            if tested_category_list:
              extend(tested_category_list)
            else:
              # Developer requested specific base categories, but context do not
              # declare one of these. Skipping this criterion risks matching too
              # many predicates, breaking the system performance-wise. So let
              # developer know there is an unexpected situation by raising.
              raise ValueError('%r does not have any %r relation' % (
                context.getPath(),
                tested_base_category,
              ))
        left_join_list = kw.get('left_join_list', [])[:]
        inner_join_list = kw.get('inner_join_list', [])[:]
        if category_list:
          preferred_predicate_category_list = portal.portal_preferences.getPreferredPredicateCategoryList([])
          left_join_category_list = []
          inner_join_category_list = []
          for category in category_list:
            if portal_categories.getBaseCategoryId(category) in preferred_predicate_category_list:
              inner_join_category_list.append(category)
            else:
              left_join_category_list.append(category)
          def onMissing(category):
            # BBB: ValueError would seem more appropriate here, but original code
            # was raising TypeError - and this is explicitely tested for.
            raise TypeError('Unknown category: %r' % (category, ))
          def onInnerJoin(column_name):
            inner_join_list.append(column_name)
            # Base category is part of preferred predicate categories, predicates
            # which ignore it are indexed with category_uid=0.
            return SimpleQuery(**{column_name: 0})
          query_list.append(portal_catalog.getCategoryParameterDict(
            inner_join_category_list,
            category_table='predicate_category',
            onMissing=onMissing,
            onJoin=onInnerJoin,
          ))
          def onLeftJoin(column_name):
            left_join_list.append(column_name)
            # Base category is not part of preferred predicate categories,
            # predicates which ignore it get no predicate_category row inserted
            # for it, so an SQL NULL appears, translating to None.
            return SimpleQuery(**{column_name: None})
          query_list.append(portal_catalog.getCategoryParameterDict(
            left_join_category_list,
            category_table='predicate_category',
            onMissing=onMissing,
            onJoin=onLeftJoin,
          ))
        else:
          # No category to match against, so predicates expecting any relation
          # would not apply, so we can exclude these.
          # Note: this relies on a special indexation mechanism for predicate
          # categories, which inserts a base_category_uid=0 line when indexed
          # predicate membership_criterion_category_list is empty.
          base_category_uid_column = 'predicate_category.base_category_uid'
          kw[base_category_uid_column] = 0
          inner_join_list.append(base_category_uid_column)
        kw['left_join_list'] = left_join_list
        kw['inner_join_list'] = inner_join_list
      if query_list:
        kw['query'] = ComplexQuery(logical_operator='AND', *query_list)

      if restricted:
        sql_result_list = portal_catalog.searchResults(**kw)
      else:
        sql_result_list = portal_catalog.unrestrictedSearchResults(**kw)
      if kw.get('src__'):
        return sql_result_list
      result_list = []
      if sql_result_list:
        if test:
          cache = {}
          def isMemberOf(context, c, strict_membership):
            if c in cache:
              return cache[c]
            cache[c] = result = portal_categories.isMemberOf(
              context, c, strict_membership=strict_membership)
            return result
        for predicate in sql_result_list:
          predicate = predicate.getObject()
          if not test or predicate.test(context, tested_base_category_list,
                                        isMemberOf=isMemberOf):
            result_list.append(predicate)
        if filter_method is not None:
          result_list = filter_method(result_list)
        if sort_key_method is not None:
          result_list.sort(key=sort_key_method)
        elif sort_method is not None:
          result_list.sort(cmp=sort_method)
      return result_list

    # XXX FIXME method should not be public
    # (some users are not able to see resource's price)
    security.declarePublic('generateMappedValue')
    def generateMappedValue(self, context, test=1, predicate_list=None, **kw):
      """
      We will generate a mapped value with the list of all predicates
      found.
      Let's say we have 3 predicates (in the order we want) like this:
      Predicate 1   [ base_price1,           ,   ,   ,    ,    , ]
      Predicate 2   [ base_price2, quantity2 ,   ,   ,    ,    , ]
      Predicate 3   [ base_price3, quantity3 ,   ,   ,    ,    , ]
      Our generated MappedValue will have the base_price of the
      predicate1, and the quantity of the Predicate2, because Predicate
      1 is the first one which defines a base_price and the Predicate2
      is the first one wich defines a quantity.
      """
      # First get the list of predicates
      if predicate_list is None:
        predicate_list = self.searchPredicateList(context, test=test, **kw)
      if len(predicate_list)==0:
        # No predicate, return None
        mapped_value = None
      else:
        # Generate tempDeliveryCell
        mapped_value = self.getPortalObject().newContent(temp_object=True,
          portal_type='Supply Cell', id='new_mapped_value')
        mapped_value_property_dict = {}
        # Look for each property the first predicate which defines the
        # property
        for predicate in predicate_list:
          getMappedValuePropertyList = getattr(predicate,
            'getMappedValuePropertyList', None)
          # searchPredicateList returns a list of any kind of predicate, which
          # includes predicates not containing any mapped value (for exemple,
          # domains). In such case, it has no meaning to handle them here.
          # A better way would be to tell catalog not to provide us with those
          # extra object, but there is no simple way (many portal types inherit
          # from MappedValue defining the accessor).
          # Feel free to improve.
          if getMappedValuePropertyList is not None:
            for mapped_value_property in predicate.getMappedValuePropertyList():
              if not mapped_value_property_dict.has_key(mapped_value_property):
                value = predicate.getProperty(mapped_value_property)
                if value is not None:
                  mapped_value_property_dict[mapped_value_property] = value
        # Update mapped value
        mapped_value.edit(**mapped_value_property_dict)
      return mapped_value

    # XXX FIXME method should not be public
    # (some users are not able to see resource's price)
    security.declarePublic('generateMultivaluedMappedValue')
    def generateMultivaluedMappedValue(self, context, test=1,
        predicate_list=None, **kw):
      """
      We will generate a mapped value with the list of all predicates
      found.
      Let's say we have 3 predicates (in the order we want) like this:
      Predicate 1   [ base_price1,           ,   ,   ,    ,    , ]
      Predicate 2   [ base_price2, additional_price2 ,   ,   ,    ,    , ]
      Predicate 3   [ base_price3, additional_price3 ,   ,   ,    ,    , ]
      Our generated MappedValue will take all values for each property and put
      them in lists, unless predicates define the same list of criterion categories
      """
      # First get the list of predicates
      if predicate_list is None:
        predicate_list = self.searchPredicateList(context, test=test, **kw)
      if predicate_list:
        mapped_value_property_dict = defaultdict(list)
        # Look for each property the first predicate with unique criterion
        # categories which defines the property
        for predicate in predicate_list:
          for mapped_value_property in predicate.getMappedValuePropertyList():
            value = predicate.getProperty(mapped_value_property)
            if value is not None:
              mapped_value_property_dict[mapped_value_property].append(value)
        mapped_value = self.getPortalObject().newContent(temp_object=True,
          portal_type='Supply Cell', id='multivalued_mapped_value')
        mapped_value._setMappedValuePropertyList(
          mapped_value_property_dict.keys())
        mapped_value.__dict__.update(mapped_value_property_dict)
        return mapped_value


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getChildDomainValueList')
    def getChildDomainValueList(self, parent, **kw):
      """
      Return child domain objects already present adn thois generetaded dynamically
      """
      # get static domain
      object_list = list(parent.objectValues())
      # get dynamic object generated from script
      object_list.extend(parent.getDomainGeneratorList(**kw))
      return object_list


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDomainByPath')
    def getDomainByPath(self, path, default=_MARKER):
      """
      Return the domain object for a given path
      """
      path = path.split('/')
      base_domain_id = path[0]
      if default is _MARKER:
        domain = self[base_domain_id]
      else:
        domain = self.get(base_domain_id, _MARKER)
        if domain is _MARKER: return default
      for depth, subdomain in enumerate(path[1:]):
        domain_list = self.getChildDomainValueList(domain, depth=depth)
        for d in domain_list:
          if d.getId() == subdomain:
            domain = d
            break
        else:
          if domain is _MARKER: return default
          raise KeyError, subdomain
      return domain

InitializeClass(DomainTool)
