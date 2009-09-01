# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Predicate import Predicate
from Acquisition import aq_base
from zLOG import LOG, WARNING

class Rule(Predicate, XMLObject):
  """
    Rule objects implement the simulation algorithm
    (expand, solve)

    Example of rules

    - Stock rule (checks stocks)

    - Order rule (copies movements from an order)

    - Capacity rule (makes sure stocks / sources are possible)

    - Transformation rule (expands transformations)

    - Template rule (creates submovements with a template system)
      used in Invoice rule, Paysheet rule, etc.

    Rules are called one by one at the global level (the rules folder)
    and at the local level (applied rules in the simulation folder)

    The simulation_tool includes rules which are parametrized by the sysadmin
    The simulation_tool does the logics of checking, calling, etc.

    simulation_tool is a subclass of Folder & Tool
  """

  # CMF Type Definition
  meta_type = 'ERP5 Rule'
  portal_type = 'Rule'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isPredicate = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  
  zope.interface.implements( interfaces.IPredicate,
                     interfaces.IRule )

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Predicate
                    , PropertySheet.Reference
                    , PropertySheet.Version
                    , PropertySheet.Rule
                    )
  
  # Portal Type of created children
  movement_type = 'Simulation Movement'

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """Tells wether generated movement needs to be accounted or not.
    
    Only account movements which are not associated to a delivery;
    Whenever delivery is there, delivery has priority
    """
    return movement.getDeliveryValue() is None

  security.declareProtected(Permissions.ModifyPortalContent,
                            'constructNewAppliedRule')
  def constructNewAppliedRule(self, context, id=None, 
                              activate_kw=None, **kw):
    """
      Creates a new applied rule which points to self
    """
    # XXX Parameter **kw is useless, so, we should remove it
    portal_types = getToolByName(self, 'portal_types')
    if id is None:
      id = context.generateNewId()
    if getattr(aq_base(context), id, None) is None:
      context.newContent(id=id,
                         portal_type='Applied Rule',
                         specialise_value=self,
                         activate_kw=activate_kw)
    return context.get(id)

  def _isBPM(self):
    """Checks if rule is used in BPM"""
    return bool(self.getTradePhaseList())

  # Simulation workflow
  def test(self, *args, **kw):
    """
    If no test method is defined, return False, to prevent infinite loop
    """
    if not self.getTestMethodId():
      return False
    return Predicate.test(self, *args, **kw)

  def _expandBPM(self, applied_rule, force=0, **kw):
    """Generic expand with helpers.
    Do NOT overload, use helpers."""
    add_list, modify_dict, \
      delete_list = self._getCompensatedMovementList(applied_rule, **kw)

    # delete not needed movements
    for movement_id in delete_list:
      applied_rule._delObject(movement_id)

    # update existing
    for movement, property_dict in modify_dict.items():
      applied_rule[movement].edit(**property_dict)

    # add new ones
    for movement_dict in add_list:
      movement_id = applied_rule._get_id(movement_dict.pop('id', None))
      new_movement = applied_rule.newContent(id=movement_id,
          portal_type=self.movement_type, **movement_dict)

    for o in applied_rule.objectValues():
      o.expand(**kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """
      Expands the current movement downward.

      An applied rule can be expanded only if its parent movement
      is expanded.
    """
    if self._isBPM():
      return self._expandBPM(applied_rule, **kw)
    for o in applied_rule.objectValues():
      o.expand(**kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, applied_rule, solution_list):
    """
      Solve inconsistency according to a certain number of solutions
      templates. This updates the

      -> new status -> solved

      This applies a solution to an applied rule. Once
      the solution is applied, the parent movement is checked.
      If it does not diverge, the rule is reexpanded. If not,
      diverge is called on the parent movement.
    """

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self, applied_rule):
    """
      -> new status -> diverged

      This basically sets the rule to "diverged"
      and blocks expansion process
    """
    pass

  # Solvers
  security.declareProtected( Permissions.AccessContentsInformation,
                            'isDivergent')
  def isDivergent(self, sim_mvt, ignore_list=[]):
    """
    Returns true if the Simulation Movement is divergent comparing to
    the delivery value
    """
    delivery = sim_mvt.getDeliveryValue()
    if delivery is None:
      return 0
      
    if self.getDivergenceList(sim_mvt) == []:
      return 0
    else:
      return 1
    
  security.declareProtected(Permissions.View, 'getDivergenceList')
  def getDivergenceList(self, sim_mvt):
    """
    Return a list of messages that contains the divergences.
    """
    result_list = []
    for divergence_tester in self.contentValues(
               portal_type=self.getPortalDivergenceTesterTypeList()):
      result = divergence_tester.explain(sim_mvt)
      result_list.extend(result)
    return result_list

  # XXX getSolverList is not part of the API and should be removed.
  # Use getDivergenceList instead.
#    security.declareProtected(Permissions.View, 'getSolverList')

#    def getSolverList(self, applied_rule):
#      """
#        Returns a list Divergence solvers
#      """

  # Deliverability / orderability
  def isOrderable(self, movement):
    return 0

  def isDeliverable(self, movement):
    return 0

  def isStable(self, applied_rule, **kw):
    """
    - generate a list of previsions
    - compare the prevision with existing children
    - return 1 if they match, 0 else
    """
    list = self._getCompensatedMovementList(applied_rule, **kw)
    for e in list:
      if len(e) > 0:
        return 0
    return 1

#### Helpers to overload
  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Rule specific dictionary used to update _getExpandablePropertyDict
    This method might be overloaded.
    """
    return {}

  def _getInputMovementList(self, applied_rule):
    """Return list of movements for applied rule.
    This method might be overloaded"""
    return [applied_rule.getParentValue()]

  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of dictionaries, that contain calculated content of
    current Simulation Movements in applied rule.
    based on its context (parent movement, delivery, configuration ...)

    These previsions are returned as dictionaries.
    """
    prevision_dict_list = []
    for input_movement, business_path in self \
        ._getInputMovementAndPathTupleList(applied_rule):
      prevision_dict_list.append(self._getExpandablePropertyDict(applied_rule,
          input_movement, business_path))
    return prevision_dict_list

#### Helpers NOT to overload
  def _getCurrentMovementList(self, applied_rule, **kw):
    """
    Returns the list of current children of the applied rule, sorted in 3
    groups : immutables/mutables/deletable

    If a movement is not frozen, and has no delivered child, it can be
    deleted.
    Else, if a movement is not frozen, and has some delivered child, it can
    be modified.
    Else, it cannot be modified.

    - is delivered
    - has delivered childs (including self)
    - is in reserved or current state
    - is frozen

    a movement is deletable if it has no delivered child, is not in current
    state, and not in delivery movements.
    a movement 
    """
    immutable_movement_list = []
    mutable_movement_list = []
    deletable_movement_list = []
    
    for movement in applied_rule.contentValues(portal_type=self.movement_type):
      if movement.isFrozen():
        immutable_movement_list.append(movement)
      else:
        if movement._isTreeDelivered():
          mutable_movement_list.append(movement)
        else:
          deletable_movement_list.append(movement)

    return (immutable_movement_list, mutable_movement_list,
            deletable_movement_list)

  def _getInputMovementAndPathTupleList(self, applied_rule):
    """Returns list of tuples (movement, business_path)"""
    input_movement_list = self._getInputMovementList(applied_rule)
    business_process = applied_rule.getBusinessProcessValue()

    input_movement_and_path_list = []
    business_path_list = []
    for input_movement in input_movement_list:
      for business_path in business_process.getPathValueList(
                          self.getTradePhaseList(),
                          input_movement):
        input_movement_and_path_list.append((input_movement, business_path))
        business_path not in business_path_list and business_path_list \
            .append(business_path)

    if len(business_path_list) > 1:
      raise NotImplementedError

    return input_movement_and_path_list

  def _getCompensatedMovementListBPM(self, applied_rule, **kw):
    """Compute the difference between prevision and existing movements

    Immutable movements need compensation, mutable ones needs to be modified
    """
    add_list = [] # list of movements to be added
    modify_dict = {} # dict of movements to be modified
    delete_list = [] # list of movements to be deleted

    prevision_list = self._generatePrevisionList(applied_rule, **kw)
    immutable_movement_list, mutable_movement_list, \
        deletable_movement_list = self._getCurrentMovementList(applied_rule,
                                                               **kw)
    movement_list = immutable_movement_list + mutable_movement_list \
                    + deletable_movement_list
    non_matched_list = movement_list[:] # list of remaining movements

    for prevision in prevision_list:
      p_matched_list = []
      for movement in non_matched_list:
        for prop in self.getMatchingPropertyList():
          if prevision.get(prop) != movement.getProperty(prop):
            break
        else:
          p_matched_list.append(movement)

      # Movements exist, we'll try to make them match the prevision
      if p_matched_list != []:
        # Check the quantity
        m_quantity = 0.0
        for movement in p_matched_list:
          m_quantity += movement.getQuantity()#getCorrectedQuantity()
        if m_quantity != prevision.get('quantity'):
          # special case - quantity
          if movement.isPropertyForced('quantity'):
            # TODO: support compensation if not prevent_compensation
            LOG('%s:%s' % (self.getRelativeUrl(), movement.getRelativeUrl()), WARNING,
                'Quantity forced to stay as %s, even if wanted %s' % (m_quantity, prevision.get('quantity')))
            # DivergenceDecision mangle
            pass
          else:
            q_diff = prevision.get('quantity') - m_quantity
            # try to find a movement that can be edited
            for movement in p_matched_list:
              if movement in (mutable_movement_list \
                  + deletable_movement_list):
                # mark as requiring modification
                prop_dict = modify_dict.setdefault(movement.getId(), {})
                #prop_dict['quantity'] = movement.getCorrectedQuantity() + \
                prop_dict['quantity'] = movement.getQuantity() + \
                    q_diff
                break
            else:
              # no modifiable movement was found, need to compensate by quantity
              raise NotImplementedError('Need to generate quantity compensation')

        for movement in p_matched_list:
          if movement in (mutable_movement_list \
              + deletable_movement_list):
            prop_dict = modify_dict.setdefault(movement.getId(), {})
            for k, v in prevision.items():
              if k not in ('quantity',) and v != movement.getProperty(k):
                # TODO: acceptance range
                if movement.isPropertyForced(k):
                  # support compensation if not prevent_compensation
                  LOG('%s:%s' % (self.getRelativeUrl(), movement.getRelativeUrl()), WARNING,
                      'Property %s forced to stay as %r, even if wanted %r' % (k, movement.getProperty(k), v))
                  # DivergenceDecision mangle
                  continue
                prop_dict.setdefault(k, v)

        # update movement lists
        for movement in p_matched_list:
          non_matched_list.remove(movement)

      # No movement matched, we need to create one
      else:
        add_list.append(prevision)

    # delete non matched movements
    for movement in non_matched_list:
      if movement in deletable_movement_list:
        # delete movement
        delete_list.append(movement.getId())
      elif movement in mutable_movement_list:
        # set movement quantity to 0 to make it "void"
        prop_dict = modify_dict.setdefault(movement.getId(), {})
        prop_dict['quantity'] = 0.0
      else:
        # movement not modifiable, we can decide to create a compensation
        # with negative quantity
        raise NotImplementedError("Tried to delete immutable movement %s" % \
            movement.getRelativeUrl())
    return (add_list, modify_dict, delete_list)

  def _getCompensatedMovementList(self, applied_rule,
                                  matching_property_list=(
                                  'resource',
                                  'variation_category_list',
                                  'variation_property_dict',), **kw):
    """
    Compute the difference between prevision and existing movements

    immutable movements need compensation, mutables needs to be modified

    XXX For now, this implementation is too simple. It could be improved by
    using MovementGroups
    """
    if self._isBPM():
      return self._getCompensatedMovementListBPM(applied_rule,
          matching_property_list=matching_property_list, **kw)
    add_list = [] # list of movements to be added
    modify_dict = {} # dict of movements to be modified
    delete_list = [] # list of movements to be deleted

    prevision_list = self._generatePrevisionList(applied_rule, **kw)
    immutable_movement_list, mutable_movement_list, \
        deletable_movement_list = self._getCurrentMovementList(applied_rule,
                                                               **kw)
    movement_list = immutable_movement_list + mutable_movement_list \
                    + deletable_movement_list
    non_matched_list = movement_list[:] # list of remaining movements 

    for prevision in prevision_list:
      p_matched_list = []
      for movement in non_matched_list:
        for prop in matching_property_list:
          if prevision.get(prop) != movement.getProperty(prop):
            break
        else:
          p_matched_list.append(movement)

      # XXX hardcoded ...
#       LOG("Rule, _getCompensatedMovementList", WARNING, 
#           "Hardcoded properties check")
      # Movements exist, we'll try to make them match the prevision
      if p_matched_list != []:
        # Check the quantity
        m_quantity = 0.0
        for movement in p_matched_list:
          m_quantity += movement.getQuantity()#getCorrectedQuantity()
        if m_quantity != prevision.get('quantity'):
          q_diff = prevision.get('quantity') - m_quantity
          # try to find a movement that can be edited
          for movement in p_matched_list:
            if movement in (mutable_movement_list \
                + deletable_movement_list):
              # mark as requiring modification
              prop_dict = modify_dict.setdefault(movement.getId(), {})
              #prop_dict['quantity'] = movement.getCorrectedQuantity() + \
              prop_dict['quantity'] = movement.getQuantity() + \
                  q_diff
              break
          # no modifiable movement was found, need to create one
          else:
            prevision['quantity'] = q_diff
            add_list.append(prevision)

        # Check the date
        for movement in p_matched_list:
          if movement in (mutable_movement_list \
              + deletable_movement_list):
            prop_dict = modify_dict.setdefault(movement.getId(), {})
            for prop in ('start_date', 'stop_date'):
              #XXX should be >= 15
              if prevision.get(prop) != movement.getProperty(prop):
                prop_dict[prop] = prevision.get(prop)
                break

            for k, v in prevision.items():
              if k not in ('quantity', 'start_date', 'stop_date') and\
                      v != movement.getProperty(k):
                prop_dict.setdefault(k, v)

        # update movement lists
        for movement in p_matched_list:
          non_matched_list.remove(movement)

      # No movement matched, we need to create one
      else:
        add_list.append(prevision)

    # delete non matched movements
    for movement in non_matched_list:
      if movement in deletable_movement_list:
        # delete movement
        delete_list.append(movement.getId())
      elif movement in mutable_movement_list:
        # set movement quantity to 0 to make it "void"
        prop_dict = modify_dict.setdefault(movement.getId(), {})
        prop_dict['quantity'] = 0.0
      else:
        # movement not modifiable, we can decide to create a compensation
        # with negative quantity
        raise NotImplementedError(
                "Can not create a compensation movement for %s" % \
                movement.getRelativeUrl())
    return (add_list, modify_dict, delete_list)

  def _getExpandablePropertyDict(self, applied_rule, movement, business_path,
      **kw):
    """
    Return a Dictionary with the Properties used to edit the simulation
    Do NOT overload this method, use _getExpandablePropertyUpdateDict instead
    """
    property_dict = {}

    default_property_list = self.getExpandablePropertyList()
    for prop in default_property_list:
      property_dict[prop] = movement.getProperty(prop)

    # Arrow
    for base_category in \
        business_path.getSourceBaseCategoryList() +\
        business_path.getDestinationBaseCategoryList():
      # XXX: we need to use _list for categories *always*
      category_url = business_path.getDefaultAcquiredCategoryMembership(
          base_category, context=movement)
      if category_url not in ['', None]:
        property_dict['%s_list' % base_category] = [category_url]
      else:
        property_dict['%s_list' % base_category] = []
    # Amount
    if business_path.getQuantity():
      property_dict['quantity'] = business_path.getQuantity()
    elif business_path.getEfficiency():
      property_dict['quantity'] = movement.getQuantity() *\
        business_path.getEfficiency()
    else:
      property_dict['quantity'] = movement.getQuantity()

    if movement.getStartDate() == movement.getStopDate():
      property_dict['start_date'] = business_path.getExpectedStartDate(
          movement)
      property_dict['stop_date'] = business_path.getExpectedStopDate(movement)
    else: # XXX shall not be used, but business_path.getExpectedStart/StopDate
          # do not works on second path...
      property_dict['start_date'] = movement.getStartDate()
      property_dict['stop_date'] = movement.getStopDate()

    # rule specific
    property_dict.update(**self._getExpandablePropertyUpdateDict(applied_rule,
      movement, business_path, property_dict))

    # save a relation to business path
    property_dict['causality_list'] = [business_path.getRelativeUrl()]

    return property_dict


