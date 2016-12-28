##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

from Products.ERP5 import _dtmldir

from zLOG import LOG, PROBLEM, WARNING, INFO

from Products.ERP5.Capacity.GLPK import solve
from numpy import zeros, resize
from DateTime import DateTime

from Products.ERP5 import DeliverySolver
from Products.ERP5 import TargetSolver
from Products.PythonScripts.Utility import allow_class

from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery, SimpleQuery

from Shared.DC.ZRDB.Results import Results
from Products.ERP5Type.Utils import mergeZRDBResults
from App.Extensions import getBrain
from MySQLdb import ProgrammingError
from MySQLdb.constants.ER import NO_SUCH_TABLE

from hashlib import md5
from warnings import warn
from cPickle import loads, dumps
from copy import deepcopy

MYSQL_MIN_DATETIME_RESOLUTION = 1/86400.

class StockOptimisationError(Exception):
    pass

class SimulationTool(BaseTool):
    """
    The SimulationTool implements the ERP5
    simulation algorithmics.


    Examples of applications:

    -

    -
    ERP5 main purpose:

    -

    -

    """
    id = 'portal_simulation'
    meta_type = 'ERP5 Simulation Tool'
    portal_type = 'Simulation Tool'
    allowed_types = ( 'ERP5 Applied Rule', )

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainSimulationTool', _dtmldir )

    def filtered_meta_types(self, user=None):
      # Filters the list of available meta types.
      all = SimulationTool.inheritedAttribute('filtered_meta_types')(self)
      meta_types = []
      for meta_type in self.all_meta_types():
        if meta_type['name'] in self.allowed_types:
          meta_types.append(meta_type)
      return meta_types

    def tpValues(self) :
      """ show the content in the left pane of the ZMI """
      return self.objectValues()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container) :
      """Init permissions right after creation.

      Permissions in simulation tool are simple:
       o Each member can access and create some content.
       o Only manager can view, because simulation can be seen as
         sensitive information.
      """
      item.manage_permission(Permissions.AddPortalContent,
            ['Member', 'Author', 'Manager'])
      item.manage_permission(Permissions.AccessContentsInformation,
            ['Member', 'Auditor', 'Manager'])
      item.manage_permission(Permissions.View,
            ['Manager',])
      BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'solveDelivery')
    def solveDelivery(self, delivery, delivery_solver_name, target_solver_name,
                      additional_parameters=None, **kw):
      """
        XXX obsoleted API

        Solves a delivery by calling first DeliverySolver, then TargetSolver
      """
      return self._solveMovementOrDelivery(delivery, delivery_solver_name,
          target_solver_name, delivery=1,
          additional_parameters=additional_parameters, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'solveMovement')
    def solveMovement(self, movement, delivery_solver_name, target_solver_name,
                      additional_parameters=None, **kw):
      """
        XXX obsoleted API

        Solves a movement by calling first DeliverySolver, then TargetSolver
      """
      return self._solveMovementOrDelivery(movement, delivery_solver_name,
          target_solver_name, movement=1,
          additional_parameters=additional_parameters, **kw)

    def _solveMovementOrDelivery(self, document, delivery_solver_name,
                                 target_solver_name, movement=0, delivery=0,
                                 additional_parameters=None,**kw):
      """
        Solves a document by calling first DeliverySolver, then TargetSolver
      """
      if movement == delivery:
        raise ValueError('Parameters movement and delivery have to be'
                         ' different')

      solve_result = []
      for solver_name, solver_module in ((delivery_solver_name, DeliverySolver),
                                         (target_solver_name, TargetSolver)):
        result = None
        if solver_name is not None:
          solver_file_path = "%s.%s" % (solver_module.__name__,
                                        solver_name)
          __import__(solver_file_path)
          solver_file = getattr(solver_module, solver_name)
          solver_class = getattr(solver_file, solver_name)
          solver = solver_class(additional_parameters=additional_parameters,
              **kw)

          if movement:
            result = solver.solveMovement(document)
          if delivery:
            result = solver.solveDelivery(document)
        solve_result.append(result)
      return solve_result

    #######################################################
    # Stock Management

    def _generatePropertyUidList(self, prop, as_text=0):
      """
      converts relative_url or text (single element or list or dict)
        to an object usable by buildSQLQuery

      as_text == 0: tries to lookup an uid from the relative_url
      as_text == 1: directly passes the argument as text
      """
      if prop is None :
        return []
      category_tool = getToolByName(self, 'portal_categories')
      property_uid_list = []
      if isinstance(prop, str):
        if not as_text:
          prop_value = category_tool.getCategoryValue(prop)
          if prop_value is None:
            raise ValueError, 'Category %s does not exists' % prop
          property_uid_list.append(prop_value.getUid())
        else:
          property_uid_list.append(prop)
      elif isinstance(prop, (list, tuple)):
        for property_item in prop :
          if not as_text:
            prop_value = category_tool.getCategoryValue(property_item)
            if prop_value is None:
              raise ValueError, 'Category %s does not exists' % property_item
            property_uid_list.append(prop_value.getUid())
          else:
            property_uid_list.append(property_item)
      elif isinstance(prop, dict):
        tmp_uid_list = []
        if isinstance(prop['query'], str):
          prop['query'] = [prop['query']]
        for property_item in prop['query'] :
          if not as_text:
            prop_value = category_tool.getCategoryValue(property_item)
            if prop_value is None:
              raise ValueError, 'Category %s does not exists' % property_item
            tmp_uid_list.append(prop_value.getUid())
          else:
            tmp_uid_list.append(property_item)
        if tmp_uid_list:
          property_uid_list = {}
          property_uid_list['operator'] = prop['operator']
          property_uid_list['query'] = tmp_uid_list
      return property_uid_list

    def _getSimulationStateQuery(self, **kw):
      simulation_state_dict = self._getSimulationStateDict(**kw)
      return self._buildSimulationStateQuery(simulation_state_dict=simulation_state_dict)

    def _buildSimulationStateQuery(self, simulation_state_dict, table='stock'):
      simulation_state = simulation_state_dict.get('simulation_state')
      if simulation_state is not None:
        return SimpleQuery(**{table + '.simulation_state': simulation_state})
      input_simulation_state = simulation_state_dict.get('input_simulation_state')
      if input_simulation_state is not None:
        simulation_query = ComplexQuery(
          self._getIncreaseQuery(table, 'quantity', True),
          SimpleQuery(**{table + '.simulation_state': input_simulation_state}),
          logical_operator='AND',
        )
        output_simulation_state = simulation_state_dict.get('output_simulation_state')
        if output_simulation_state is not None:
          simulation_query = ComplexQuery(
            simulation_query,
            ComplexQuery(
              self._getIncreaseQuery(table, 'quantity', False),
              SimpleQuery(**{table + '.simulation_state': output_simulation_state}),
              logical_operator='AND',
            ),
            logical_operator='OR'
          )
        return simulation_query

    def _getSimulationStateDict(self, simulation_state=None, omit_transit=0,
                                input_simulation_state=None,
                                output_simulation_state=None,
                                transit_simulation_state=None,
                                strict_simulation_state=None):
      """
      This method is used in order to give what should be
      the input_simulation_state or output_simulation_state
      depending on many parameters
      """
      string_or_list = (str, list, tuple)
      # Simulation States
      # If strict_simulation_state is set, we directly put it into the dictionary
      simulation_dict = {}
      if strict_simulation_state:
        if isinstance(simulation_state, string_or_list)\
                and simulation_state:
           simulation_query = SimpleQuery(
                   **{'stock.simulation_state': simulation_state})
      else:
        # first, we evaluate simulation_state
        sql_kw = {}
        if simulation_state and isinstance(simulation_state, string_or_list):
          if isinstance(simulation_state, str):
            sql_kw['input_simulation_state'] = [simulation_state]
            sql_kw['output_simulation_state'] = [simulation_state]
          else:
            sql_kw['input_simulation_state'] = simulation_state
            sql_kw['output_simulation_state'] = simulation_state
        # then, if omit_transit == 1, we evaluate (simulation_state -
        # transit_simulation_state) for input_simulation_state
        if omit_transit:
          if isinstance(simulation_state, string_or_list)\
                and simulation_state:
            if isinstance(transit_simulation_state, string_or_list)\
                  and transit_simulation_state:
              # when we know both are usable, we try to calculate
              # (simulation_state - transit_simulation_state)
              if isinstance(simulation_state, str):
                simulation_state = [simulation_state]
              if isinstance(transit_simulation_state, str) :
                transit_simulation_state = [transit_simulation_state]
              delivered_simulation_state_list = []
              for state in simulation_state :
                if state not in transit_simulation_state :
                  delivered_simulation_state_list.append(state)
              sql_kw['input_simulation_state'] = delivered_simulation_state_list

        # alternatively, the user can directly define input_simulation_state
        # and output_simulation_state
        if input_simulation_state and isinstance(input_simulation_state,
                                                  string_or_list):
          if isinstance(input_simulation_state, str):
            input_simulation_state = [input_simulation_state]
          sql_kw['input_simulation_state'] = input_simulation_state
        if output_simulation_state and isinstance(output_simulation_state,
                                                  string_or_list):
          if isinstance(output_simulation_state, str):
            output_simulation_state = [output_simulation_state]
          sql_kw['output_simulation_state'] = output_simulation_state
        # XXX In this case, we must not set sql_kw[input_simumlation_state] before
        input_simulation_state = None
        output_simulation_state = None
        if sql_kw.has_key('input_simulation_state'):
          input_simulation_state = sql_kw.get('input_simulation_state')
        if sql_kw.has_key('output_simulation_state'):
          output_simulation_state = sql_kw.get('output_simulation_state')
        if input_simulation_state is not None \
           or output_simulation_state is not None:
          sql_kw.pop('input_simulation_state',None)
          sql_kw.pop('output_simulation_state',None)
        if input_simulation_state is not None:
          if output_simulation_state is not None:
            if input_simulation_state == output_simulation_state:
              simulation_dict['simulation_state'] = input_simulation_state
            else:
              simulation_dict['input_simulation_state'] = input_simulation_state
              simulation_dict['output_simulation_state'] = output_simulation_state
          else:
            simulation_dict['input_simulation_state'] = input_simulation_state
        elif output_simulation_state is not None:
          simulation_dict['simulation_state'] = output_simulation_state
      return simulation_dict

    def _getIncreaseQuery(self, table, column, increase, sql_catalog_id=None):
      """
      Returns a Query filtering rows depending on whether they represent an
      increase or a decrease.
      table (string)
        Name of table to use as stock table.
      column (string)
        Name of interesting column. Supported values are:
        - total_price for asset price increase/decrease
        - quantity for quantity increase (aka input)/decrease (aka output)
      increase (bool)
        False: decreasing rows are kept
        True: increasing rows are kept
      sql_catalog_id (string or None)
        Idenfitier of an SQLCatalog object relevant to table, or None for
        default one.
      """
      if column == 'total_price':
        dedicated_column = 'is_asset_increase'
      elif column == 'quantity':
        dedicated_column = 'is_input'
      else:
        raise ValueError('Unknown column %r' % (column, ))
      if self.getPortalObject().portal_catalog.hasColumn(
            dedicated_column,
            sql_catalog_id,
          ):
        return SimpleQuery(**{dedicated_column: increase})
      # Dedicated columns are not present, compute on the fly.
      return ComplexQuery(
        ComplexQuery(
          SimpleQuery(comparison_operator='<', **{table + '.' + column: 0}),
          SimpleQuery(**{table + '.is_cancellation': increase}),
          logical_operator='AND',
        ),
        ComplexQuery(
          SimpleQuery(comparison_operator='>=', **{table + '.' + column: 0}),
          SimpleQuery(**{table + '.is_cancellation': not increase}),
          logical_operator='AND',
        ),
        logical_operator='OR',
      )

    def _generateSQLKeywordDict(self, table='stock', **kw):
        sql_kw, new_kw = self._generateKeywordDict(**kw)
        return self._generateSQLKeywordDictFromKeywordDict(table=table,
                 sql_kw=sql_kw, new_kw=new_kw)

    def _generateSQLKeywordDictFromKeywordDict(self, table='stock', sql_kw={},
                                               new_kw={}):
        ctool = getToolByName(self, 'portal_catalog')
        sql_kw = sql_kw.copy()
        new_kw = new_kw.copy()

        # Group-by expression  (eg. group_by=['node_uid'])
        group_by = new_kw.pop('group_by_list', [])

        # group by from stock table (eg. group_by_node=True)
        # prepend table name to avoid ambiguities.
        column_group_by = new_kw.pop('column_group_by', [])
        if column_group_by:
          group_by.extend(['%s.%s' % (table, x) for x in column_group_by])

        # group by from related keys columns (eg. group_by_node_category=True)
        related_key_group_by = new_kw.pop('related_key_group_by', [])
        if related_key_group_by:
          group_by.extend(['%s_%s' % (table, x) for x in related_key_group_by])

        # group by involving a related key (eg. group_by=['product_line_uid'])
        related_key_dict_passthrough_group_by = new_kw.get(
                'related_key_dict_passthrough', {}).pop('group_by_list', [])
        if isinstance(related_key_dict_passthrough_group_by, basestring):
          related_key_dict_passthrough_group_by = (
                related_key_dict_passthrough_group_by,)
        group_by.extend(related_key_dict_passthrough_group_by)

        if group_by:
          new_kw['group_by_list'] = group_by

        # select expression
        select_dict = new_kw.setdefault('select_dict', {})
        related_key_select_expression_list = new_kw.pop(
                'related_key_select_expression_list', [])
        for related_key_select in related_key_select_expression_list:
          select_dict[related_key_select] = '%s_%s' % (table,
                                                       related_key_select)

        # Column values
        column_value_dict = new_kw.pop('column_value_dict', {})
        for key, value in column_value_dict.iteritems():
          new_kw['%s.%s' % (table, key)] = value
        # Related keys
        # First, the passthrough (acts as default values)
        for key, value in new_kw.pop('related_key_dict_passthrough', {})\
            .iteritems():
          new_kw[key] = value
        # Second, calculated values
        for key, value in new_kw.pop('related_key_dict', {}).iteritems():
          new_kw['%s_%s' % (table, key)] = value
        # Simulation states matched with input and output omission
        def getSimulationQuery(simulation_dict, omit_dict):
          simulation_query = self._buildSimulationStateQuery(
            simulation_state_dict=simulation_dict,
            table=table,
          )
          query_list = [
            self._getIncreaseQuery(table, column, value)
            for key, column, value in (
              ('input',          'quantity',    False),
              ('output',         'quantity',    True),
              ('asset_increase', 'total_price', False),
              ('asset_decrease', 'total_price', True),
            )
            if omit_dict.get(key)
          ]
          if query_list:
            if simulation_query is not None:
              query_list.append(simulation_query)
            return ComplexQuery(
              query_list,
              logical_operator='AND',
            )
          return simulation_query
        simulation_query = getSimulationQuery(
          new_kw.pop('simulation_dict', {}),
          new_kw.pop('omit_dict', {}),
        )
        reserved_kw = new_kw.pop('reserved_kw', None)
        if reserved_kw is not None:
          reserved_query = getSimulationQuery(
            reserved_kw.pop('simulation_dict', {}),
            reserved_kw.pop('omit_dict', {}),
          )
          if simulation_query is None:
            simulation_query = reserved_query
          elif reserved_query is not None:
            simulation_query = ComplexQuery(
              simulation_query,
              reserved_query,
              logical_operator='OR',
            )
        if simulation_query is not None:
          new_kw['query'] = simulation_query

        # Sort on
        if 'sort_on' in new_kw:
          table_column_list = ctool.getSQLCatalog().getTableColumnList(table)
          sort_on = new_kw['sort_on']
          new_sort_on = []
          for column_id, sort_direction in sort_on:
            if column_id in table_column_list:
              column_id = '%s.%s' % (table, column_id)
            new_sort_on.append((column_id, sort_direction))
          new_kw['sort_on'] = tuple(new_sort_on)

        # Remove some internal parameters that does not have any meaning for
        # catalog
        new_kw.pop('ignore_group_by', None)

        catalog_sql_kw = ctool.buildSQLQuery(**new_kw)
        from_table_dict = dict(sql_kw.pop('from_table_list', []))
        for alias, table in catalog_sql_kw.pop('from_table_list', None) or []:
          assert from_table_dict.get(alias) in (None, table), (
            alias,
            table,
            from_table_dict[alias],
          )
          from_table_dict[alias] = table
        sql_kw.update(catalog_sql_kw)
        sql_kw['from_table_list'] = from_table_dict.items()

        # When group_by_time_sequence_list is used, the ZSQL method template
        # will use a variable slot_index, we want to select it, group and order
        # by it.
        if sql_kw.get('group_by_time_sequence_list'):
          new_kw['group_by_list'] = new_kw.get('group_by_list', []) + ['slot_index']
          new_kw['order_by_list'] = new_kw.get('order_by_list', []) + [('slot_index', )]
          new_kw.setdefault('select_dict', {})['slot_index'] = 'slot_index'

        sql_kw.update(ctool.buildSQLQuery(**new_kw))
        return sql_kw

    def _generateKeywordDict(self,
        # dates
        from_date=None, to_date=None, at_date=None,
        omit_mirror_date=1,
        # instances
        resource=None, node=None, payment=None,
        section=None, mirror_section=None, item=None,
        function=None, project=None, funding=None, payment_request=None,
        transformed_resource=None, ledger=None,
        # used for tracking
        input=0, output=0,
        # categories
        resource_category=None, node_category=None, payment_category=None,
        section_category=None, mirror_section_category=None,
        function_category=None, project_category=None, funding_category=None,
        ledger_category=None, payment_request_category=None,
        # categories with strict membership
        resource_category_strict_membership=None,
        node_category_strict_membership=None,
        payment_category_strict_membership=None,
        section_category_strict_membership=None,
        mirror_section_category_strict_membership=None,
        function_category_strict_membership=None,
        project_category_strict_membership=None,
        funding_category_strict_membership=None,
        ledger_category_strict_membership=None,
        payment_request_category_strict_membership=None,
        # simulation_state
        strict_simulation_state=0,
        simulation_state=None, transit_simulation_state = None, omit_transit=0,
        input_simulation_state=None, output_simulation_state=None,
        reserved_kw=None,
        # variations
        variation_text=None, sub_variation_text=None,
        variation_category=None,
        transformed_variation_text=None,
        # uids
        resource_uid=None, node_uid=None, section_uid=None, payment_uid=None,
        mirror_node_uid=None, mirror_section_uid=None, function_uid=None,
        project_uid=None, funding_uid=None, ledger_uid=None,
        payment_request_uid=None,
        # omit input and output
        omit_input=0,
        omit_output=0,
        omit_asset_increase=0,
        omit_asset_decrease=0,
        # interpolation_method
        interpolation_method='default',
        # group by
        group_by_node=0,
        group_by_node_category=0,
        group_by_node_category_strict_membership=0,
        group_by_mirror_node=0,
        group_by_mirror_node_category=0,
        group_by_mirror_node_category_strict_membership=0,
        group_by_section=0,
        group_by_section_category=0,
        group_by_section_category_strict_membership=0,
        group_by_mirror_section=0,
        group_by_mirror_section_category=0,
        group_by_mirror_section_category_strict_membership=0,
        group_by_payment=0,
        group_by_payment_category=0,
        group_by_payment_category_strict_membership=0,
        group_by_sub_variation=0,
        group_by_variation=0,
        group_by_movement=0,
        group_by_resource=0,
        group_by_project=0,
        group_by_project_category=0,
        group_by_project_category_strict_membership=0,
        group_by_funding=0,
        group_by_funding_category=0,
        group_by_funding_category_strict_membership=0,
        group_by_ledger=0,
        group_by_ledger_category=0,
        group_by_ledger_category_strict_membership=0,
        group_by_payment_request=0,
        group_by_payment_request_category=0,
        group_by_payment_request_category_strict_membership=0,
        group_by_function=0,
        group_by_function_category=0,
        group_by_function_category_strict_membership=0,
        group_by_date=0,
        group_by_time_sequence_list=None,
        # sort_on
        sort_on=None,
        group_by=None,
        # selection
        selection_domain=None,
        selection_report=None,
        # keywords for related keys
        **kw):
      """
      Generates keywords and calls buildSQLQuery

      - omit_mirror_date: normally, date's parameters are only based on date
        column. If 0, it also used the mirror_date column.
      """
      new_kw = {}
      sql_kw = {
        'from_table_list': [],
        # Set of catalog aliases that must be joined in the ZSQLMethod ('foo'
        # meaning something along the lines of 'foo.uid = stock.foo_uid')
        'selection_domain_catalog_alias_set': [],
        # input and output are used by getTrackingList
        'input': input,
        'output': output,
        # BBB
        'selection_domain': None,
        'selection_report': None,
      }

      if selection_domain is None:
        sql_kw['selection_domain_from_expression'] = None
        sql_kw['selection_domain_where_expression'] = None
      else:
        # Pre-render selection_domain, as it is easier done here than in DTML.
        if isinstance(selection_domain, dict):
          selection_domain_dict = selection_domain
        else:
          selection_domain_dict = selection_domain.asDomainDict()
        if 'ledger' in selection_domain_dict:
          # XXX: what if both 'node' and 'ledger' are present ?
          # Finer configuration may be needed here.
          query_table_alias = 'ledger'
        else:
          query_table_alias = 'node'
        selection_domain_sql_dict = self.getPortalObject().portal_catalog.buildSQLQuery(
          selection_domain=selection_domain,
          query_table_alias=query_table_alias,
        )
        sql_kw['selection_domain_from_expression'] = selection_domain_sql_dict['from_expression']
        sql_kw['from_table_list'].extend(selection_domain_sql_dict['from_table_list'])
        sql_kw['selection_domain_where_expression'] = selection_domain_sql_dict['where_expression']
        sql_kw['selection_domain_catalog_alias_set'].append(query_table_alias)
      if selection_report is not None:
        new_kw['selection_report'] = selection_report

      # Add sort_on parameter if defined
      if sort_on is not None:
        new_kw['sort_on'] = sort_on

      class DictMixIn(dict):
        def set(dictionary, key, value):
          result = bool(value)
          if result:
            dictionary[key] = value
          return result

        def setUIDList(dictionary, key, value, as_text=0):
          uid_list = self._generatePropertyUidList(value, as_text=as_text)
          return dictionary.set(key, uid_list)

      column_value_dict = DictMixIn()

      if omit_mirror_date:
        date_dict = {}
        if from_date :
          date_dict.setdefault('query', []).append(from_date)
          date_dict['range'] = 'min'
          if to_date :
            date_dict.setdefault('query', []).append(to_date)
            date_dict['range'] = 'minmax'
          elif at_date :
            date_dict.setdefault('query', []).append(at_date)
            date_dict['range'] = 'minngt'
        elif to_date :
          date_dict.setdefault('query', []).append(to_date)
          date_dict['range'] = 'max'
        elif at_date :
          date_dict.setdefault('query', []).append(at_date)
          date_dict['range'] = 'ngt'
        if date_dict:
          column_value_dict['date'] = date_dict
        if interpolation_method != 'default':
          if not group_by_time_sequence_list:
            if not (from_date and (to_date or at_date)):
              raise ValueError("date_range is required to use interpolation_method")
            # if we consider flow, we also select movement whose mirror date is
            # in the from_date/to_date range and movement whose
            # start_date/stop_date contains the report range.
            # The selected range is wider, but the selected movements will have an
            # "interpolation_ratio" applied to their quantity and prices.
            if to_date:
              column_value_dict['date'] = ComplexQuery(
                    Query(date=(from_date, to_date), range='minmax'),
                    Query(mirror_date=(from_date, to_date), range='minmax'),
                    ComplexQuery(
                        Query(mirror_date=from_date, range='min'),
                        Query(date=to_date, range='max'),
                        logical_operator="AND"),
                    ComplexQuery(
                        Query(date=from_date, range='min'),
                        Query(mirror_date=to_date, range='max'),
                        logical_operator="AND"),
                    logical_operator="OR"
                )
            else:
              column_value_dict['date'] = ComplexQuery(
                    Query(date=(from_date, at_date), range='minngt'),
                    Query(mirror_date=(from_date, at_date), range='minngt'),
                    ComplexQuery(
                        Query(mirror_date=from_date, range='min'),
                        Query(date=at_date, range='ngt'),
                        logical_operator="AND"),
                    ComplexQuery(
                        Query(date=from_date, range='min'),
                        Query(mirror_date=at_date, range='ngt'),
                        logical_operator="AND"),
                    logical_operator="OR"
                )
      else:
        column_value_dict['date'] = {'query': [to_date], 'range': 'ngt'}
        column_value_dict['mirror_date'] = {'query': [from_date], 'range': 'nlt'}

      column_value_dict.set('resource_uid', resource_uid)
      column_value_dict.set('payment_uid', payment_uid)
      column_value_dict.set('project_uid', project_uid)
      column_value_dict.set('funding_uid', funding_uid)
      column_value_dict.set('ledger_uid', ledger_uid)
      column_value_dict.set('payment_request_uid', payment_request_uid)
      column_value_dict.set('function_uid', function_uid)
      column_value_dict.set('section_uid', section_uid)
      column_value_dict.set('node_uid', node_uid)
      column_value_dict.set('mirror_node_uid', mirror_node_uid)
      column_value_dict.set('mirror_section_uid', mirror_section_uid)
      column_value_dict.setUIDList('resource_uid', resource)
      column_value_dict.setUIDList('aggregate_uid', item)
      column_value_dict.setUIDList('node_uid', node)
      column_value_dict.setUIDList('payment_uid', payment)
      column_value_dict.setUIDList('project_uid', project)
      column_value_dict.setUIDList('funding_uid', funding)
      column_value_dict.setUIDList('ledger_uid', ledger)
      column_value_dict.setUIDList('payment_request_uid', payment_request)
      column_value_dict.setUIDList('function_uid', function)

      sql_kw['transformed_uid'] = self._generatePropertyUidList(transformed_resource)

      column_value_dict.setUIDList('section_uid', section)
      column_value_dict.setUIDList('mirror_section_uid', mirror_section)

      # Handle variation_category as variation_text
      if variation_category:
        if variation_text:
          raise ValueError(
              "Passing both variation_category and variation_text is not supported")
        warn("variation_category is deprecated, please use variation_text instead",
             DeprecationWarning)
        if isinstance(variation_category, basestring):
          variation_category = (variation_category,)
        # variation text is a \n separated list of variation categories, but without
        # trailing nor leading \n
        variation_text = [
            "{}\n%".format(x) for x in variation_category] + [
            "%\n{}\n%".format(x) for x in variation_category] + [
            "%\n{}".format(x) for x in variation_category] + [
            "{}".format(x) for x in variation_category]

      column_value_dict.setUIDList('variation_text', variation_text,
                                   as_text=1)
      column_value_dict.setUIDList('sub_variation_text', sub_variation_text,
                                   as_text=1)
      new_kw['column_value_dict'] = column_value_dict.copy()

      related_key_dict = DictMixIn()
      # category membership
      related_key_dict.setUIDList('resource_category_uid', resource_category)
      related_key_dict.setUIDList('node_category_uid', node_category)
      related_key_dict.setUIDList('project_category_uid', project_category)
      related_key_dict.setUIDList('funding_category_uid', funding_category)
      related_key_dict.setUIDList('ledger_category_uid', ledger_category)
      related_key_dict.setUIDList('payment_request_category_uid', payment_request_category)
      related_key_dict.setUIDList('function_category_uid', function_category)
      related_key_dict.setUIDList('payment_category_uid', payment_category)
      related_key_dict.setUIDList('section_category_uid', section_category)
      related_key_dict.setUIDList('mirror_section_category_uid',
                                  mirror_section_category)
      # category strict membership
      related_key_dict.setUIDList('resource_category_strict_membership_uid',
                                  resource_category_strict_membership)
      related_key_dict.setUIDList('node_category_strict_membership_uid',
                                  node_category_strict_membership)
      related_key_dict.setUIDList('project_category_strict_membership_uid',
                                  project_category_strict_membership)
      related_key_dict.setUIDList('funding_category_strict_membership_uid',
                                  funding_category_strict_membership)
      related_key_dict.setUIDList('ledger_category_strict_membership_uid',
                                  ledger_category_strict_membership)
      related_key_dict.setUIDList('payment_request_category_strict_membership_uid',
                                  payment_request_category_strict_membership)
      related_key_dict.setUIDList('function_category_strict_membership_uid',
                                  function_category_strict_membership)
      related_key_dict.setUIDList('payment_category_strict_membership_uid',
                                  payment_category_strict_membership)
      related_key_dict.setUIDList('section_category_strict_membership_uid',
                                  section_category_strict_membership)
      related_key_dict.setUIDList(
        'mirror_section_category_strict_membership_uid',
        mirror_section_category_strict_membership)

      new_kw['related_key_dict'] = related_key_dict.copy()
      new_kw['related_key_dict_passthrough'] = kw
      # Check we do not get a known group_by
      related_group_by = []
      if group_by:
        if isinstance(group_by, basestring):
          group_by = (group_by,)
        for value in group_by:
          if value == "node_uid":
            group_by_node = 1
          elif value == 'mirror_node_uid':
            group_by_mirror_node = 1
          elif value ==  'section_uid':
            group_by_section = 1
          elif value == 'mirror_section_uid':
            group_by_mirror_section = 1
          elif value == 'payment_uid':
            group_by_payment = 1
          elif value == 'sub_variation_text':
            group_by_sub_variation = 1
          elif value == 'variation_text':
            group_by_variation = 1
          elif value == 'uid':
            group_by_movement = 1
          elif value == 'resource_uid':
            group_by_resource = 1
          elif value == 'project_uid':
            group_by_project = 1
          elif value == 'funding_uid':
            group_by_funding = 1
          elif value == 'ledger_uid':
            group_by_ledger = 1
          elif value == 'payment_request_uid':
            group_by_payment_request = 1
          elif value == "function_uid":
            group_by_function = 1
          elif value == 'date':
            group_by_date = 1
          else:
            related_group_by.append(value)
        if related_group_by:
          new_kw['related_key_dict_passthrough']['group_by_list'] = related_group_by

      new_kw['simulation_dict'] = self._getSimulationStateDict(
        simulation_state=simulation_state,
        omit_transit=omit_transit,
        input_simulation_state=input_simulation_state,
        output_simulation_state=output_simulation_state,
        transit_simulation_state=transit_simulation_state,
        strict_simulation_state=strict_simulation_state,
      )
      new_kw['omit_dict'] = {
        'input': omit_input,
        'output': omit_output,
        'asset_increase': omit_asset_increase,
        'asset_decrease': omit_asset_decrease,
      }
      if reserved_kw is not None:
        if not isinstance(reserved_kw, dict):
          # Not a dict when taken from URL, so, cast is needed
          # to make pop method available
          reserved_kw = dict(reserved_kw)
        new_kw['reserved_kw'] = {
          'omit_dict': {
            'input': reserved_kw.pop('omit_input', False),
            'output': reserved_kw.pop('omit_output', False),
          },
          'simulation_dict': self._getSimulationStateDict(**reserved_kw),
        }

      # build the group by expression
      # if we group by a criterion, we also add this criterion to the select
      # expression, unless it is already selected in Resource_zGetInventoryList
      # the caller can also pass select_dict or select_list. select_expression,
      # which is deprecated in ZSQLCatalog is not supported here.
      select_dict = kw.get('select_dict', {})
      select_dict.update(dict.fromkeys(list(kw.pop('select_list', [])) + related_group_by))
      new_kw['select_dict'] = select_dict
      related_key_select_expression_list = []

      column_group_by_expression_list = []
      related_key_group_by_expression_list = []
      if group_by_node:
        column_group_by_expression_list.append('node_uid')
      if group_by_mirror_node:
        column_group_by_expression_list.append('mirror_node_uid')
      if group_by_section:
        column_group_by_expression_list.append('section_uid')
      if group_by_mirror_section:
        column_group_by_expression_list.append('mirror_section_uid')
      if group_by_payment:
        column_group_by_expression_list.append('payment_uid')
      if group_by_sub_variation:
        column_group_by_expression_list.append('sub_variation_text')
      if group_by_variation:
        column_group_by_expression_list.append('variation_text')
      if group_by_movement:
        column_group_by_expression_list.append('uid')
      if group_by_resource:
        column_group_by_expression_list.append('resource_uid')
      if group_by_project:
        column_group_by_expression_list.append('project_uid')
      if group_by_funding:
        column_group_by_expression_list.append('funding_uid')
      if group_by_ledger:
        column_group_by_expression_list.append('ledger_uid')
      if group_by_payment_request:
        column_group_by_expression_list.append('payment_request_uid')
      if group_by_function:
        column_group_by_expression_list.append('function_uid')
      if group_by_date:
        column_group_by_expression_list.append('date')

      if column_group_by_expression_list:
        new_kw['column_group_by'] = column_group_by_expression_list

      if group_by_section_category:
        related_key_group_by_expression_list.append('section_category_uid')
        related_key_select_expression_list.append('section_category_uid')
      if group_by_section_category_strict_membership:
        related_key_group_by_expression_list.append(
            'section_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'section_category_strict_membership_uid')
      if group_by_mirror_section_category:
        related_key_group_by_expression_list.append('mirror_section_category_uid')
        related_key_select_expression_list.append('mirror_section_category_uid')
      if group_by_mirror_section_category_strict_membership:
        related_key_group_by_expression_list.append(
            'mirror_section_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'mirror_section_category_strict_membership_uid')
      if group_by_node_category:
        related_key_group_by_expression_list.append('node_category_uid')
        related_key_select_expression_list.append('node_category_uid')
      if group_by_node_category_strict_membership:
        related_key_group_by_expression_list.append(
            'node_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'node_category_strict_membership_uid')
      if group_by_mirror_node_category:
        related_key_group_by_expression_list.append('mirror_node_category_uid')
      if group_by_mirror_node_category_strict_membership:
        related_key_group_by_expression_list.append(
            'mirror_node_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'mirror_node_category_strict_membership_uid')
      if group_by_payment_category:
        related_key_group_by_expression_list.append('payment_category_uid')
        related_key_select_expression_list.append('payment_category_uid')
      if group_by_payment_category_strict_membership:
        related_key_group_by_expression_list.append(
            'payment_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'payment_category_strict_membership_uid')
      if group_by_function_category:
        related_key_group_by_expression_list.append('function_category_uid')
        related_key_select_expression_list.append('function_category_uid')
      if group_by_function_category_strict_membership:
        related_key_group_by_expression_list.append(
            'function_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'function_category_strict_membership_uid')
      if group_by_project_category:
        related_key_group_by_expression_list.append('project_category_uid')
        related_key_select_expression_list.append('project_category_uid')
      if group_by_project_category_strict_membership:
        related_key_group_by_expression_list.append(
            'project_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'project_category_strict_membership_uid')
      if group_by_funding_category:
        related_key_group_by_expression_list.append('funding_category_uid')
        related_key_select_expression_list.append('funding_category_uid')
      if group_by_funding_category_strict_membership:
        related_key_group_by_expression_list.append(
            'funding_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'funding_category_strict_membership_uid')
      if group_by_ledger_category:
        related_key_group_by_expression_list.append('ledger_category_uid')
        related_key_select_expression_list.append('ledger_category_uid')
      if group_by_ledger_category_strict_membership:
        related_key_group_by_expression_list.append(
            'ledger_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'ledger_category_strict_membership_uid')
      if group_by_payment_category:
        related_key_group_by_expression_list.append('payment_request_category_uid')
        related_key_select_expression_list.append('payment_request_category_uid')
      if group_by_payment_request_category_strict_membership:
        related_key_group_by_expression_list.append(
            'payment_request_category_strict_membership_uid')
        related_key_select_expression_list.append(
            'payment_request_category_strict_membership_uid')

      if related_key_group_by_expression_list:
        new_kw['related_key_group_by'] = related_key_group_by_expression_list
      if related_key_select_expression_list:
        new_kw['related_key_select_expression_list'] =\
                related_key_select_expression_list

# XXX
      sql_kw['group_by_time_sequence_list'] = group_by_time_sequence_list
      return sql_kw, new_kw

    #######################################################
    # Inventory management
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventory')
    def getInventory(self, src__=0, simulation_period='', **kw):
      """
      Returns an inventory of a single or multiple resources on a single or
      multiple nodes as a single float value

      from_date (>=) - only take rows which date is >= from_date

      to_date   (<)  - only take rows which date is < to_date

      at_date   (<=) - only take rows which date is <= at_date

      resource (only in generic API in simulation)

      node           -  only take rows in stock table which node_uid is
                        equivalent to node

      payment        -  only take rows in stock table which payment_uid is
                        equivalent to payment

      section        -  only take rows in stock table which section_uid is
                        equivalent to section

      mirror_section -  only take rows in stock table which mirror_section_uid is
                        mirror_section

      resource_category  -  only take rows in stock table which
                        resource_uid is member of resource_category

      node_category   - only take rows in stock table which node_uid is
                        member of section_category

      payment_category   -  only take rows in stock table which payment_uid
                            is in section_category

      section_category -  only take rows in stock table which section_uid is
                          member of section_category

      mirror_section_category - only take rows in stock table which
                                mirror_section_uid is member of
                                mirror_section_category

      node_filter     - only take rows in stock table which node_uid
                        matches node_filter

      payment_filter  - only take rows in stock table which payment_uid
                        matches payment_filter

      section_filter  - only take rows in stock table which section_uid
                        matches section_filter

      mirror_section_filter - only take rows in stock table which
                              mirror_section_uid matches mirror_section_filter

      variation_text -  only take rows in stock table with specified
                        variation_text.
                        XXX this way of implementing variation selection is far
                        from perfect

      sub_variation_text - only take rows in stock table with specified
                        variation_text

      variation_category - variation or list of possible variations (it is not
                        a cross-search ; SQL query uses OR).
                        Deprecated, use variation_text.

      simulation_state - only take rows with specified simulation_state

      transit_simulation_state - specifies which states are transit states

      omit_transit   -  do not evaluate transit_simulation_state

      input_simulation_state - only take rows with specified simulation_state
                        and quantity > 0

      output_simulation_state - only take rows with specified simulation_state
                        and quantity < 0

      interpolation_method - Method to consider movements when calculating flows.
        * (default): Consider the movement decreases 100% of source stock on
          start date and increase 100% of the destination node stock on stop
          date.
        * linear: consider the movement decreases source stock and increase
          destination stock linearly between start date and stop date.
        * all_or_nothing: consider only movement who starts after the beginning of
          the query period and finishes after the end of the query period.
        * one_for_all: consider the movement fully as long as it is partially
          contained in the query period.

      ignore_variation -  do not take into account variation in inventory
                        calculation (useless on getInventory, but useful on
                        getInventoryList)

      standardise    -  provide a standard quantity rather than an SKU (XXX
                        not implemented yet)

      omit_simulation - doesn't take into account simulation movements

      only_accountable - Only take into account accountable movements. By
                        default, only movements for which isAccountable() is
                        true will be taken into account.

      omit_input     -  doesn't take into account movement with quantity > 0

      omit_output    -  doesn't take into account movement with quantity < 0

      omit_asset_increase - doesn't take into account movement with asset_price > 0

      omit_asset_decrease - doesn't take into account movement with asset_price < 0

      selection_domain, selection_report - see ListBox

      group_by_variation - (useless on getInventory, but useful on
                        getInventoryList)

      group_by_node  -  (useless on getInventory, but useful on
                        getInventoryList)

      group_by_mirror_node - (useless on getInventory, but useful on
                        getInventoryList)

      group_by_sub_variation - (useless on getInventory, but useful on
                        getInventoryList)

      group_by_movement - (useless on getInventory, but useful on
                        getInventoryList)

      precision - the precision used to round quantities and prices.

      metric_type   - convert the results to a specific metric_type

      quantity_unit - display results using this specific quantity unit

      transformed_resource - one, or several resources. list resources that can
                             be produced using those resources as input in a
                             transformation.
                             relative_resource_url for each returned line will
                             point to the transformed resource, while the stock
                             will be the stock of the produced resource,
                             expressed in number of transformed resources.
      transformed_variation_text - to be used with transformed_resource, to
                                   to refine the transformation selection only
                                   to those using variated resources as input.

      **kw           -  if we want extended selection with more keywords (but
                        bad performance) check what we can do with
                        buildSQLQuery

      NOTE: we may want to define a parameter so that we can select the kind of
      inventory statistics we want to display (ex. sum, average, cost, etc.)
      """
      # JPS: this is a hint for implementation of xxx_filter arguments
      # node_uid_count = portal_catalog.countResults(**node_filter)
      # if node_uid_count not too big:
      #   node_uid_list = cache(portal_catalog(**node_filter))
      #   pass this list to ZSQL method
      # else:
      #   build a table in MySQL
      #   and join that table with the stock table
      method = getattr(self,'get%sInventoryList' % simulation_period)
      kw['ignore_group_by'] = 1
      result = method(inventory_list=0, src__=src__, **kw)
      if src__:
        return result

      total_result = 0.0
      if len(result) > 0:
        if len(result) != 1:
          raise ValueError, 'Sorry we must have only one'
        result = result[0]

        if hasattr(result, "converted_quantity"):
          total_result = result.converted_quantity
        else:
          inventory = result.total_quantity
          if inventory is not None:
            total_result = inventory

      return total_result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      return self.getInventory(simulation_period='Current', **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - reserved_inventory)
      """
      return self.getInventory(simulation_period='Available', **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns future inventory
      """
      return self.getInventory(simulation_period='Future', **kw)

    def _getDefaultGroupByParameters(self, ignore_group_by=0,
        group_by_node=0, group_by_mirror_node=0,
        group_by_section=0, group_by_mirror_section=0,
        group_by_payment=0, group_by_project=0, group_by_funding=0,
        group_by_ledger=0, group_by_function=0,
        group_by_variation=0, group_by_sub_variation=0,
        group_by_movement=0, group_by_date=0,
        group_by_section_category=0,
        group_by_section_category_strict_membership=0,
        group_by_resource=None,
        group_by_time_sequence_list=(),
        group_by=None,
        **ignored):
      """
      Set defaults group_by parameters

      If ignore_group_by is true, this function returns an empty dict.

      If any group-by is provided, automatically group by resource aswell
      unless group_by_resource is explicitely set to false.
      If no group by is provided, use the default group by: movement, node and
      resource.
      """
      new_group_by_dict = {}
      if not ignore_group_by and group_by is None:
        if group_by_node or group_by_mirror_node or group_by_section or \
           group_by_project or group_by_funding or group_by_ledger or \
           group_by_function or group_by_mirror_section or group_by_payment or \
           group_by_sub_variation or group_by_variation or \
           group_by_movement or group_by_date or group_by_section_category or\
           group_by_section_category_strict_membership or \
           group_by_time_sequence_list:
          if group_by_resource is None:
            group_by_resource = 1
          new_group_by_dict['group_by_resource'] = group_by_resource
        elif group_by_resource is None:
          new_group_by_dict['group_by_movement'] = 1
          new_group_by_dict['group_by_node'] = 1
          new_group_by_dict['group_by_resource'] = 1
      return new_group_by_dict

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryList')
    def getInventoryList(self, src__=0, optimisation__=True,
                         ignore_variation=0, standardise=0,
                         omit_simulation=0,
                         only_accountable=True,
                         default_stock_table='stock',
                         interpolation_method='default',
                         selection_domain=None, selection_report=None,
                         statistic=0, inventory_list=1,
                         precision=None, connection_id=None,
                         **kw):
      """
        Returns a list of inventories for a single or multiple
        resources on a single or multiple nodes, grouped by resource,
        node, section, etc. Every line defines an inventory value for
        a given group of resource, node, section.
        NOTE: we may want to define a parameter so that we can select
        the kind of inventory statistics we want to display (ex. sum,
        average, cost, etc.)

        Optimisation queries.
        Optimisation of a stock lookup is done to avoid a table scan
        of all lines corresponding to a given node, section or payment,
        because they grow with time and query time should not.
        First query: Fetch fitting full inventory dates.
          For each node, section or payment, find the first anterior full
          inventory.
        Second query: Fetch full inventory amounts.
          Fetch values of inventory identified in the first query.
        Third query: Classic stock table read.
          Fetch all rows in stock table which are posterior to the inventory.
        Final result
          Add results of the second and third queries, and return it.

        Missing optimisations:
         - In a getInventory case where everything is specified for the
           resource, it's not required for the inventory to be full, it
           just need to be done for the right resource.
           If the resource isn't completely defined, we require inventory
           to be full, which is implemented.
         - Querying multiple nodes/categories/payments in one call prevents
           from using optimisation, it should be equivalent to multiple calls
           on individual nodes/categories/payments.
         -
      """
      getCategory = self.getPortalObject().portal_categories.getCategoryUid

      result_column_id_dict = {}

      metric_type = kw.pop('metric_type', None)
      quantity_unit = kw.pop('quantity_unit', None)
      quantity_unit_uid = None

      if quantity_unit is not None:

        if isinstance(quantity_unit, str):
          quantity_unit_uid = getCategory(quantity_unit, 'quantity_unit')
          if quantity_unit_uid is not None:
            result_column_id_dict['converted_quantity'] = None
            if metric_type is None:
              # use the default metric type
              metric_type = quantity_unit.split("/", 1)[0]
        elif isinstance(quantity_unit, (int, float)):
          # quantity_unit used to be a numerical parameter..
          raise ValueError('Numeric values for quantity_unit are not supported')


      convert_quantity_result = False
      if metric_type is not None:
        metric_type_uid = getCategory(metric_type, 'metric_type')

        if metric_type_uid is not None:
          convert_quantity_result = True
          kw['metric_type_uid'] = Query(
                                    metric_type_uid=metric_type_uid,
                                    table_alias_list=(("measure", "measure"),))

      if src__:
        sql_source_list = []
      # If no group at all, give a default sort group by
      kw.update(self._getDefaultGroupByParameters(**kw))
      base_inventory_kw = {
        'stock_table_id': default_stock_table,
        'src__': src__,
        'ignore_variation': ignore_variation,
        'interpolation_method': interpolation_method,
        'standardise': standardise,
        'omit_simulation': omit_simulation,
        'only_accountable': only_accountable,
        'precision': precision,
        'inventory_list': inventory_list,
        'connection_id': connection_id,
        'statistic': statistic,
        'convert_quantity_result': convert_quantity_result,
        'quantity_unit_uid': quantity_unit_uid,
      }
      # Get cached data
      if getattr(self, "Resource_zGetInventoryCacheResult", None) is not None and \
              optimisation__ and (not kw.get('from_date')) and \
              'transformed_resource' not in kw \
              and "category" not in str(kw) \
              and "group_by_time_sequence_list" not in kw:
        # Here is the different kind of date
        # from_date : >=
        # to_date   : <
        # at_date   : <=
        # As we just have from_date, it means that we must use
        # the to_date for the cache in order to avoid double computation
        # of the same line
        at_date = kw.pop("at_date", None)
        if at_date is None:
          to_date = kw.pop("to_date", None)
        else:
          # add one second so that we can use to_date
          to_date = at_date + MYSQL_MIN_DATETIME_RESOLUTION
        try:
          cached_result, cached_date = self._getCachedInventoryList(
              to_date=to_date,
              sql_kw=kw,
              **base_inventory_kw)
        except StockOptimisationError:
          cached_result = []
          kw['to_date'] = to_date
        else:
          if src__:
            sql_source_list.extend(cached_result)
          # Now must generate query for date diff
          kw['to_date'] = to_date
          kw['from_date'] = cached_date
      else:
        cached_result = []
      sql_kw, new_kw = self._generateKeywordDict(interpolation_method=interpolation_method, **kw)
      # Copy kw content as _generateSQLKeywordDictFromKeywordDict
      # remove some values from it
      try:
        new_kw_copy = deepcopy(new_kw)
      except TypeError:
        # new_kw contains wrong parameters
        # as optimisation has already been disable we
        # do not care about the deepcopy
        new_kw_copy = new_kw
      stock_sql_kw = self._generateSQLKeywordDictFromKeywordDict(
          table=default_stock_table, sql_kw=sql_kw, new_kw=new_kw_copy)
      stock_sql_kw.update(base_inventory_kw)

        # TODO: move in _generateSQLKeywordDictFromKeywordDict
      if interpolation_method in ('linear', 'all_or_nothing', 'one_for_all'):
          # XXX only DateTime instance are supported
        from_date = kw.get('from_date')
        if from_date:
          from_date = from_date.toZone("UTC")
        to_date = kw.get('to_date')
        if to_date:
          to_date = to_date.toZone("UTC")
        at_date = kw.get('at_date')
        if at_date:
          at_date = at_date.toZone("UTC")
        stock_sql_kw['interpolation_method_from_date'] = from_date
        stock_sql_kw['interpolation_method_to_date'] = to_date
        stock_sql_kw['interpolation_method_at_date'] = at_date
      elif interpolation_method != 'default':
        raise ValueError("Unsupported interpolation_method %r" % (interpolation_method,))

      delta_result = self.Resource_zGetInventoryList(
          **stock_sql_kw)
      if src__:
        sql_source_list.append(delta_result)
        result = ';\n-- NEXT QUERY\n'.join(sql_source_list)
      else:
        if cached_result:
            result = self._addBrainResults(delta_result, cached_result, new_kw)
        else:
            result = delta_result
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryCacheLag')
    def getInventoryCacheLag(self):
      """
      Returns a duration, in days, for stock cache management.
      If data in stock cache is older than lag compared to query's date
      (at_date or to_date), then it becomes a "soft miss": use found value,
      but add a new entry to cache at query's date minus half the lag.
      So this value should be:
      - Small enough that few enough rows need to be table-scanned for
        average queries (probably queries against current date).
      - Large enough that few enough documents get modified past that date,
        otherwise cache entries would be removed from cache all the time.
      """
      return self.SimulationTool_getInventoryCacheLag()

    def _getCachedInventoryList(self, to_date, sql_kw, stock_table_id, src__=False, **kw):
      """
      Try to get a cached inventory list result
      If not existing, fill the cache
      """
      Resource_zGetInventoryList = self.Resource_zGetInventoryList
      # Generate the SQL source without date parameter
      # This will be the cache key
      try:
          no_date_kw = deepcopy(sql_kw)
      except TypeError:
          LOG("SimulationTool._getCachedInventoryList", WARNING,
              "Failed copying sql_kw, disabling stock cache",
              error=True)
          raise StockOptimisationError
      no_date_sql_kw, no_date_new_kw = self._generateKeywordDict(**no_date_kw)
      no_date_stock_sql_kw = self._generateSQLKeywordDictFromKeywordDict(
        table=stock_table_id, sql_kw=no_date_sql_kw,
        new_kw=no_date_new_kw)
      kw.update(no_date_stock_sql_kw)
      if src__:
        sql_source_list = []
      # Generate the cache key (md5 of query source)
      sql_text_hash = md5(Resource_zGetInventoryList(
        stock_table_id=stock_table_id,
        src__=1,
        **kw)).digest()
      # Try to get result from cache
      Resource_zGetInventoryCacheResult = self.Resource_zGetInventoryCacheResult
      inventory_cache_kw = {'query': sql_text_hash}
      if to_date is not None:
        inventory_cache_kw['date'] = to_date
      try:
          cached_sql_result = Resource_zGetInventoryCacheResult(**inventory_cache_kw)
      except ProgrammingError, (code, _):
          if code != NO_SUCH_TABLE:
            raise
          # First use of the optimisation, we need to create the table
          LOG("SimulationTool._getCachedInventoryList", INFO,
              "Creating inventory cache stock")
          if src__:
              sql_source_list.append(self.SimulationTool_zCreateInventoryCache(src__=1))
          else:
              self.SimulationTool_zCreateInventoryCache()
          cached_sql_result = None

      if src__:
        sql_source_list.append(Resource_zGetInventoryCacheResult(src__=1, **inventory_cache_kw))
      if cached_sql_result:
        brain_result = loads(cached_sql_result[0].result)
        # Rebuild the brains
        cached_result = Results(
          (brain_result['items'], brain_result['data']),
          brains=getBrain(
            Resource_zGetInventoryList.class_file_,
            Resource_zGetInventoryList.class_name_,
          ),
          parent=self,
        )
      else:
        cached_result = []
      cache_lag = self.getInventoryCacheLag()
      if cached_sql_result and (to_date is None or (to_date - DateTime(cached_sql_result[0].date) < cache_lag)):
        cached_date = DateTime(cached_sql_result[0].date)
        result = cached_result
      elif to_date is not None:
        # Cache miss, or hit with old data: store a new entry in cache.
        # Don't store it at to_date, as it risks being flushed soon (ie, when
        # any document older than to_date gets reindexed in stock table).
        # Don't store it at to_date - cache_lag, as it would risk expiring
        # soon as we store it (except if to_date is fixed for many queries,
        # which we cannot tell here).
        # So store it at half the cache_lag before to_date.
        cached_date = to_date - cache_lag / 2
        new_cache_kw = deepcopy(sql_kw)
        if cached_result:
          # We can use cached result to generate new cache result
          new_cache_kw['from_date'] = DateTime(cached_sql_result[0].date)
        sql_kw, new_kw = self._generateKeywordDict(
          to_date=cached_date,
          **new_cache_kw)
        kw.update(self._generateSQLKeywordDictFromKeywordDict(
            table=stock_table_id,
            sql_kw=sql_kw,
            new_kw=new_kw,
          )
        )
        new_result = Resource_zGetInventoryList(
          stock_table_id=stock_table_id,
          src__=src__,
          **kw)
        if src__:
          sql_source_list.append(new_result)
        else:
          result = self._addBrainResults(new_result, cached_result, new_kw)
          self.Resource_zInsertInventoryCacheResult(
            query=sql_text_hash,
            date=cached_date,
            result=dumps({
              'items': result.__items__,
              'data': result._data,
            }),
          )
      else:
        # Cache miss and this getInventory() not specifying to_date,
        # and other getInventory() have not created usable caches.
        # In such case, do not create cache, do not use cache.
        result = []
        cached_date = None
      if src__:
        result = sql_source_list
      return result, cached_date

    def _addBrainResults(self, first_result, second_result, new_kw):
      """
      Build a Results which is the addition of two other result
      """
      # This part defined key to group lines from different Results
      group_by_id_list = []
      group_by_id_list_append = group_by_id_list.append

      for group_by_id in new_kw.get('column_group_by', []):
        if group_by_id == 'uid':
          group_by_id_list_append('stock_uid')
        else:
          group_by_id_list_append(group_by_id)
      # Add related key group by
      related_key_dict_passthrough = new_kw.get("related_key_dict_passthrough", {})
      group_by_list = related_key_dict_passthrough.get('group_by_list', [])
      cannot_group_by = set(group_by_list).difference(
        related_key_dict_passthrough.get('select_list', []),
      )
      if cannot_group_by:
        # XXX-Aurel : to review & change, must prevent coming here before
        raise ValueError("Impossible to group by %s" % (cannot_group_by, ))
      group_by_id_list += group_by_list

      if len(group_by_id_list):
        def getInventoryListKey(line):
          """
          Generate a key based on values used in SQL group_by
          """
          return tuple([line[x] for x in group_by_id_list])

      else:
        def getInventoryListKey(line):
          """
          Return a dummy key, all line will be summed
          """
          return "dummy"
      result_column_id_dict = {
        'inventory': None,
        'total_quantity': None,
        'total_price': None
      }
      def addLineValues(line_a=None, line_b=None):
        """
        Add columns of 2 lines and return a line with same
        schema. If one of the parameters is None, returns the
        other parameters.

        Arithmetic modifications on additions:
        None + x = x
        None + None = None
        """
        if line_a is None:
          return line_b
        if line_b is None:
          return line_a
        # Create a new Shared.DC.ZRDB.Results.Results.__class__
        # instance to add the line values.
        # the logic for the 5 lines below is taken from
        # Shared.DC.ZRDB.Results.Results.__getitem__
        Result = line_a.__class__
        parent = line_a.aq_parent
        result = Result((), parent)
        try:
          # We must copy the path so that getObject works
          setattr(result, 'path', line_a.path)
        except ValueError: # XXX: ValueError ? really ?
          # getInventory return no object, so no path available
          pass
        if parent is not None:
          result = result.__of__(parent)
        for key in line_a.__record_schema__:
          value = line_a[key]
          if key in result_column_id_dict:
            value_b = line_b[key]
            if None not in (value, value_b):
              result[key] = value + value_b
            elif value is not None:
              result[key] = value
            else:
              result[key] = value_b
          elif line_a[key] == line_b[key]:
            result[key] = line_a[key]
          elif key not in ('date', 'stock_uid', 'path'):
            # There are 2 possible reasons to end up here:
            # - key corresponds to a projected column for which are neither
            #   known aggregated columns (in which case they should be in
            #   result_column_id_dict) nor part of grouping columns, and the
            #   result happens to be unstable. There are cases in ERP5 where
            #   such result is suposed to be stable, for example
            #   group_by=('xxx_uid'), selection_list=('xxx_path') because the
            #   relation is bijective (although the database doesn't know it).
            #   These should result in stable results (but don't necessarily
            #   do, ex: xxx_title when object title has been changed between
            #   cache fill and cache lookup).
            # - line_a and line_b are indeed mismatched, and code calling us
            #   has a bug.
            LOG('InventoryTool.getInventoryList.addLineValues',
              PROBLEM,
              'mismatch for %s column: %s and %s' % (
                key, line_a[key], line_b[key]))
        return result
      # Add lines
      inventory_list_dict = {}
      for line_list in (first_result, second_result):
        for line in line_list:
          line_key = getInventoryListKey(line)
          line_a = inventory_list_dict.get(line_key)
          inventory_list_dict[line_key] = addLineValues(line_a, line)
      sorted_inventory_list = inventory_list_dict.values()
      # Sort results manually when required
      sort_on = new_kw.get('sort_on')
      if sort_on:
        def cmp_inventory_line(line_a, line_b):
          """
            Compare 2 inventory lines and sort them according to
            sort_on parameter.
          """
          result = 0
          for key, sort_direction in sort_on:
            try:
              result = cmp(line_a[key], line_b[key])
            except KeyError:
              raise Exception('Impossible to sort result since columns sort '
                'happens on are not available in result: %r' % (key, ))
            if result:
              if not sort_direction.upper().startswith('A'):
                # Default sort is ascending, if a sort is given and
                # it does not start with an 'A' then reverse sort.
                # Tedious syntax checking is MySQL's job, and
                # happened when queries were executed.
                result *= -1
              break
          return result
        sorted_inventory_list.sort(cmp_inventory_line)
      # Brain is rebuild properly using tuple not r instance
      column_list = first_result._searchable_result_columns()
      column_name_list = [x['name'] for x in column_list]
      # Rebuild a result object based on added results
      Resource_zGetInventoryList = self.Resource_zGetInventoryList
      return Results(
        (column_list, tuple([tuple([getattr(y, x) for x in column_name_list]) \
          for y in sorted_inventory_list])),
        parent=self,
        brains=getBrain(
          Resource_zGetInventoryList.class_file_,
          Resource_zGetInventoryList.class_name_,
        ),
      )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getConvertedInventoryList')
    def getConvertedInventoryList(self, simulation_period='', **kw):
      """
      Return list of inventory with a 'converted_quantity' additional column,
      which contains the sum of measurements for the specified metric type,
      expressed in the 'quantity_unit' unit.

      metric_type   - category
      quantity_unit - category
      """

      warn('getConvertedInventoryList is Deprecated, use ' \
           'getInventory instead.', DeprecationWarning)

      method = getattr(self,'get%sInventoryList' % simulation_period)

      return method(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAllInventoryList')
    def getAllInventoryList(self, src__=0, **kw):
      """
      Returns list of inventory, for all periods.
      Performs 1 SQL request for each simulation state, and merge the results.
      Rename relevant columns with a '${simulation}_' prefix
      (ex: 'total_price' -> 'current_total_price').
      """
      columns = ('total_quantity', 'total_price', 'converted_quantity')

      # Guess the columns to use to identify each row, by looking at the GROUP
      # clause. Note that the call to 'mergeZRDBResults' will crash if the GROUP
      # clause contains a column not requested in the SELECT clause.
      kw.update(self._getDefaultGroupByParameters(**kw), ignore_group_by=1)
      group_by_list = self._generateKeywordDict(**kw)[1].get('group_by_list', ())

      results = []
      edit_result = {}
      get_false_value = lambda row, column_name: row.get(column_name) or 0

      for simulation in 'current', 'available', 'future':
        method = getattr(self, 'get%sInventoryList' % simulation.capitalize())
        rename = {'inventory': None} # inventory column is deprecated
        for column in columns:
          rename[column] = new_name = '%s_%s' % (simulation, column)
          edit_result[new_name] = get_false_value
        results += (method(src__=src__, **kw), rename),

      if src__:
        return ';\n-- NEXT QUERY\n'.join(r[0] for r in results)
      return mergeZRDBResults(results, group_by_list, edit_result)


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryList')
    def getCurrentInventoryList(self, omit_transit=1,
                                transit_simulation_state=None, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['simulation_state'] = portal.getPortalCurrentInventoryStateList() + \
                               portal.getPortalTransitInventoryStateList()
      if transit_simulation_state is None:
        transit_simulation_state = portal.getPortalTransitInventoryStateList()

      return self.getInventoryList(
                            omit_transit=omit_transit,
                            transit_simulation_state=transit_simulation_state,
                            **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryList')
    def getAvailableInventoryList(self, omit_transit=1, transit_simulation_state=None, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      portal = self.getPortalObject()
      if transit_simulation_state is None:
        transit_simulation_state = portal.getPortalTransitInventoryStateList()
      kw['simulation_state'] = portal.getPortalCurrentInventoryStateList() + \
                               portal.getPortalTransitInventoryStateList()
      reserved_kw = {'simulation_state': portal.getPortalReservedInventoryStateList(),
                     'transit_simulation_state': transit_simulation_state,
                     'omit_input': 1}
      return self.getInventoryList(reserved_kw=reserved_kw, omit_transit=omit_transit,
                     transit_simulation_state=transit_simulation_state, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['simulation_state'] = portal.getPortalFutureInventoryStateList() + \
                               portal.getPortalTransitInventoryStateList() + \
                               portal.getPortalReservedInventoryStateList() + \
                               portal.getPortalCurrentInventoryStateList()
      return self.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryStat')
    def getInventoryStat(self, simulation_period='', **kw):
      """
      getInventoryStat is the pending to getInventoryList in order to
      provide statistics on getInventoryList lines in ListBox such as:
      total of inventories, number of variations, number of different
      nodes, etc.
      """
      kw['group_by_variation'] = 0
      method = getattr(self,'get%sInventoryList' % simulation_period)
      return method(statistic=1, inventory_list=0, optimisation__=False,
                                   ignore_group_by=1, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of current inventory grouped by section or site
      """
      return self.getInventoryStat(simulation_period='Current', **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryStat')
    def getAvailableInventoryStat(self, **kw):
      """
      Returns statistics of available inventory grouped by section or site
      """
      return self.getInventoryStat(simulation_period='Available', **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of future inventory grouped by section or site
      """
      return self.getInventoryStat(simulation_period='Future', **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryChart')
    def getInventoryChart(self, src__=0, **kw):
      """
      Returns a list of couples derived from getInventoryList in order
      to feed a chart renderer. Each couple consist of a label
      (node, section, payment, combination of node & section, etc.)
      and an inventory value.

      Mostly useful for charts in ERP5 forms.
      """
      result = self.getInventoryList(src__=src__, **kw)
      if src__ :
        return result

      return map(lambda r: (r.node_title, r.total_quantity), result)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalObject()\
        .getPortalCurrentInventoryStateList()
      return self.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['simulation_state'] = portal.getPortalFutureInventoryStateList() + \
                               portal.getPortalTransitInventoryStateList() + \
                               portal.getPortalReservedInventoryStateList() + \
                               portal.getPortalCurrentInventoryStateList()
      return self.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryAssetPrice')
    def getInventoryAssetPrice(self, src__=0,
                               simulation_period='',
                               valuation_method=None,
                               **kw):
      """
      Same thing as getInventory but returns an asset
      price rather than an inventory.

      If valuation method is None, returns the sum of total prices.

      Else it should be a string, in:
        Filo
        Fifo
        WeightedAverage
        MonthlyWeightedAverage
        MovingAverage
      When using a specific valuation method, a resource_uid is expected
      as well as one of (section_uid or node_uid).
      """
      if valuation_method is None:
        method = getattr(self,'get%sInventoryList' % simulation_period)
        kw['ignore_group_by'] = 1
        result = method( src__=src__, inventory_list=0, **kw)
        if src__ :
          return result

        if len(result) == 0:
          return 0.0

        total_result = 0.0
        for result_line in result:
          if result_line.total_price is not None:
            total_result += result_line.total_price

        return total_result

      if valuation_method not in ('Fifo', 'Filo', 'WeightedAverage',
        'MonthlyWeightedAverage', 'MovingAverage'):
        raise ValueError("Invalid valuation method: %s" % valuation_method)

      assert 'node_uid' in kw or 'section_uid' in kw
      sql_kw = self._generateSQLKeywordDict(**kw)

      if 'section_uid' in kw and 'node_uid' not in kw:
        # ignore internal movements if ignore node
        sql_kw['where_expression'] += ' AND ' \
          'NOT(stock.section_uid<=>stock.mirror_section_uid)'

      result = self.Resource_zGetAssetPrice(
          valuation_method=valuation_method,
          src__=src__,
          **sql_kw)

      if src__ :
        return result

      if len(result) > 0:
        return result[-1].total_asset_price

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryAssetPrice')
    def getCurrentInventoryAssetPrice(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventoryAssetPrice(simulation_period='Current',**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryAssetPrice')
    def getAvailableInventoryAssetPrice(self, **kw):
      """
      Returns list of available inventory grouped by section or site
      (current inventory - deliverable)
      """
      portal = self.getPortalObject()
      kw['simulation_state'] = portal.getPortalReservedInventoryStateList() + \
                               portal.getPortalCurrentInventoryStateList()
      return self.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryAssetPrice')
    def getFutureInventoryAssetPrice(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['simulation_state'] = portal.getPortalFutureInventoryStateList() + \
                               portal.getPortalReservedInventoryStateList() + \
                               portal.getPortalCurrentInventoryStateList()
      return self.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryList')
    def getInventoryHistoryList(self, src__=0, ignore_variation=0,
                                standardise=0, omit_simulation=0,
                                only_accountable=True, omit_input=0,
                                omit_output=0, precision=None, **kw):
      """
      Returns a time based serie of inventory values
      for a single or a group of resource, node, section, etc. This is useful
      to list the evolution with time of inventory values (quantity, asset price).

      TODO:
        - make sure getInventoryHistoryList can return
          cumulative values calculated by SQL (JPS)
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      return self.Resource_getInventoryHistoryList(
                      src__=src__, ignore_variation=ignore_variation,
                      standardise=standardise, omit_simulation=omit_simulation,
                      only_accountable=only_accountable,
                      omit_input=omit_input, omit_output=omit_output,
                      precision=precision,
                      **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, src__=0, ignore_variation=0,
                                 standardise=0, omit_simulation=0,
                                 only_accountable=True,
                                 omit_input=0, omit_output=0,
                                 precision=None, **kw):
      """
      getInventoryHistoryChart is the pensing to getInventoryHistoryList
      to ease the rendering of time based graphs which show the evolution
      of one ore more inventories. Each item in the serie consists of
      time, value and "colour" (multiple graphs can be drawn for example
      for each variation of a resource)
      """
      sql_kw = self._generateSQLKeywordDict(**kw)

      return self.Resource_getInventoryHistoryChart(
                    src__=src__, ignore_variation=ignore_variation,
                    standardise=standardise, omit_simulation=omit_simulation,
                    only_accountable=only_accountable,
                    omit_input=omit_input, omit_output=omit_output,
                    precision=precision,
                    **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryList')
    def getMovementHistoryList(self, src__=0, ignore_variation=0,
                               standardise=0, omit_simulation=0,
                               omit_input=0, omit_output=0,
                               only_accountable=True,
                               omit_asset_increase=0, omit_asset_decrease=0,
                               initial_running_total_quantity=0,
                               initial_running_total_price=0, precision=None,
                               **kw):
      """Returns a list of movements which modify the inventory
      for a single or a group of resource, node, section, etc.
      A running total quantity and a running total price are available on
      brains. The initial values can be passed, in case you want to have an
      "initial summary line".
      """
      # Extend select_dict by order_by_list columns.
      catalog = self.getPortalObject().portal_catalog.getSQLCatalog()
      kw = catalog.getCannonicalArgumentDict(kw)
      extra_column_set = {i[0] for i in kw.get('order_by_list', ())}
      kw.setdefault('select_dict', {}).update(
        (x.replace('.', '_') + '__ext__', x)
        for x in extra_column_set if not x.endswith('__score__'))

      sql_kw = self._generateSQLKeywordDict(**kw)

      return self.Resource_zGetMovementHistoryList(
                         src__=src__, ignore_variation=ignore_variation,
                         standardise=standardise,
                         omit_simulation=omit_simulation,
                         only_accountable=only_accountable,
                         omit_input=omit_input, omit_output=omit_output,
                         omit_asset_increase=omit_asset_increase,
                         omit_asset_decrease=omit_asset_decrease,
                         initial_running_total_quantity=
                                  initial_running_total_quantity,
                         initial_running_total_price=
                                  initial_running_total_price,
                         precision=precision, **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryStat')
    def getMovementHistoryStat(self, src__=0, **kw):
      """
      getMovementHistoryStat is the pending to getMovementHistoryList
      for ListBox stat

      supported parameters are similar to ones accepted by getInventoryList
      with the exception of group_by_*
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      inventory_list = self.getInventoryList(ignore_group_by=1, **kw)
      assert len(inventory_list) == 1
      return inventory_list[0]

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getNextAlertInventoryDate')
    def getNextAlertInventoryDate(self, reference_quantity=0, src__=0,
                       simulation_period='Future', from_date=None,
                       range='min',
                       initial_inventory_kw=None,
                       inventory_list_kw=None,
                       **kw):
      """
      Give the next date where the quantity is lower than the
      reference quantity. This is calculated by first looking if inventory
      right now is good or not. If not, then look at inventory list until
      a movement makes the inventory like expected.

      range  - either 'min' (default) or 'nlt'. With 'nlt', returns
               the next date where inventory is above reference_quantity

      initial_inventory_kw - additional parameters for the initial inventory

      inventory_list_kw - additional parameters for looking at next movements
                          (exemple: use omit_output)
      """
      result = None
      # First look at current inventory, we might have already an inventory
      # lower than reference_quantity
      def getCheckQuantityMethod():
        if range == 'min':
          return lambda x: x < reference_quantity
        elif range == 'nlt':
          return lambda x: x >= reference_quantity
        else:
          raise ValueError("Uknown range type : %s" % (range,))

      checkQuantity = getCheckQuantityMethod()
      if from_date is None:
        from_date = DateTime()
      def getAugmentedInventoryKeyword(additional_kw):
        inventory_kw = kw
        if additional_kw:
          inventory_kw = kw.copy()
          inventory_kw.update(additional_kw)
        return inventory_kw
      inventory_method = getattr(self, "get%sInventory" % simulation_period)
      initial_inventory = inventory_method(at_date=from_date,
                           **getAugmentedInventoryKeyword(initial_inventory_kw))
      if checkQuantity(initial_inventory):
        result = from_date
      else:
        inventory_list_method = getattr(self,
          "get%sInventoryList" % simulation_period)
        inventory_list = inventory_list_method(src__=src__, from_date=from_date,
            sort_on = (('date', 'ascending'),), group_by_movement=1,
            **getAugmentedInventoryKeyword(inventory_list_kw))
        if src__ :
          return inventory_list
        total_inventory = initial_inventory
        for inventory in inventory_list:
          if inventory['inventory'] is not None:
            total_inventory += inventory['inventory']
            if checkQuantity(total_inventory):
              result = inventory['date']
              break
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, **kw):
      """
      Deficient Inventory with a reference_quantity of 0, so when the
      stock will be negative
      """
      return self.getNextAlertInventoryDate(reference_quantity=0, **kw)

    #######################################################
    # Traceability management
    security.declareProtected(Permissions.AccessContentsInformation, 'getTrackingList')
    def getTrackingList(self, src__=0,
        strict_simulation_state=1, history=0, **kw) :
      """
      Returns a list of items in the form

        uid (of item)
        date
        node_uid
        section_uid
        resource_uid
        variation_text
        delivery_uid

      If at_date is provided, returns the a list which answers
      to the question "where are those items at this date" or
      "which are those items which are there a this date"

      If at_date is not provided, returns a history of positions
      which answers the question "where have those items been
      between this time and this time". This will be handled by
      something like getTrackingHistoryList

      This method is only suitable for singleton items (an item which can
      only be at a single place at a given time). Such items include
      containers, serial numbers (ex. for engine), rolls with subrolls,

      This method is not suitable for batches (ex. a coloring batch).
      For such items, standard getInventoryList method is appropriate

      Parameters are the same as for getInventory.

      Default sort orders is based on dates, reverse.


      from_date (>=) -

      to_date   (<)  -

      at_date   (<=) - only take rows which date is <= at_date

      history (boolean) - keep history variations

      resource (only in generic API in simulation)

      node        -  only take rows in stock table which node_uid is equivalent to node

      section        -  only take rows in stock table which section_uid is equivalent to section

      resource_category        -  only take rows in stock table which resource_uid is in resource_category

      node_category        -  only take rows in stock table which node_uid is in section_category

      section_category        -  only take rows in stock table which section_uid is in section_category

      variation_text - only take rows in stock table with specified variation_text
                       XXX this way of implementing variation selection is far from perfect

      variation_category - variation or list of possible variations
                           Deprecated, use variation_text

      simulation_state - only take rows with specified simulation_state

      selection_domain, selection_report - see ListBox

      **kw  - if we want extended selection with more keywords (but bad performance)
              check what we can do with buildSQLQuery

      Extra parameters for getTrackingList :

      item

      input - if set, answers to the question "which are those items which have been
              delivered for the first time after from_date". Cannot be used with output

      output - if set, answers to the question "which are those items which have been
               delivered for the last time before at_date or to_date". Cannot be used with input

      """
      next_item_simulation_state = kw.pop('next_item_simulation_state', None)
      new_kw = self._generateSQLKeywordDict(table='item',strict_simulation_state=strict_simulation_state,**kw)
      for key in ('at_date', 'to_date'):
        value = kw.get(key, None)
        if value is not None:
          if isinstance(value, DateTime):
            value = value.toZone('UTC').ISO()
          value = '%s' % (value, )
        # Do not remove dates in new_kw, they are required in
        # order to do a "select item left join item on date"
        new_kw[key] = value

      # Extra parameters for the SQL Method
      new_kw['join_on_item'] = not history and (new_kw.get('at_date') or \
                               new_kw.get('to_date') or \
                               new_kw.get('input') or \
                               new_kw.get('output'))
      new_kw['date_condition_in_join'] = not (new_kw.get('input') or new_kw.get('output'))

      # Pass simulation state to request
      if next_item_simulation_state:
        new_kw['simulation_state_list'] = next_item_simulation_state
      elif kw.has_key('item.simulation_state'):
        new_kw['simulation_state_list'] = kw['item.simulation_state']
      else:
        new_kw['simulation_state_list'] =  None

      return self.Resource_zGetTrackingList(src__=src__,
                                            **new_kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentTrackingList')
    def getCurrentTrackingList(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['item.simulation_state'] = portal\
        .getPortalCurrentInventoryStateList()
      kw['next_item_simulation_state'] = portal\
        .getPortalCurrentInventoryStateList() + portal\
        .getPortalTransitInventoryStateList()
      return self.getTrackingList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentTrackingHistoryList')
    def getCurrentTrackingHistoryList(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['item.simulation_state'] = self.getPortalObject()\
        .getPortalCurrentInventoryStateList()
      return self.getTrackingHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getTrackingHistoryList')
    def getTrackingHistoryList(self, **kw):
      """
      Returns history list of inventory grouped by section or site
      """
      kw['history'] = 1
      return self.getTrackingList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureTrackingList')
    def getFutureTrackingList(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      portal = self.getPortalObject()
      kw['item.simulation_state'] = portal.getPortalFutureInventoryStateList() + \
                                    portal.getPortalTransitInventoryStateList() + \
                                    portal.getPortalReservedInventoryStateList() + \
                                    portal.getPortalCurrentInventoryStateList()
      return self.getTrackingList(**kw)

    #######################################################
    # Capacity Management
    security.declareProtected( Permissions.ModifyPortalContent, 'updateCapacity' )
    def updateCapacity(self, node):
      capacity_item_list = []
      for o in node.contentValues():
        if o.isCapacity():
          # Do whatever is needed
          capacity_item_list += o.asCapacityItemList()
          pass
      # Do whatever with capacity_item_list
      # and store the resulting new capacity in node
      node._capacity_item_list = capacity_item_list

    security.declareProtected( Permissions.ModifyPortalContent, 'isMovementInsideCapacity' )
    def isMovementInsideCapacity(self, movement):
      """
        Purpose: provide answer to customer for the question "can you do it ?"

        movement:
          date
          source destination (2 nodes)
          source_section ...
      """
      # Get nodes and dat
      source_node = movement.getSourceValue()
      destination_node = movement.getDestinationValue()
      start_date = movement.getStartDate()
      stop_date = movement.getStopDate()
      # Return result
      return self.isNodeInsideCapacity(source_node, start_date, additional_movement=movement, sign=1) and self.isNodeInsideCapacity(destination_node, stop_date, additional_movement=movement, sign=-1)

    security.declareProtected( Permissions.ModifyPortalContent, 'isNodeInsideCapacity' )
    def isNodeInsideCapacity(self, node, date, simulation_state=None, additional_movement=None, sign=1):
      """
        Purpose: decide if a node is consistent with its capacity definitions
        at a certain date (ie. considreing the stock / production history
      """
      # First get the current inventory situation for this node
      inventory_list = node.getInventoryList(XXXXX)
      # Add additional movement
      if additional_movement:
          inventory_list = inventory_list + sign * additional_movement # needs to be implemented
      # Return answer
      return self.isAmountListInsideCapacity(node, inventory_list)

    security.declareProtected( Permissions.ModifyPortalContent, 'isAmountListInsideCapacity' )
    def isAmountListInsideCapacity(self, node, amount_list,
         resource_aggregation_base_category=None, resource_aggregation_depth=None):
      """
        Purpose: decide if a list of amounts is consistent with the capacity of a node

        If any resource in amount_list is missing in the capacity of the node, resource
        aggregation is performed, based on resource_aggregation_base_category. If the
        base category is not specified, it is an error (should guess instead?). The resource
        aggregation is done at the level of resource_aggregation_depth in the tree
        of categories. If resource_aggregation_depth is not specified, it's an error.

        Assumptions: amount_list is an association list, like ((R1 V1) (R2 V2)).
                     node has an attribute '_capacity_item_list' which is a list of association lists.
                     resource_aggregation_base_category is a Base Category object or a list of Base
                     Category objects or None.
                     resource_aggregation_depth is a strictly positive integer or None.
      """
      # Make a copy of the attribute _capacity_item_list, because it may be necessary
      # to modify it for resource aggregation.
      capacity_item_list = node._capacity_item_list[:]

      # Make a mapping between resources and its indices.
      resource_map = {}
      index = 0
      for alist in capacity_item_list:
        for pair in alist:
          resource = pair[0]
#          LOG('isAmountListInsideCapacity', 0,
#              "resource is %s" % repr(resource))
          if resource not in resource_map:
            resource_map[resource] = index
            index += 1

      # Build a point from the amount list.
      point = zeros(index, 'd') # Fill up zeros for safety.
      mask_map = {}     # This is used to skip items in amount_list.
      for amount in amount_list:
        if amount[0] in mask_map:
          continue
        # This will fail, if amount_list has any different resource from the capacity.
        # If it has any different point, then we should ......
        #
        # There would be two possible different solutions:
        # 1) If a missing resource is a meta-resource of resources supported by the capacity,
        #    it is possible to add the resource into the capacity by aggregation.
        # 2) If a missing resource has a meta-resource as a parent and the capacity supports
        #    the meta-resource directly or indirectly (`indirectly' means `by aggregation'),
        #    it is possible to convert the missing resource into the meta-resource.
        #
        # However, another way has been implemented here. This does the following, if the resource
        # is not present in the capacity:
        # 1) If the value is zero, just ignore the resource, because zero is always acceptable.
        # 2) Attempt to aggregate resources both of the capacity and of the amount list. This aggregation
        #    is performed at the depth of 'resource_aggregation_depth' under the base category
        #    'resource_aggregation_base_category'.
        #
        resource = amount[0]
        if resource in resource_map:
          point[resource_map[amount[0]]] = amount[1]
        else:
          if amount[1] == 0:
            # If the value is zero, no need to consider.
            pass
          elif resource_aggregation_base_category is None or resource_aggregation_depth is None:
            # XXX use an appropriate error class
            # XXX should guess a base category instead of emitting an exception
            raise RuntimeError, "The resource '%s' is not found in the capacity, and the argument 'resource_aggregation_base_category' or the argument 'resource_aggregation_depth' is not specified" % resource
          else:
            # It is necessary to aggregate resources, to guess the capacity of this resource.

            def getAggregationResourceUrl(url, depth):
              # Return a partial url of the argument 'url'.
              # If 'url' is '/foo/bar/baz' and 'depth' is 2, return '/foo/bar'.
              pos = 0
              for i in range(resource_aggregation_depth):
                pos = url.find('/', pos+1)
                if pos < 0:
                  break
              if pos < 0:
                return None
              pos = url.find('/', pos+1)
              if pos < 0:
                pos = len(url)
              return url[:pos]

            def getAggregatedResourceList(aggregation_url, category, resource_list):
              # Return a list of resources which should be aggregated. 'aggregation_url' is used
              # for a top url of those resources. 'category' is a base category for the aggregation.
              aggregated_resource_list = []
              for resource in resource_list:
                for url in resource.getCategoryMembershipList(category, base=1):
                  if url.startswith(aggregation_url):
                    aggregated_resource_list.append(resource)
              return aggregated_resource_list

            def getAggregatedItemList(item_list, resource_list, aggregation_resource):
              # Return a list of association lists, which is a result of an aggregation.
              # 'resource_list' is a list of resources which should be aggregated.
              # 'aggregation_resource' is a category object which is a new resource created by
              # this aggregation.
              # 'item_list' is a list of association lists.
              new_item_list = []
              for alist in item_list:
                new_val = 0
                new_alist = []
                # If a resource is not a aggregated, then add it to the new alist as it is.
                # Otherwise, aggregate it to a single value.
                for pair in alist:
                  if pair[0] in resource_list:
                    new_val += pair[1]
                  else:
                    new_alist.append(pair)
                # If it is zero, ignore this alist, as it is nonsense.
                if new_val != 0:
                  new_alist.append([aggregation_resource, new_val])
                  new_item_list.append(new_alist)
              return new_item_list

            # Convert this to a string if necessary, for convenience.
            if not isinstance(resource_aggregation_base_category, (tuple, list)):
              resource_aggregation_base_category = (resource_aggregation_base_category,)

            done = 0
#            LOG('isAmountListInsideCapacity', 0,
#                "resource_aggregation_base_category is %s" % repr(resource_aggregation_base_category))
            for category in resource_aggregation_base_category:
              for resource_url in resource.getCategoryMembershipList(category, base=1):
                aggregation_url = getAggregationResourceUrl(resource_url,
                                                            resource_aggregation_depth)
                if aggregation_url is None:
                  continue
                aggregated_resource_list = getAggregatedResourceList (aggregation_url,
                                                                      category,
                                                                      resource_map.keys())
                # If any, do the aggregation.
                if len(aggregated_resource_list) > 0:
                  aggregation_resource = self.portal_categories.resolveCategory(aggregation_url)
                  # Add the resource to the mapping.
 #                 LOG('aggregation_resource', 0, str(aggregation_resource))
                  resource_map[aggregation_resource] = index
                  index += 1
                  # Add the resource to the point.
                  point = resize(point, (index,))
                  val = 0
                  for aggregated_amount in amount_list:
                    for url in aggregated_amount[0].getCategoryMembershipList(category, base=1):
                      if url.startswith(aggregation_url):
                        val += aggregated_amount[1]
                        mask_map[aggregated_amount[0]] = None
                        break
                  point[index-1] = val
                  # Add capacity definitions of the resource into the capacity.
                  capacity_item_list += getAggregatedItemList(capacity_item_list,
                                                              aggregated_resource_list,
                                                              aggregation_resource)
                  done = 1
                  break
              if done:
                break
            if not done:
              raise RuntimeError, "Aggregation failed"

      # Build a matrix from the capacity item list.
#      LOG('resource_map', 0, str(resource_map))
      matrix = zeros((len(capacity_item_list)+1, index), 'd')
      for index in range(len(capacity_item_list)):
        for pair in capacity_item_list[index]:
          matrix[index,resource_map[pair[0]]] = pair[1]

#      LOG('isAmountListInsideCapacity', 0,
#          "matrix = %s, point = %s, capacity_item_list = %s" % (str(matrix), str(point), str(capacity_item_list)))
      return solve(matrix, point)


    # Asset Price Calculation
    def updateAssetPrice(self, resource, variation_text, section_category, node_category,
                         strict_membership=0, simulation_state=None):
      if simulation_state is None:
        simulation_state = self.getPortalCurrentInventoryStateList()
      category_tool = getToolByName(self, 'portal_categories')
      section_value = category_tool.resolveCategory(section_category)
      node_value = category_tool.resolveCategory(node_category)
      # Initialize price
      current_asset_price = 0.0 # Missing: initial inventory price !!!
      current_inventory = 0.0
      # Parse each movement
      brain_list = self.Resource_zGetMovementHistoryList(resource=[resource],
                             variation_text=variation_text,
                             section_category=section_category,
                             node_category=node_category,
                             strict_membership=strict_membership,
                             simulation_state=simulation_state) # strict_membership not taken into account
                             # We select movements related to certain nodes (ex. Stock) and sections (ex.Coramy Group)
      result = []
      for b in brain_list:
        m = b.getObject()
        if m is not None:
          previous_inventory = current_inventory
          inventory_quantity = b.quantity # We should use the aggregated quantity provided by Resource_zGetMovementHistoryList
          quantity = m.getQuantity() # The movement quantity is important to determine the meaning of source and destination
          # Maybe we should take care of target qty in delired deliveries
          if quantity is None:
            quantity = 0.0
          if m.getSourceValue() is None:
            # This is a production movement or an inventory movement
            # Use Industrial Price
            current_inventory += inventory_quantity # Update inventory
            if m.getPortalType() in ('Inventory Line', 'Inventory Cell'): # XX should be replaced by isInventory ???
              asset_price = m.getPrice()
              if asset_price in (0.0, None):
                asset_price = current_asset_price # Use current price if no price defined
            else: # this is a production
              asset_price = m.getIndustrialPrice()
              if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
            result.append((m.getRelativeUrl(), m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getQuantity(), 'Production or Inventory', 'Price: %s' % asset_price
                        ))
          elif m.getDestinationValue() is None:
            # This is a consumption movement or an inventory movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getQuantity(), 'Consumption or Inventory', 'Price: %s' % asset_price
                        ))
          elif m.getSourceValue().isAcquiredMemberOf(node_category) and m.getDestinationValue().isAcquiredMemberOf(node_category):
            # This is an internal movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getQuantity(), 'Internal', 'Price: %s' % asset_price
                        ))
          elif m.getSourceValue().isAcquiredMemberOf(node_category) and quantity < 0:
            # This is a physically inbound movement - try to use commercial price
            if m.getSourceSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue().isAcquiredMemberOf(section_category):
              current_inventory += inventory_quantity # Update inventory
              if m.getDestinationValue().isAcquiredMemberOf('site/Piquage'):
                # Production
                asset_price = m.getIndustrialPrice()
                if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getQuantity(), 'Production', 'Price: %s' % asset_price
                            ))
              else:
                # Inbound from same section
                asset_price = current_asset_price
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                            ))
            else:
              current_inventory += inventory_quantity # Update inventory
              asset_price = m.getPrice()
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                          ))
          elif m.getDestinationValue().isAcquiredMemberOf(node_category) and quantity > 0:
            # This is a physically inbound movement - try to use commercial price
            if m.getSourceSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getSourceSectionValue().isAcquiredMemberOf(section_category):
              current_inventory += inventory_quantity # Update inventory
              if m.getSourceValue().isAcquiredMemberOf('site/Piquage'):
                # Production
                asset_price = m.getIndustrialPrice()
                if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getQuantity(), 'Production', 'Price: %s' % asset_price
                            ))
              else:
                # Inbound from same section
                asset_price = current_asset_price
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                          ))
            else:
              current_inventory += inventory_quantity # Update inventory
              asset_price = m.getPrice()
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                          ))
          else:
            # Outbound movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getQuantity(), 'Outbound', 'Price: %s' % asset_price
                          ))

          # Update asset_price
          if current_inventory > 0:
            if inventory_quantity is not None:
              # Update price with an average of incoming goods and current goods
              current_asset_price = ( current_asset_price * previous_inventory + asset_price * inventory_quantity ) / float(current_inventory)
          else:
            # New price is the price of incoming goods - negative stock has no meaning for asset calculation
            current_asset_price = asset_price

          result.append(('###New Asset Price', current_asset_price, 'New Inventory', current_inventory))

          # Update Asset Price on the right side
          if m.getSourceSectionValue() is not None and m.getSourceSectionValue().isAcquiredMemberOf(section_category):
            # for each movement, source section is member of one and one only accounting category
            # therefore there is only one and one only source asset price
            m._setSourceAssetPrice(current_asset_price)
            #quantity = m.getInventoriatedQuantity()
            #if quantity:
            #  #total_asset_price = - current_asset_price * quantity
            #  #m.Movement_zSetSourceTotalAssetPrice(uid=m.getUid(), total_asset_price = total_asset_price)
            #  m._setSourceAssetPrice(current_asset_price)
          if m.getDestinationSectionValue() is not None and m.getDestinationSectionValue().isMemberOf(section_category):
            # for each movement, destination section is member of one and one only accounting category
            # therefore there is only one and one only destination asset price
            m._setDestinationAssetPrice(current_asset_price)
            #quantity = m.getInventoriatedQuantity()
            #if quantity:
            #  total_asset_price = current_asset_price * quantity
            #  m.Movement_zSetDestinationTotalAssetPrice(uid=m.getUid(), total_asset_price = total_asset_price)
          # Global reindexing required afterwards in any case: so let us do it now
          # Until we get faster methods (->reindexObject())
          m.reindexObject()

      return result

    def _findBuilderForDelivery(self, delivery, movement_portal_type):
      """
      Find out the builder corresponding to a delivery by looking at the business process
      """
      builder = None
      portal_type = delivery.getPortalType()
      for business_link in delivery.asComposedDocument().objectValues(portal_type="Business Link"):
        for business_link_builder in business_link.getDeliveryBuilderValueList():
          if business_link_builder.getDeliveryPortalType() == portal_type \
          and business_link_builder.getDeliveryLinePortalType() == movement_portal_type:
            builder = business_link_builder
            break
        if builder is not None:
          break
      return builder

    security.declareProtected( Permissions.ModifyPortalContent, 'mergeDeliveryList' )
    def mergeDeliveryList(self, delivery_list):
      """
        Merge multiple deliveries into one delivery.
        All delivery lines are merged into the first one.
        The first one is therefore called main_delivery here.
        The others are cancelled.
      """
      # Sanity checks.
      if not(len(delivery_list) >=2):
        raise ValueError("Please select at least 2 deliveries")
      portal= self.getPortalObject()
      translateString = portal.Base_translateString
      error_list = []
      if len(delivery_list) > 1:
        portal_type_set = set([x.getPortalType() for x in delivery_list])
        if len(portal_type_set) != 1:
          error_list.append(translateString("Please select only deliveries of same type"))
        else:
          allowed_state_set = set(portal.getPortalReservedInventoryStateList() + \
                                 portal.getPortalFutureInventoryStateList())
          found_state_set = set([x.getSimulationState() for x in delivery_list])
          if found_state_set.difference(allowed_state_set):
            error_list.append(translateString("Found delivery having unexpected status for merge"))
          else:
            movement_portal_type_set = set()
            for delivery in delivery_list:
              movement_portal_type_set.update([x.getPortalType() for x in delivery.getMovementList()])
            if len(movement_portal_type_set) != 1:
              error_list.append(translateString("Please Select only movement of same type"))
            else:
              # Allow to call a script to do custom checking conditions before merge
              main_delivery = delivery_list[0]
              check_merge_condition_method = main_delivery._getTypeBasedMethod("checkMergeConditionOnDeliveryList")
              if check_merge_condition_method is not None:
                error_list.extend(check_merge_condition_method(delivery_list=delivery_list))
              if len(error_list) == 0:
                # so far so good
                # in delivery_list we have list of delivery to merge
                simulation_movement_list = []
                to_copy_delivery_line_list = [] # for lines not coming from upper simulation, thus
                                                # created by hand should be manually added to main
                                                # delivery since they are not coming from builder
                for delivery in delivery_list:
                  line_id_to_delete_list = []
                  for movement in delivery.getMovementList():
                    related_simulation_movement_list = movement.getDeliveryRelatedValueList()
                    for simulation_movement in related_simulation_movement_list:
                      # if we are on a root applied rule directly, so in the case of
                      # a manually added line, we have to copy
                      # the simulation movement into to main delivery
                      if simulation_movement.getParentValue().getParentValue().getId() == "portal_simulation":
                        # For manually added lines, make sure we have only one simulation movement
                        assert len(related_simulation_movement_list) == 1
                        if not(delivery is main_delivery):
                          to_copy_delivery_line_list.append(movement)
                      else:
                        simulation_movement.setDeliveryValue(None)
                        simulation_movement_list.append(simulation_movement)
                        # Since we keep the main delivery, we remove existing lines already
                        # coming from builder to let builder recreate them in the same time
                        # as other ones (to possibly merge lines also)
                        movement_id = movement.getId()
                        if delivery is main_delivery and not(movement_id in line_id_to_delete_list):
                          line_id_to_delete_list.append(movement.getId())
                  if line_id_to_delete_list:
                    delivery.manage_delObjects(ids=line_id_to_delete_list)
                # It is required to expand again simulation movement, because
                # we unlinked them from delivery, so it is possible that some
                # properties will change on simulation movement (mostly categories).
                # By expanding again, we will avoid having many deliveries instead
                # of one when doing "merge"
                for simulation_movement in simulation_movement_list:
                  simulation_movement.expand(expand_policy='immediate')

                # activate builder
                movement_portal_type, = movement_portal_type_set
                merged_builder = self._findBuilderForDelivery(main_delivery, movement_portal_type)
                if merged_builder is None:
                  error_list.append(translateString("Unable to find builder"))
                else:
                  merged_builder.build(movement_relative_url_list=[q.getRelativeUrl() for q in \
                                       simulation_movement_list], merge_delivery=True,
                                       delivery_relative_url_list=[main_delivery.getRelativeUrl()])
                # Finally, copy all lines that were created manually on all deliveries except
                # the main one
                @UnrestrictedMethod
                def setMainDeliveryModifiable(delivery):
                  # set causality state in such way we can modify delivery
                  delivery.diverge()
                setMainDeliveryModifiable(main_delivery)
                delivery_type_list = portal.getPortalDeliveryTypeList()
                for delivery_line in to_copy_delivery_line_list:
                  delivery = delivery_line.getParentValue()
                  if not(delivery.getPortalType() in delivery_type_list):
                    raise NotImplementedError("Merge of deliveries doe not yet handle case of cells")
                  copy_data = delivery.manage_copyObjects(ids=[delivery_line.getId()])
                  main_delivery.manage_pasteObjects(copy_data)
                main_delivery.updateCausalityState()

                # Finally do cleanup
                for delivery in delivery_list[1:]:
                  # cancel, delete - to disallow any user related operations on those deliveries
                  after_merge_method = delivery._getTypeBasedMethod('cleanDeliveryAfterMerge')
                  if after_merge_method is not None:
                    after_merge_method()
      else:
        error_list.append(translateString("Please select at least two deliveries"))
      return error_list

    #######################################################
    # Sequence
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getSequence')
    def getSequence(self, **kw):
      """
      getSequence is take the same parameters as Sequence constructor,
      and return a Sequence.
      """
      return Sequence(**kw)

    #######################################################
    # Time Management
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableTime')
    def getAvailableTime(self, from_date=None, to_date=None,
                         portal_type=[], node=[],
                         resource=[], src__=0, **kw):
      """
      Calculate available time for a node
      Returns an inventory of a single or multiple resources on a single
      node as a single float value

      from_date (>=) - only take rows which mirror_date is >= from_date

      to_date   (<)  - only take rows which date is < to_date

      node           - only take rows in stock table which node_uid is
                       equivalent to node

      resource       - only take rows in stock table which resource_uid is
                       equivalent to resource

      portal_type    - only take rows in stock table which portal_type
                       is in portal_type parameter
      """
      # XXX For now, consider that from_date and to_date are required
      if (from_date is None) or (to_date is None):
        raise NotImplementedError, \
              "getAvailableTime does not managed yet None values"
      portal = self.getPortalObject()
      # Calculate portal_type
      if portal_type == []:
        portal_type = portal.getPortalCalendarPeriodTypeList()

      simulation_state = portal.getPortalCurrentInventoryStateList() + \
                         portal.getPortalTransitInventoryStateList() + \
                         portal.getPortalReservedInventoryStateList()

      sql_result = portal.Node_zGetAvailableTime(
                          from_date=from_date,
                          to_date=to_date,
                          portal_type=portal_type,
                          node=node,
                          resource=resource,
                          simulation_state=simulation_state,
                          src__=src__, **kw)
      if not src__:
        result = 0
        if len(sql_result) == 1:
          result = sql_result[0].total_quantity
      else:
        result = sql_result
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableTimeSequence')
    def getAvailableTimeSequence(self, from_date, to_date,
                                 portal_type=[], node=[],
                                 resource=[],
                                 src__=0,
                                 **kw):
      """
      Calculate available time for a node in multiple period of time.
      Each row is the available time for a specific period

      node           - only take rows in stock table which node_uid is
                       equivalent to node

      portal_type    - only take rows in stock table which portal_type
                       is in portal_type parameter

      resource       - only take rows in stock table which resource_uid is
                       equivalent to resource

      from_date (>=) - return period which start >= from_date

      to_date   (<)  - return period which start < to_date

      second, minute,
      hour, day,
      month, year   - duration of each time period (cumulative)
      """
      portal = self.getPortalObject()
      # Calculate portal_type
      if portal_type == []:
        portal_type = portal.getPortalCalendarPeriodTypeList()

      sequence = Sequence(from_date, to_date, **kw)
      for sequence_item in sequence:
        setattr(sequence_item, 'total_quantity',
                self.getAvailableTime(
                          from_date=sequence_item.from_date,
                          to_date=sequence_item.to_date,
                          portal_type=portal_type,
                          node=node,
                          resource=resource,
                          src__=src__))
      return sequence

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableTimeMovementList')
    def getAvailableTimeMovementList(self, from_date, to_date,
                                 **kw):
      """
      Calculate available time movement list by taking into account
      both available time and not available time.

      Necessary parameter is at least node.

      Parameters supported by getMovementHistoryList are supported here.

      from_date (>=) - return period which start >= from_date

      to_date   (<)  - return period which start < to_date
      """
      portal = self.getPortalObject()
      if kw.get("simulation_state", None) is None:
        kw["simulation_state"] = portal.getPortalCurrentInventoryStateList() + \
                         portal.getPortalTransitInventoryStateList() + \
                         portal.getPortalReservedInventoryStateList()
      movement_list = self.getMovementHistoryList(from_date=from_date,
                                 to_date=to_date, group_by_movement=1,
                                 group_by_date=1, **kw)
      # do import on top, but better to avoid breaking instances with older softwares
      from interval import IntervalSet, Interval
      # we look at all movements, and we build a set of intervals for available
      # time, another for not available time, and we do substraction of both sets
      assignment_interval_set = IntervalSet()
      leave_interval_set = IntervalSet()
      result_list = []

      def getOrderedMovementDates(movement):
        date_list = [movement.date, movement.mirror_date]
        date_list.sort()
        return date_list

      movement_availability_dict = {} # to later map availability intervals with their movements
      for movement in movement_list:
        start_date, stop_date = getOrderedMovementDates(movement)
        current_interval = Interval(start_date, stop_date)
        # case of available time
        if movement.total_quantity > 0:
          assignment_interval_set.add(current_interval)
          movement_availability_dict[current_interval] = movement
        # case of not available time
        else:
          leave_interval_set.add(current_interval)
      i = 0
      # Parse all calculated availability_interval to find matching movements to
      # be returned in the result. IntervalSet are already ordered
      for availability_interval in (assignment_interval_set - leave_interval_set):
        while True:
          assignment_interval = assignment_interval_set[i]
          if availability_interval in assignment_interval:
            result_list.append(movement_availability_dict[assignment_interval].asContext(
              start_date=availability_interval.lower_bound,
              stop_date=availability_interval.upper_bound))
            break
          else:
            i += 1
      return result_list

    def _checkExpandAll(self, activate_kw={}):
      """Check all simulation trees using AppliedRule._checkExpand
      """
      portal = self.getPortalObject()
      active_process = portal.portal_activities.newActiveProcess().getPath()
      kw = dict(priority=3, tag='checkExpand')
      kw.update(group_method_cost=1, max_retry=0,
                active_process=active_process, **activate_kw)
      self._recurseCallMethod('_checkExpand', min_depth=1, max_depth=1,
                              activate_kw=kw)
      return active_process

from Products.ERP5Type.DateUtils import addToDate

class SequenceItem:
  """
  SequenceItem define a time period.
  period.
  """
  def __init__(self, from_date, to_date):
    self.from_date = from_date
    self.to_date = to_date

class Sequence:
  """
  Sequence is a iterable object, which calculate a range of time
  period.
  """
  def __init__(self, from_date, to_date,
               second=None, minute=None, hour=None,
               day=None, month=None, year=None):
    """
    Calculate a list of time period.
    Time period is a 2-tuple of 2 DateTime, which represent the from date
    and to date of the period.

    The start date of a period is calculated with the rule
        start_date of the previous + period duration

    from_date (>=) - return period which start >= from_date

    to_date   (<)  - return period which start < to_date

    second, minute,
    hour, day,
    month, year   - duration of each time period (cumulative)
                    at least one of those parameters must be specified.
    """
    if not (second or minute or hour or day or month or year):
      raise ValueError('Period duration must be specified')

    self.item_list = []
    # Calculate all time period
    current_from_date = from_date
    while current_from_date < to_date:
      current_to_date = addToDate(current_from_date,
                                  second=second,
                                  minute=minute,
                                  hour=hour,
                                  day=day,
                                  month=month,
                                  year=year)
      self.item_list.append(SequenceItem(current_from_date,
                                         current_to_date))
      current_from_date = current_to_date

  def __len__(self):
    return len(self.item_list)

  def __getitem__(self, key):
    return self.item_list[key]

  def __contains__(self, value):
    return (value in self.item_list)

  def __iter__(self):
    for x in self.item_list:
      yield x

InitializeClass(Sequence)
allow_class(Sequence)
InitializeClass(SequenceItem)
allow_class(SequenceItem)

InitializeClass(SimulationTool)
