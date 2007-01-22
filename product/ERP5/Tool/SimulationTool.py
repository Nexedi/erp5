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
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

from Products.ERP5 import _dtmldir

from zLOG import LOG

from Products.ERP5.Capacity.GLPK import solve
from Numeric import zeros, resize
from DateTime import DateTime

from Products.ERP5 import DeliverySolver
from Products.ERP5 import TargetSolver

class SimulationTool (BaseTool):
    """
    The SimulationTool implements the ERP5
    simulation algorithmics.


    Examples of applications:

    -

    -
    ERP5 main purpose:

    -

    -

    TODO: XXX please use BaseTool
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
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainSimulationTool', _dtmldir )

    # Filter content (ZMI))
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

    def solveDelivery(self, delivery, dsolver_name, tsolver_name,
                                     additional_parameters=None,**kw):
      """
        Solve a delivery by calling DeliverySolver and TargetSolver
      """
      self.solveMovementOrDelivery(delivery, dsolver_name, tsolver_name,
          delivery=1,additional_parameters=additional_parameters,**kw)

    def solveMovement(self, movement, dsolver_name, tsolver_name,
                                       additional_parameters=None,**kw):
      """
        Solve a movement by calling DeliverySolver and TargetSolver
      """
      return self.solveMovementOrDelivery(movement, dsolver_name, tsolver_name,
          movement=1,additional_parameters=additional_parameters,**kw)

    def solveMovementOrDelivery(self, obj, dsolver_name, tsolver_name,
                                          movement=0,delivery=0,
                                          additional_parameters=None,**kw):
      """
        Solve a delivery by calling DeliverySolver and TargetSolver
      """
      for solver_name, solver_module in [(dsolver_name, DeliverySolver),\
                                         (tsolver_name, TargetSolver)]:

        if solver_name is not None:
          solver_file_path = "%s.%s" % (solver_module.__name__,
                                        solver_name)
          __import__(solver_file_path)
          solver_file = getattr(solver_module, solver_name)
          solver_class = getattr(solver_file, solver_name)
          solver = solver_class(additional_parameters=additional_parameters,**kw)

          if movement:
            return solver.solveMovement(obj)
          if delivery:
            return solver.solveDelivery(obj)

    #######################################################
    # Stock Management

    def _generatePropertyUidList(self, property, as_text=0):
      """
      converts relative_url or text (single element or list or dict)
        to an object usable by buildSQLQuery

      as_text == 0: tries to lookup an uid from the relative_url
      as_text == 1: directly passes the argument as text
      """
      if property is None :
        return []
      category_tool = getToolByName(self, 'portal_categories')
      property_uid_list = []
      if type(property) is type('') :
        if not as_text:
          prop_value = category_tool.getCategoryValue(property)
          if prop_value is None:
            raise ValueError, 'Category %s does not exists' % property
          property_uid_list.append(prop_value.getUid())
        else:
          property_uid_list.append(property)
      elif type(property) is type([]) or type(property) is type(()) :
        for property_item in property :
          if not as_text:
            prop_value = category_tool.getCategoryValue(property_item)
            if prop_value is None:
              raise ValueError, 'Category %s does not exists' % property_item
            property_uid_list.append(prop_value.getUid())
          else:
            property_uid_list.append(property_item)
      elif type(property) is type({}) :
        tmp_uid_list = []
        if type(property['query']) is type('') :
          property['query'] = [property['query']]
        for property_item in property['query'] :
          if not as_text:
            prop_value = category_tool.getCategoryValue(property_item)
            if prop_value is None:
              raise ValueError, 'Category %s does not exists' % property_item
            tmp_uid_list.append(prop_value.getUid())
          else:
            tmp_uid_list.append(property_item)
        if tmp_uid_list:
          property_uid_list = {}
          property_uid_list['operator'] = property['operator']
          property_uid_list['query'] = tmp_uid_list
      return property_uid_list

    def _generateSQLKeywordDict(self, table='stock',
        # dates
        from_date=None, to_date=None, at_date=None,
        # instances
        resource=None, node=None, payment=None,
        section=None, mirror_section=None, item=None,
        # used for tracking
        input=0, output=0,
        # categories
        resource_category=None, node_category=None, payment_category=None,
        section_category=None, mirror_section_category=None,
        # categories with strict membership
        resource_category_strict_membership=None,
        node_category_strict_membership=None,
        payment_category_strict_membership=None,
        section_category_strict_membership=None,
        mirror_section_category_strict_membership=None,
        # simulation_state
        strict_simulation_state=0,
        simulation_state=None, transit_simulation_state = None, omit_transit=0,
        input_simulation_state=None, output_simulation_state=None,
        # variations
        variation_text=None, sub_variation_text=None,
        variation_category=None,
        # uids
        resource_uid=None, node_uid=None, section_uid=None,
        # keywords for related keys
        **kw):
      """
      generates keywords and calls buildSQLQuery
      """
      new_kw = {}
      new_kw.update(kw)
      sql_kw = {}

      # input and output are used by getTrackingList
      sql_kw['input'] = input
      sql_kw['output'] = output

      date_dict = {'query':[], 'operator':'and'}
      if from_date :
        date_dict['query'].append(from_date)
        date_dict['range'] = 'min'
        if to_date :
          date_dict['query'].append(to_date)
          date_dict['range'] = 'minmax'
        elif at_date :
          date_dict['query'].append(at_date)
          date_dict['range'] = 'minngt'
      elif to_date :
        date_dict['query'].append(to_date)
        date_dict['range'] = 'max'
      elif at_date :
        date_dict['query'].append(at_date)
        date_dict['range'] = 'ngt'
      if len(date_dict) :
        new_kw[table + '.date'] = date_dict

      # Some columns exists on multiple tables, we have to clear ambiguities
      if resource_uid is not None :
        new_kw[table + '.resource_uid'] = resource_uid
      if section_uid is not None :
        new_kw[table + '.section_uid'] = section_uid
        sql_kw['section_filtered'] = 1
      if node_uid is not None :
        new_kw[table + '.node_uid'] = node_uid

      resource_uid_list = self._generatePropertyUidList(resource)
      if resource_uid_list:
        new_kw[table + '.resource_uid'] = resource_uid_list

      item_uid_list = self._generatePropertyUidList(item)
      if item_uid_list:
        new_kw[table + '.aggregate_uid'] = item_uid_list

      node_uid_list = self._generatePropertyUidList(node)
      if node_uid_list:
        new_kw[table + '.node_uid'] = node_uid_list

      payment_uid_list = self._generatePropertyUidList(payment)
      if payment_uid_list:
        new_kw[table + '.payment_uid'] = payment_uid_list

      section_uid_list = self._generatePropertyUidList(section)
      if section_uid_list:
        new_kw[table + '.section_uid'] = section_uid_list
        sql_kw['section_filtered'] = 1

      mirror_section_uid_list = self._generatePropertyUidList(mirror_section)
      if mirror_section_uid_list:
        new_kw[table + '.mirror_section_uid'] = mirror_section_uid_list

      variation_text_list = self._generatePropertyUidList(variation_text,
                                                          as_text=1)
      if variation_text_list:
        new_kw[table + '.variation_text'] = variation_text_list

      sub_variation_text_list = self._generatePropertyUidList(
                                              sub_variation_text, as_text=1)
      if sub_variation_text_list:
        new_kw[table + '.sub_variation_text'] = sub_variation_text_list

      # category membership
      resource_category_uid_list = self._generatePropertyUidList(
                                              resource_category)
      if resource_category_uid_list:
        new_kw[table + '_resource_category_uid'] = resource_category_uid_list

      node_category_uid_list = self._generatePropertyUidList(node_category)
      if node_category_uid_list:
        new_kw[table + '_node_category_uid'] = node_category_uid_list

      payment_category_uid_list = self._generatePropertyUidList(payment_category)
      if payment_category_uid_list:
        new_kw[table + '_payment_category_uid'] = payment_category_uid_list

      section_category_uid_list = self._generatePropertyUidList(section_category)
      if section_category_uid_list:
        new_kw[table + '_section_category_uid'] = section_category_uid_list
        sql_kw['section_filtered'] = 1

      mirror_section_category_uid_list = self._generatePropertyUidList(
                                              mirror_section_category)
      if mirror_section_category_uid_list:
        new_kw[table + '_mirror_section_category_uid'] =\
                                              mirror_section_category_uid_list

      # category strict membership
      resource_category_strict_membership_uid_list =\
            self._generatePropertyUidList(resource_category_strict_membership)
      if resource_category_strict_membership_uid_list:
        new_kw[table + '_resource_category_strict_membership_uid'] =\
            resource_category_strict_membership_uid_list

      node_category_strict_membership_uid_list =\
            self._generatePropertyUidList(node_category_strict_membership)
      if node_category_strict_membership_uid_list:
        new_kw[table + '_node_category_strict_membership_uid'] =\
            node_category_strict_membership_uid_list

      payment_category_strict_membership_uid_list =\
            self._generatePropertyUidList(payment_category_strict_membership)
      if payment_category_strict_membership_uid_list:
        new_kw[table + '_payment_category_strict_membership_uid'] =\
            payment_category_strict_membership_uid_list

      section_category_strict_membership_uid_list =\
            self._generatePropertyUidList(section_category_strict_membership)
      if section_category_strict_membership_uid_list:
        new_kw[table + '_section_category_strict_membership_uid'] =\
            section_category_strict_membership_uid_list
        sql_kw['section_filtered'] = 1

      mirror_section_category_strict_membership_uid_list =\
            self._generatePropertyUidList(
                                  mirror_section_category_strict_membership)
      if mirror_section_category_strict_membership_uid_list:
        new_kw[table + '_mirror_section_category_strict_membership_uid'] =\
            mirror_section_category_strict_membership_uid_list

      #variation_category_uid_list = self._generatePropertyUidList(variation_category)
      #if len(variation_category_uid_list) :
      #  new_kw['variationCategory'] = variation_category_uid_list
      
      string_or_list = (str, list, tuple)
      # Simulation States
      # If strict_simulation_state is set, we directly put it into the dictionary
      if strict_simulation_state:
        if isinstance(simulation_state, string_or_list)\
                and simulation_state:
          new_kw['simulation_state'] = simulation_state
      else:
        # first, we evaluate simulation_state
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

      # It is necessary to use here another SQL query (or at least a subquery)
      # to get _DISTINCT_ uid from predicate_category table.
      # Otherwise, by using a where_expression, cells which fit conditions
      # more than one time are counted more than one time, and the resulting
      # inventory is false
      # XXX Perhaps is there a better solution
      add_kw = {}
      if variation_category is not None and variation_category:
        where_expression = self.getPortalObject().portal_categories\
          .buildSQLSelector(
            category_list = variation_category,
            query_table = 'predicate_category')
        if where_expression != '':
          add_kw['where_expression'] = where_expression
          add_kw['predicate_category.uid'] = '!=NULL'
          add_kw['group_by_expression'] = 'uid'
          add_query = self.portal_catalog(**add_kw)
          uid_list = []
          for line in add_query:
            uid_list.append(line.uid)
          new_kw['where_expression'] = '( %s )' % ' OR '.join(
                      ['catalog.uid=%s' % uid for uid in uid_list])

      # build the group by expression
      group_by_expression_list = []
      if kw.get('group_by_node', 0):
        group_by_expression_list.append('%s.node_uid' % table)
      if kw.get('group_by_mirror_node', 0):
        group_by_expression_list.append('%s.mirror_node_uid' % table)
      if kw.get('group_by_section', 0):
        group_by_expression_list.append('%s.section_uid' % table)
      if kw.get('group_by_mirror_section', 0):
        group_by_expression_list.append('%s.mirror_section_uid' % table)
      if kw.get('group_by_payment', 0):
        group_by_expression_list.append('%s.payment_uid' % table)
      if kw.get('group_by_sub_variation', 0):
        group_by_expression_list.append('%s.sub_variation_text' % table)
      if kw.get('group_by_variation', 0):
        group_by_expression_list.append('%s.variation_text' % table)
      if group_by_expression_list:
        # by default, we group by resource
        if kw.get('group_by_resource', 1):
          group_by_expression_list.append('%s.resource_uid' % table)
        new_kw['group_by_expression'] = ', '.join(group_by_expression_list)
      
      sql_kw.update(self.portal_catalog.buildSQLQuery(**new_kw))
      return sql_kw

    #######################################################
    # Inventory management
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventory')
    def getInventory(self, src__=0, ignore_variation=0, standardise=0,
                     omit_simulation=0, omit_input=0, omit_output=0,
                     selection_domain=None, selection_report=None,
                     precision=None, **kw):
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
                        This needs to be extended with some kind of
                        variation_category ?
                        XXX this way of implementing variation selection is far
                        from perfect

      sub_variation_text - only take rows in stock table with specified
                        variation_text

      variation_category - variation or list of possible variations (it is not
                        a cross-search ; SQL query uses OR)

      simulation_state - only take rows with specified simulation_state

      transit_simulation_state - specifies which states are transit states

      omit_transit   -  do not evaluate transit_simulation_state

      input_simulation_state - only take rows with specified simulation_state
                        and quantity > 0

      output_simulation_state - only take rows with specified simulation_state
                        and quantity < 0

      ignore_variation -  do not take into account variation in inventory
                        calculation (useless on getInventory, but useful on
                        getInventoryList)

      standardise    -  provide a standard quantity rather than an SKU (XXX
                        not implemented yet)

      omit_simulation - doesn't take into account simulation movements

      omit_input     -  doesn't take into account movement with quantity < 0

      omit_output    -  doesn't take into account movement with quantity > 0

      selection_domain, selection_report - see ListBox

      group_by_variation - (useless on getInventory, but useful on
                        getInventoryList)

      group_by_node  -  (useless on getInventory, but useful on
                        getInventoryList)

      group_by_mirror_node - (useless on getInventory, but useful on
                        getInventoryList)

      group_by_sub_variation - (useless on getInventory, but useful on
                        getInventoryList)

      precision - the precision used to round quantities and prices.

      **kw           -  if we want extended selection with more keywords (but
                        bad performance) check what we can do with
                        buildSQLQuery

      NOTE: we may want to define a parameter so that we can select the kind of
      inventory statistics we want to display (ex. sum, average, cost, etc.)
      """
      sql_kw = self._generateSQLKeywordDict(**kw)

      # JPS: this is a hint for implementation of xxx_filter arguments
      # node_uid_count = portal_catalog.countResults(**node_filter)
      # if node_uid_count not too big:
      #   node_uid_list = cache(portal_catalog(**node_filter))
      #   pass this list to ZSQL method
      # else:
      #   build a table in MySQL
      #   and join that table with the stock table

      result = self.Resource_zGetInventory(
          src__=src__, ignore_variation=ignore_variation,
          standardise=standardise, omit_simulation=omit_simulation,
          omit_input=omit_input, omit_output=omit_output,
          selection_domain=selection_domain, selection_report=selection_report,
          precision=precision, **sql_kw)
      if src__:
        return result

      total_result = 0.0
      if len(result) > 0:
        for result_line in result:
          if result_line.inventory is not None:
            total_result += result_line.inventory

      return total_result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - reserved_inventory)
      """
      current_inventory = self.getCurrentInventory(**kw)
      kw['simulation_state'] = self.getPortalReservedInventoryStateList()
      reserved_inventory = self.getInventory(omit_input=1,**kw)
      return current_inventory+reserved_inventory

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns future inventory
      """
      kw['simulation_state'] = tuple(
                   list(self.getPortalFutureInventoryStateList()) + \
                   list(self.getPortalReservedInventoryStateList()) + \
                   list(self.getPortalCurrentInventoryStateList()))
      return self.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryList')
    def getInventoryList(self, src__=0, ignore_variation=0, standardise=0,
                         omit_simulation=0, omit_input=0, omit_output=0,
                         selection_domain=None, selection_report=None,
                         precision=None, **kw):
      """
        Returns a list of inventories for a single or multiple
        resources on a single or multiple nodes, grouped by resource,
        node, section, etc. Every line defines an inventory value for
        a given group of resource, node, section.
        NOTE: we may want to define a parameter so that we can select
        the kind of inventory statistics we want to display (ex. sum,
        average, cost, etc.)
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      return self.Resource_zGetInventoryList(
                    src__=src__, ignore_variation=ignore_variation,
                    standardise=standardise, omit_simulation=omit_simulation,
                    omit_input=omit_input, omit_output=omit_output,
                    selection_domain=selection_domain,
                    selection_report=selection_report, precision=precision,
                    **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryList')
    def getAvailableInventoryList(self, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
                    list(self.getPortalReservedInventoryStateList()) + \
                    list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
                 list(self.getPortalFutureInventoryStateList()) + \
                 list(self.getPortalReservedInventoryStateList()) + \
                 list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryStat')
    def getInventoryStat(self, src__=0, ignore_variation=0, standardise=0,
                         omit_simulation=0, omit_input=0, omit_output=0,
                         selection_domain=None, selection_report=None,
                         precision=None, **kw):
      """
      getInventoryStat is the pending to getInventoryList in order to
      provide statistics on getInventoryList lines in ListBox such as:
      total of inventories, number of variations, number of different
      nodes, etc.
      """
      kw['group_by_variation'] = 0
      sql_kw = self._generateSQLKeywordDict(**kw)
      result = self.Resource_zGetInventory(
          src__=src__, ignore_variation=ignore_variation,
          standardise=standardise, omit_simulation=omit_simulation,
          omit_input=omit_input, omit_output=omit_output,
          selection_domain=selection_domain,
          selection_report=selection_report,
          precision=precision, **sql_kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryStat')
    def getAvailableInventoryStat(self, **kw):
      """
      Returns statistics of current inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
                    list(self.getPortalReservedInventoryStateList()) + \
                    list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of future inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
                 list(self.getPortalFutureInventoryStateList()) + \
                 list(self.getPortalReservedInventoryStateList()) + \
                 list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryStat(**kw)

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

      return map(lambda r: (r.node_title, r.inventory), result)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
                      list(self.getPortalFutureInventoryStateList()) + \
                      list(self.getPortalReservedInventoryStateList()) + \
                      list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryAssetPrice')
    def getInventoryAssetPrice(self, src__=0, ignore_variation=0,
                               standardise=0, omit_simulation=0, omit_input=0,
                               omit_output=0, selection_domain=None,
                               selection_report=None, precision=None, **kw):
      """
      Same thing as getInventory but returns an asset
      price rather than an inventory.
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      result = self.Resource_zGetInventory(
          src__=src__, ignore_variation=ignore_variation,
          standardise=standardise, omit_simulation=omit_simulation,
          omit_input=omit_input, omit_output=omit_output,
          selection_domain=selection_domain, selection_report=selection_report,
          precision=precision, **sql_kw)
      if src__ :
        return result

      total_result = 0.0
      if len(result) > 0:
        for result_line in result:
          if result_line.total_price is not None:
            total_result += result_line.total_price

      return total_result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryAssetPrice')
    def getCurrentInventoryAssetPrice(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryAssetPrice')
    def getAvailableInventoryAssetPrice(self, **kw):
      """
      Returns list of available inventory grouped by section or site
      (current inventory - deliverable)
      """
      kw['simulation_state'] = tuple(
                    list(self.getPortalReservedInventoryStateList()) + \
                    list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryAssetPrice')
    def getFutureInventoryAssetPrice(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      kw['simulation_state'] = tuple(
               list(self.getPortalFutureInventoryStateList()) + \
               list(self.getPortalReservedInventoryStateList()) + \
               list(self.getPortalCurrentInventoryStateList()))
      return self.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryList')
    def getInventoryHistoryList(self, src__=0, ignore_variation=0,
                                standardise=0, omit_simulation=0, omit_input=0,
                                omit_output=0, selection_domain=None,
                                selection_report=None, precision=None, **kw):
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
                      omit_input=omit_input, omit_output=omit_output,
                      selection_domain=selection_domain,
                      selection_report=selection_report, precision=precision,
                      **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, src__=0, ignore_variation=0,
                                 standardise=0, omit_simulation=0,
                                 omit_input=0, omit_output=0,
                                 selection_domain=None,
                                 selection_report=None, precision=None, **kw):
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
                    omit_input=omit_input, omit_output=omit_output,
                    selection_domain=selection_domain,
                    selection_report=selection_report, precision=precision,
                    **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryList')
    def getMovementHistoryList(self, src__=0, ignore_variation=0,
                               standardise=0, omit_simulation=0,
                               omit_input=0, omit_output=0,
                               selection_domain=None, selection_report=None,
                               initial_running_total_quantity=0,
                               initial_running_total_price=0, precision=None,
                               **kw):
      """Returns a list of movements which modify the inventory
      for a single or a group of resource, node, section, etc.
      A running total quantity and a running total price are available on
      brains. The initial values can be passed, in case you want to have an
      "initial summary line".
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      return self.Resource_zGetMovementHistoryList(
                         src__=src__, ignore_variation=ignore_variation,
                         standardise=standardise,
                         omit_simulation=omit_simulation,
                         omit_input=omit_input, omit_output=omit_output,
                         selection_domain=selection_domain,
                         selection_report=selection_report,
                         initial_running_total_quantity=
                                  initial_running_total_quantity,
                         initial_running_total_price=
                                  initial_running_total_price,
                         precision=precision, **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryStat')
    def getMovementHistoryStat(self, src__=0, ignore_variation=0,
                               standardise=0, omit_simulation=0, omit_input=0,
                               omit_output=0, selection_domain=None,
                               selection_report=None, precision=None, **kw):
      """
      getMovementHistoryStat is the pending to getMovementHistoryList
      for ListBox stat
      """
      sql_kw = self._generateSQLKeywordDict(**kw)
      return self.Resource_zGetInventory(src__=src__,
          ignore_variation=ignore_variation, standardise=standardise,
          omit_simulation=omit_simulation, omit_input=omit_input,
          omit_output=omit_output, selection_domain=selection_domain,
          selection_report=selection_report, precision=precision, **sql_kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, src__=0,
        ignore_variation=0, standardise=0, omit_simulation=0, omit_input=0, omit_output=0,
        selection_domain=None, selection_report=None, precision=None, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      sql_kw = self._generateSQLKeywordDict(order_by_expression='stock.date', **kw)
      sql_kw['group_by_expression'] = 'stock.uid'
      sql_kw['order_by_expression'] = 'stock.date'

      result = self.Resource_zGetInventory(src__=src__,
          ignore_variation=ignore_variation, standardise=standardise, omit_simulation=omit_simulation,
          omit_input=omit_input, omit_output=omit_output,
          selection_domain=selection_domain, selection_report=selection_report,
          precision=precision, **sql_kw)
      if src__ :
        return result

      total_inventory = 0.
      for inventory in result:
        if inventory['inventory'] is not None:
          total_inventory += inventory['inventory']
          if total_inventory < 0:
            return inventory['date']

      return None

    #######################################################
    # Traceability management
    security.declareProtected(Permissions.AccessContentsInformation, 'getTrackingList')
    def getTrackingList(self, src__=0,
        selection_domain=None, selection_report=None,
        strict_simulation_state=1, **kw) :
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

      resource (only in generic API in simulation)

      node        -  only take rows in stock table which node_uid is equivalent to node

      section        -  only take rows in stock table which section_uid is equivalent to section

      resource_category        -  only take rows in stock table which resource_uid is in resource_category

      node_category        -  only take rows in stock table which node_uid is in section_category

      section_category        -  only take rows in stock table which section_uid is in section_category

      variation_text - only take rows in stock table with specified variation_text
                       this needs to be extended with some kind of variation_category ?
                       XXX this way of implementing variation selection is far from perfect

      variation_category - variation or list of possible variations

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
      new_kw = self._generateSQLKeywordDict(table='item',strict_simulation_state=strict_simulation_state,**kw)
      new_kw['at_date'] = kw.get('at_date')

      # Extra parameters for the SQL Method
      new_kw['join_on_item'] = new_kw.get('at_date') or \
                               new_kw.get('input') or \
                               new_kw.get('output')
      new_kw['date_condition_in_join'] = not (new_kw.get('input') or new_kw.get('output'))

      # Pass simulation state to request
      if kw.has_key('item.simulation_state'):
          new_kw['simulation_state_list'] = kw['item.simulation_state']
      else:
          new_kw['simulation_state_list'] =  None

      return self.Resource_zGetTrackingList(src__=src__,
                                            selection_domain=selection_domain,
                                            selection_report=selection_report,
                                            **new_kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentTrackingList')
    def getCurrentTrackingList(self, **kw):
      """
      Returns list of current inventory grouped by section or site
      """
      kw['item.simulation_state'] = self.getPortalCurrentInventoryStateList()
      return self.getTrackingList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureTrackingList')
    def getFutureTrackingList(self, **kw):
      """
      Returns list of future inventory grouped by section or site
      """
      kw['item.simulation_state'] = tuple(list(self.getPortalFutureInventoryStateList())
          + list(self.getPortalReservedInventoryStateList()) + list(self.getPortalCurrentInventoryStateList()))
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
            if type(resource_aggregation_base_category) not in (type([]), type(())):
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
          #m.immediateReindexObject()
          m.reindexObject()
          #m.activate(priority=7).immediateReindexObject() # Too slow

      return result

    # Used for mergeDeliveryList.
    class MergeDeliveryListError(Exception): pass

    security.declareProtected( Permissions.ModifyPortalContent, 'mergeDeliveryList' )
    def mergeDeliveryList(self, delivery_list):
      """
        Merge multiple deliveries into one delivery.
        All delivery lines are merged into the first one.
        The first one is therefore called main_delivery here.
        The others are cancelled.
        Return the main delivery.
      """
      # Sanity checks.
      if len(delivery_list) == 0:
        raise self.MergeDeliveryListError, "No delivery is passed"
      elif len(delivery_list) == 1:
        raise self.MergeDeliveryListError, "Only one delivery is passed"

      main_delivery = delivery_list[0]
      delivery_list = delivery_list[1:]

      # Another sanity check. It is necessary for them to be identical in some attributes.
      for delivery in delivery_list:
        for attr in ('portal_type', 'simulation_state',
                     'source', 'destination',
                     'source_section', 'destination_section',
                     'source_decision', 'destination_decision',
                     'source_administration', 'destination_administration',
                     'source_payment', 'destination_payment'):
          main_value = main_delivery.getProperty(attr)
          value = delivery.getProperty(attr)
          if  main_value != value:
            raise self.MergeDeliveryListError, \
              "%s is not the same between %s and %s (%s and %s)" % (attr, delivery.getId(), main_delivery.getId(), value, main_value)

      # One more sanity check. Check if discounts are the same, if any.
      main_discount_list = main_delivery.contentValues(filter = {'portal_type': self.getPortalDiscountTypeList()})
      for delivery in delivery_list:
        discount_list = delivery.contentValues(filter = {'portal_type': self.getPortalDiscountTypeList()})
        if len(main_discount_list) != len(discount_list):
          raise self.MergeDeliveryListError, "Discount is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())
        for discount in discount_list:
          for main_discount in main_discount_list:
            if discount.getDiscount() == main_discount.getDiscount() \
               and discount.getDiscountRatio() == main_discount.getDiscountRatio() \
               and discount.getDiscountType() == main_discount.getDiscountType() \
               and discount.getImmediateDiscount() == main_discount.getImmediateDiscount():
              break
          else:
            raise self.MergeDeliveryListError, "Discount is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())

      # One more sanity check. Check if payment conditions are the same, if any.
      main_payment_condition_list = main_delivery.contentValues(filter = {'portal_type': self.getPortalPaymentConditionTypeList()})
      for delivery in delivery_list:
        payment_condition_list = delivery.contentValues(filter = {'portal_type': self.getPortalPaymentConditionTypeList()})
        if len(main_payment_condition_list) != len(payment_condition_list):
          raise self.MergeDeliveryListError, "Payment Condition is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())
        for condition in payment_condition_list:
          for main_condition in main_payment_condition_list:
            if condition.getPaymentMode() == main_condition.getPaymentMode() \
               and condition.getPaymentAdditionalTerm() == main_condition.getPaymentAdditionalTerm() \
               and condition.getPaymentAmount() == main_condition.getPaymentAmount() \
               and condition.getPaymentEndOfMonth() == main_condition.getPaymentEndOfMonth() \
               and condition.getPaymentRatio() == main_condition.getPaymentRatio() \
               and condition.getPaymentTerm() == main_condition.getPaymentTerm():
              break
          else:
            raise self.MergeDeliveryListError, "Payment Condition is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())

      # Make sure that all activities are flushed, to get simulation movements from delivery cells.
      for delivery in delivery_list:
        for order in delivery.getCausalityValueList(portal_type = self.getPortalOrderTypeList()):
          for applied_rule in order.getCausalityRelatedValueList(portal_type = 'Applied Rule'):
            applied_rule.flushActivity(invoke = 1)
        for causality_related_delivery in delivery.getCausalityValueList(portal_type = self.getPortalDeliveryTypeList()):
          for applied_rule in causality_related_delivery.getCausalityRelatedValueList(portal_type = 'Applied Rule'):
            applied_rule.flushActivity(invoke = 1)

      # Get a list of simulated movements and invoice movements.
      main_simulated_movement_list = main_delivery.getSimulatedMovementList()
      main_invoice_movement_list = main_delivery.getInvoiceMovementList()
      simulated_movement_list = main_simulated_movement_list[:]
      invoice_movement_list = main_invoice_movement_list[:]
      for delivery in delivery_list:
        simulated_movement_list.extend(delivery.getSimulatedMovementList())
        invoice_movement_list.extend(delivery.getInvoiceMovementList())

      #for movement in simulated_movement_list + invoice_movement_list:
      #  parent = movement.aq_parent
      #  LOG('mergeDeliveryList', 0, 'movement = %s, parent = %s, movement.getPortalType() = %s, parent.getPortalType() = %s' % (repr(movement), repr(parent), repr(movement.getPortalType()), repr(parent.getPortalType())))

      LOG('mergeDeliveryList', 0, 'simulated_movement_list = %s, invoice_movement_list = %s' % (str(simulated_movement_list), str(invoice_movement_list)))
      for main_movement_list, movement_list in \
        ((main_simulated_movement_list, simulated_movement_list),
         (main_invoice_movement_list, invoice_movement_list)):
        root_group = self.collectMovement(movement_list,
                                          check_order = 0,
                                          check_path = 0,
                                          check_date = 0,
                                          check_criterion = 1,
                                          check_resource = 1,
                                          check_base_variant = 1,
                                          check_variant = 1)
        for criterion_group in root_group.group_list:
          LOG('mergeDeliveryList dump tree', 0, 'criterion = %s, movement_list = %s, group_list = %s' % (repr(criterion_group.criterion), repr(criterion_group.movement_list), repr(criterion_group.group_list)))
          for resource_group in criterion_group.group_list:
            LOG('mergeDeliveryList dump tree', 0, 'resource = %s, movement_list = %s, group_list = %s' % (repr(resource_group.resource), repr(resource_group.movement_list), repr(resource_group.group_list)))
            for base_variant_group in resource_group.group_list:
              LOG('mergeDeliveryList dump tree', 0, 'base_category_list = %s, movement_list = %s, group_list = %s' % (repr(base_variant_group.base_category_list), repr(base_variant_group.movement_list), repr(base_variant_group.group_list)))
              for variant_group in base_variant_group.group_list:
                LOG('mergeDeliveryList dump tree', 0, 'category_list = %s, movement_list = %s, group_list = %s' % (repr(variant_group.category_list), repr(variant_group.movement_list), repr(variant_group.group_list)))

        for criterion_group in root_group.group_list:
          for resource_group in criterion_group.group_list:
            for base_variant_group in resource_group.group_list:
              # Get a list of categories.
              category_dict = {}
              for variant_group in base_variant_group.group_list:
                for category in variant_group.category_list:
                  category_dict[category] = 1
              category_list = category_dict.keys()

              # Try to find a delivery line.
              delivery_line = None
              for movement in base_variant_group.movement_list:
                if movement in main_movement_list:
                  if movement.aq_parent.getPortalType() in self.getPortalSimulatedMovementTypeList() \
                    or movement.aq_parent.getPortalType() in self.getPortalInvoiceMovementTypeList():
                    delivery_line = movement.aq_parent
                  else:
                    delivery_line = movement
                  LOG('mergeDeliveryList', 0, 'delivery_line %s is found: criterion = %s, resource = %s, base_category_list = %s' % (repr(delivery_line), repr(criterion_group.criterion), repr(resource_group.resource), repr(base_variant_group.base_category_list)))
                  break

              if delivery_line is None:
                # Not found. So create a new delivery line.
                movement = base_variant_group.movement_list[0]
                if movement.aq_parent.getPortalType() in self.getPortalSimulatedMovementTypeList() \
                  or movement.aq_parent.getPortalType() in self.getPortalInvoiceMovementTypeList():
                  delivery_line_type = movement.aq_parent.getPortalType()
                else:
                  delivery_line_type = movement.getPortalType()
                delivery_line = main_delivery.newContent(portal_type = delivery_line_type,
                                                         resource = resource_group.resource)
                LOG('mergeDeliveryList', 0, 'New delivery_line %s is created: criterion = %s, resource = %s, base_category_list = %s' % (repr(delivery_line), repr(criterion_group.criterion), repr(resource_group.resource), repr(base_variant_group.base_category_list)))

              # Update the base categories and categories.
              #LOG('mergeDeliveryList', 0, 'base_category_list = %s, category_list = %s' % (repr(base_category_list), repr(category_list)))
              delivery_line.setVariationBaseCategoryList(base_variant_group.base_category_list)
              delivery_line.setVariationCategoryList(category_list)

              object_to_update = None
              for variant_group in base_variant_group.group_list:
                if len(variant_group.category_list) == 0:
                  object_to_update = delivery_line
                else:
                  for delivery_cell in delivery_line.contentValues():
                    predicate_value_list = delivery_cell.getPredicateValueList()
                    LOG('mergeDeliveryList', 0, 'delivery_cell = %s, predicate_value_list = %s, variant_group.category_list = %s' % (repr(delivery_cell), repr(predicate_value_list), repr(variant_group.category_list)))
                    if len(predicate_value_list) == len(variant_group.category_list):
                      for category in variant_group.category_list:
                        if category not in predicate_value_list:
                          break
                      else:
                        object_to_update = delivery_cell
                        break

                #LOG('mergeDeliveryList', 0, 'object_to_update = %s' % repr(object_to_update))
                if object_to_update is not None:
                  cell_price = object_to_update.getPrice() or 0.0
                  cell_quantity = object_to_update.getQuantity() or 0.0
                  cell_target_quantity = object_to_update.getNetConvertedTargetQuantity() or 0.0 # XXX What to do ?
                  cell_total_price = cell_target_quantity * cell_price
                  cell_category_list = list(object_to_update.getCategoryList())

                  for movement in variant_group.movement_list:
                    if movement in main_movement_list:
                      continue
                    LOG('mergeDeliveryList', 0, 'movement = %s' % repr(movement))
                    cell_quantity += movement.getQuantity()
                    cell_target_quantity += movement.getNetConvertedTargetQuantity()
                    try:
                      # XXX WARNING - ADD PRICED QUANTITY
                      cell_price = movement.getPrice()
                      cell_total_price += movement.getNetConvertedTargetQuantity() * cell_price
                    except TypeError:
                      cell_total_price = None
                    for category in movement.getCategoryList():
                      if category not in cell_category_list:
                        cell_category_list.append(category)
                    # Make sure that simulation movements point to an appropriate delivery line or
                    # delivery cell.
                    if hasattr(movement, 'getDeliveryRelatedValueList'):
                      for simulation_movement in \
                        movement.getDeliveryRelatedValueList(portal_type = 'Simulation Movement'):
                        simulation_movement.setDeliveryValue(object_to_update)
                        #simulation_movement.reindexObject()
                    if hasattr(movement, 'getOrderRelatedValueList'):
                      for simulation_movement in \
                        movement.getOrderRelatedValueList(portal_type = 'Simulation Movement'):
                        simulation_movement.setOrderValue(object_to_update)
                        #simulation_movement.reindexObject()

                  if cell_target_quantity != 0 and cell_total_price is not None:
                    average_price = cell_total_price / cell_target_quantity
                  else:
                    average_price = 0

                  LOG('mergeDeliveryList', 0, 'object_to_update = %s, cell_category_list = %s, cell_target_quantity = %s, cell_quantity = %s, average_price = %s' % (repr(object_to_update), repr(cell_category_list), repr(cell_target_quantity), repr(cell_quantity), repr(average_price)))
                  object_to_update.setCategoryList(cell_category_list)
                  if object_to_update.getPortalType() in self.getPortalSimulatedMovementTypeList():
                    object_to_update.edit(target_quantity = cell_target_quantity,
                                          quantity = cell_quantity,
                                          price = average_price,
                                          )
                  elif object_to_update.getPortalType() in self.getPortalInvoiceMovementTypeList():
                    # Invoices do not have target quantities, and the price never change.
                    object_to_update.edit(quantity = cell_quantity,
                                          price = cell_price,
                                          )
                  else:
                    raise self.MergeDeliveryListError, "Unknown portal type %s" % str(object_to_update.getPortalType())
                  #object_to_update.immediateReindexObject()
                else:
                  raise self.MergeDeliveryListError, "No object to update"

      # Merge containers. Just copy them from other deliveries into the main.
      for delivery in delivery_list:
        container_id_list = delivery.contentIds(filter = {'portal_type': self.getPortalContainerTypeList()})
        if len(container_id_list) > 0:
          copy_data = delivery.manage_copyObjects(ids = container_id_list)
          new_id_list = main_delivery.manage_pasteObjects(copy_data)

      # Unify the list of causality.
      causality_list = main_delivery.getCausalityValueList()
      for delivery in delivery_list:
        for causality in delivery.getCausalityValueList():
          if causality not in causality_list:
            causality_list.append(causality)
      LOG("mergeDeliveryList", 0, "causality_list = %s" % str(causality_list))
      main_delivery.setCausalityValueList(causality_list)

      # Cancel deliveries.
      for delivery in delivery_list:
        LOG("mergeDeliveryList", 0, "cancelling %s" % repr(delivery))
        delivery.cancel()

      # Reindex the main delivery.
      main_delivery.reindexObject()

      return main_delivery


InitializeClass(SimulationTool)
