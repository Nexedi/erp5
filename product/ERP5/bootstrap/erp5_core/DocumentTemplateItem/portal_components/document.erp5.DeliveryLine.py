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

import zope.interface
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.ImmobilisationMovement import ImmobilisationMovement

from inspect import getargspec
from Products.ERP5Type.Base import Base
edit_args_list = getargspec(Base._edit).args

from erp5.component.interface.IDivergenceController import IDivergenceController

class DeliveryLine(Movement, XMLMatrix, ImmobilisationMovement):
  """
  A DeliveryLine object allows to implement lines in
  Deliveries (packing list, order, invoice, etc.)

  It may include a price (for insurance, for customs, for invoices,
  for orders)
  """
  meta_type = 'ERP5 Delivery Line'
  portal_type = 'Delivery Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.ItemAggregation
                    , PropertySheet.SortIndex
                    )

  # Declarative interfaces
  zope.interface.implements(IDivergenceController,)

  # Multiple inheritance definition
  updateRelatedContent = XMLMatrix.updateRelatedContent

  # Force in _edit to modify variation_base_category_list first
  def _edit(self, edit_order=(), **kw):
    # XXX FIXME For now, special cases are handled in _edit methods in many
    # documents : DeliveryLine, DeliveryCell ... Ideally, to prevent code
    # duplication, it should be handled in a _edit method present only in
    # Amount.py

    # If variations and resources are set at the same time, resource must be
    # set before any variation.
    before_order = ('resource', 'resource_value',
                    'variation_base_category_list',
                    'variation_category_list')
    before_kw = {k: kw.pop(k) for k in before_order if k in kw}
    if before_kw:
      before_kw.update((k, kw[k]) for k in edit_args_list if k in kw)
      Base._edit(self, edit_order=before_order, **before_kw)
    if kw:
      Movement._edit(self, edit_order=edit_order, **kw)

  # We must check if the user has changed the resource of particular line
  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  def edit(self, REQUEST=None, force_update = 0, reindex_object=1, **kw):
    return self._edit(REQUEST=REQUEST, force_update=force_update, reindex_object=reindex_object, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self):
    """To avoid duplicate docstring. Please read movement interface."""
    return self.getParentValue().isAccountable() and (not self.hasCellContent())

  security.declareProtected(Permissions.AccessContentsInformation,
                           'isMovingItem')
  def isMovingItem(self, item):
    type_based_script = self._getTypeBasedMethod('isMovingItem')
    if type_based_script:
      return type_based_script(item)
    return self.isAccountable()

  def _getTotalPrice(self, default=0.0, context=None, fast=0):
    """
    Returns the total price for this line, this line contains, or the cells it contains.

    if hasLineContent: return sum of lines total price
    if hasCellContent: return sum of cells total price
    else: return quantity * price
    if fast argument is true, inventory API will be used.
    """
    if fast:
      kw = {}
      kw['section_uid'] = self.getDestinationSectionUid()
      kw['stock.explanation_uid'] = self.getExplanationUid()
      kw['relative_url'] = ( '%s/%%' % (
        self.getRelativeUrl().replace('_', '\\_')),
        self.getRelativeUrl() )
      kw['only_accountable'] = False
      return self.getPortalObject().portal_simulation.getInventoryAssetPrice(**kw)
    if self.hasLineContent():
      meta_type = self.meta_type
      return sum(l.getTotalPrice(context=context)
                 for l in self.objectValues() if l.meta_type==meta_type)
    elif not self.hasCellContent(base_id='movement'):
      return Movement._getTotalPrice(self, default=default, context=context)
    return sum(cell.getTotalPrice(default=0.0, context=context)
               for cell in self.getCellValueList())

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTotalQuantity')
  def getTotalQuantity(self, fast=0):
    """
    Returns the quantity if no cell or the total quantity if cells

    if hasLineContent: return sum of lines total quantity
    if hasCellContent: return sum of cells total quantity
    else: return quantity
    if fast argument is true, inventory API will be used.
    """
    if fast:
      kw = {}
      kw['section_uid'] = self.getDestinationSectionUid()
      kw['stock.explanation_uid'] = self.getExplanationUid()
      kw['relative_url'] = ( '%s/%%' % (
        self.getRelativeUrl().replace('_', '\\_')),
        self.getRelativeUrl() )
      kw['only_accountable'] = False
      return self.getPortalObject().portal_simulation.getInventory(**kw)

    base_id = 'movement'
    if self.hasLineContent():
      meta_type = self.meta_type
      return sum(l.getTotalQuantity() for l in
          self.objectValues() if l.meta_type==meta_type)
    elif self.hasCellContent(base_id=base_id):
      return sum([cell.getQuantity() for cell in self.getCellValueList()])
    return self.getQuantity()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasLineContent')
  def hasLineContent(self):
    """Return true if the object contains lines.

      This method only checks the first sub line because all sub
      lines should be same meta type in reality if we have line
      inside line.
    """
    return len(self) != 0 and self.objectValues()[0].meta_type == self.meta_type

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasCellContent')
  def hasCellContent(self, base_id='movement'):
    """Return true if the object contains cells.
    """
    # Do not use XMLMatrix.hasCellContent, because it can generate
    # inconsistency in catalog
    # Exemple: define a line and set the matrix cell range, but do not create
    # cell.
    # Line was in this case consider like a movement, and was catalogued.
    # But, getVariationText of the line was not empty.
    # So, in ZODB, resource as without variation, but in catalog, this was
    # the contrary...
    cell_range = XMLMatrix.getCellRange(self, base_id=base_id)
    return (cell_range is not None and len(cell_range) > 0)
    # DeliveryLine can be a movement when it does not content any cell and
    # matrix cell range is not empty.
    # Better implementation is needed.
    # We want to define a line without cell, defining a variated resource.
    # If we modify the cell range, we need to move the quantity to a new
    # cell, which define the same variated resource.
#       return XMLMatrix.hasCellContent(self, base_id=base_id)

  security.declareProtected( Permissions.AccessContentsInformation,
      'isMovement' )
  def isMovement(self):
    """
    returns true is the object contains no submovement (line or cell)
    """
    object_list = self.objectValues()
    if object_list:
      portal_type = self.getPortalObject().getPortalMovementTypeList()
      for ob in object_list:
        if ob.getPortalType() in portal_type:
          return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'getMovedItemUidList')
  def getMovedItemUidList(self):
    """This method returns an uid list of items
    """
    return [item.getUid() for item in self.getAggregateValueList() \
        if self.isMovingItem(item)]

  security.declareProtected( Permissions.AccessContentsInformation, 'getCellValueList' )
  def getCellValueList(self, base_id='movement'):
    """
    This method can be overriden
    """
    return XMLMatrix.getCellValueList(self, base_id=base_id)

  security.declareProtected( Permissions.AccessContentsInformation, 'getCell' )
  def getCell(self, *kw , **kwd):
    """
    This method can be overriden
    """
    if 'base_id' not in kwd:
      kwd['base_id'] = 'movement'

    return XMLMatrix.getCell(self, *kw, **kwd)

  security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
  def newCell(self, *kw, **kwd):
    """
    This method creates a new cell
    """
    if 'base_id' not in kwd:
      kwd['base_id'] = 'movement'

    return XMLMatrix.newCell(self, *kw, **kwd)

  def applyToDeliveryLineRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
    # Find related in simulation
    for my_simulation_movement in self.getDeliveryRelatedValueList(
                                            portal_type = 'Simulation Movement'):
      # And apply
      getattr(my_simulation_movement.getObject(), method_id)()
    for c in self.objectValues(portal_type='Delivery Cell'):
      for my_simulation_movement in c.getDeliveryRelatedValueList(
                                            portal_type = 'Simulation Movement'):
        # And apply
        getattr(my_simulation_movement.getObject(), method_id)()

  def reindexObject(self, *k, **kw):
    """Reindex children"""
    self.recursiveReindexObject(*k, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
  def getInventoriatedQuantity(self):
    """
    """
    return Movement.getInventoriatedQuantity(self)

#     security.declarePrivate('_checkConsistency')
#     def _checkConsistency(self, fixit=0, mapped_value_property_list = ('quantity', 'price')):
#       """
#         Check the constitency of transformation elements
#       """
#       error_list = XMLMatrix._checkConsistency(self, fixit=fixit)
#
#       # First quantity
#       # We build an attribute equality and look at all cells
#       q_constraint = Constraint.AttributeEquality(
#         domain_base_category_list = self.getVariationBaseCategoryList(),
#         predicate_operator = 'SUPERSET_OF',
#         mapped_value_property_list = mapped_value_property_list )
#       for k in self.getCellKeys(base_id = 'movement'):
#         kw={}
#         kw['base_id'] = 'movement'
#         c = self.getCell(*k, **kw)
#         if c is not None:
#           predicate_value = []
#           for p in k:
#             if p is not None: predicate_value += [p]
#           q_constraint.edit(predicate_value_list = predicate_value)
#           if fixit:
#             error_list += q_constraint.fixConsistency(c)
#           else:
#             error_list += q_constraint.checkConsistency(c)
#           if list(c.getVariationCategoryList()) != predicate_value:
#             error_message =  "Variation %s but sould be %s" % (c.getVariationCategoryList(),predicate_value)
#             if fixit:
#               c.setVariationCategoryList(predicate_value)
#               error_message += " (Fixed)"
#             error_list += [(c.getRelativeUrl(), 'VariationCategoryList inconsistency', 100, error_message)]
#
#       return error_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRootDeliveryValue')
  def getRootDeliveryValue(self):
    """
    Returns the root delivery responsible of this line
    """
    return self.getParentValue().getRootDeliveryValue()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateSimulationDeliveryProperties')
  def updateSimulationDeliveryProperties(self, movement_list = None):
    """
    Set properties delivery_ratio and delivery_error for each
    simulation movement in movement_list (all movements by default),
    according to this delivery calculated quantity
    """
    parent = self.getParentValue()
    if parent is not None:
      parent.updateSimulationDeliveryProperties(movement_list, self)

  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, item, container):
    "if the container is a line too, reindex it"
    if self.meta_type == container.meta_type:
      container.reindexObject()
    return Movement.manage_afterAdd(self, item, container)

  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, item, container):
    "if the container is a line too, reindex it"
    if self.meta_type == container.meta_type:
      container.reindexObject()
    return Movement.manage_beforeDelete(self, item, container)

# divergence support with solving

  security.declareProtected(Permissions.AccessContentsInformation, 'isDivergent')
  def isDivergent(self):
    """Returns true if the delivery line is divergent, or if any contained
    cell is divergent.
    """
    return bool(self.getDivergenceList())

  security.declareProtected(Permissions.AccessContentsInformation, 'getDivergenceList')
  def getDivergenceList(self):
    """Returns a list of messages that contains the divergences for that line
    and the cells it may contain.
    """
    if self.hasCellContent():
      divergence_list = []
      for cell in self.objectValues(portal_type=self.getPortalObject()
          .getPortalDeliveryMovementTypeList()):
        divergence_list += cell.getDivergenceList()
      return divergence_list
    else:
      return Movement.getDivergenceList(self)

  def _distributePropertyToSimulation(self, decision):
    """Distributes property from self to all related simulation movements

    AKA - accept decision"""
    for simulation_movement in self.getDeliveryRelatedValueList(
        portal_type='Simulation Movement'):
      simulation_movement.edit(**{
        decision.divergence.tested_property:
          self.getProperty(decision.divergence.tested_property)
      })

  def _updatePropertyFromSimulation(self, decision_list):
    """Update property from simulation
    'Stolen' from Products.ERP5.Document.DeliveryBuilder._solveDivergence

    Another possibility is to just simply copy properties or, in case of
    quantity, add from all simulation movements.
    """
    simulation_movement_list = self.getDeliveryRelatedValueList(
                                    portal_type="Simulation Movement")

    business_link = simulation_movement_list[0].getCausalityValue()
    delivery = self.getExplanationValue()
    delivery_portal_type = delivery.getPortalType()
    delivery_line_portal_type = self.getPortalType()
    # we need to find only one matching delivery builder
    for delivery_builder in business_link.getDeliveryBuilderValueList():
      if delivery_builder.getDeliveryPortalType() == \
           delivery_portal_type and \
         delivery_builder.getDeliveryLinePortalType() == \
           delivery_line_portal_type:
        break
    else:
      raise ValueError('No builder found')

    self.edit(quantity=0) # adoption have to 'rebuild' delivery line
    # Collect
    root_group_node = delivery_builder.collectMovement(
        simulation_movement_list)

    divergence_list = [decision.divergence for decision in decision_list]

    # Build
    portal = self.getPortalObject()
    delivery_module = getattr(portal, delivery_builder.getDeliveryModule())
    delivery_to_update_list = [delivery]
    delivery_list = delivery_builder._processDeliveryGroup(
      delivery_module,
      root_group_node,
      delivery_builder.getDeliveryMovementGroupList(),
      delivery_to_update_list=delivery_to_update_list,
      divergence_list=divergence_list,
      force_update=1)

    new_delivery_list = [x for x in delivery_list if x != delivery]
    if new_delivery_list:
      raise ValueError('No new deliveries shall be created')

    # Then, we should re-apply quantity divergence according to 'Do
    # nothing' quantity divergence list because all quantity are already
    # calculated in adopt prevision phase.
    quantity_dict = {}
    for divergence in self.getDivergenceList():
      if divergence.getProperty('divergence_scope') != 'quantity' or \
             divergence in divergence_list:
        continue
      s_m = divergence.getProperty('simulation_movement')
      delivery_movement = s_m.getDeliveryValue()
      assert delivery_movement == self
      quantity_gap = divergence.getProperty('decision_value') - \
                     divergence.getProperty('prevision_value')
      delivery_movement.setQuantity(delivery_movement.getQuantity() + \
                                    quantity_gap)
      quantity_dict[s_m] = \
          divergence.getProperty('decision_value')

    # Finally, recalculate delivery_ratio
    #
    # Here, created/updated movements are not indexed yet. So we try to
    # gather delivery relations from simulation movements.
    delivery_dict = {}
    for s_m in simulation_movement_list:
      delivery_path = s_m.getDelivery()
      delivery_dict[delivery_path] = \
                                   delivery_dict.get(delivery_path, []) + \
                                   [s_m]

    for s_m_list_per_movement in delivery_dict.values():
      total_quantity = sum([quantity_dict.get(s_m, s_m.getQuantity()) \
                            for s_m in s_m_list_per_movement])
      if total_quantity != 0.0:
        for s_m in s_m_list_per_movement:
          delivery_ratio = quantity_dict.get(s_m, s_m.getQuantity()) \
                                             / total_quantity
          s_m.edit(delivery_ratio=delivery_ratio)
      else:
        for s_m in s_m_list_per_movement:
          delivery_ratio = 1.0 / len(s_m_list_per_movement)
          s_m.edit(delivery_ratio=delivery_ratio)

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, decision_list):
    """Solves line according to decision list
    """
    simulation_tool = self.getPortalObject().portal_simulation
    solveMovement = simulation_tool.solveMovement
    # accept + split
    for decision in [q for q in decision_list if q.decision != 'adopt']:
      if decision.decision == 'accept':
        # accepting - in case of passed DeliverySolver use it, otherwise
        # simply copy values to simulation
        if not decision.delivery_solver_name:
          self._distributePropertyToSimulation(decision)
        solveMovement(self, decision.delivery_solver_name,
            decision.target_solver_name, divergence_list = [decision.divergence])
      elif decision.decision == 'split':
        solveMovement(self, decision.delivery_solver_name,
            decision.target_solver_name, **decision.split_kw)
      else: # aka - do nothing
        pass
    # adopt
    adopt_decision_list = [q for q in decision_list \
                           if q.decision == 'adopt']
    if adopt_decision_list:
      self._updatePropertyFromSimulation(adopt_decision_list)