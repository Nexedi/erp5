# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.SolverMixin import SolverMixin
from erp5.component.mixin.ConfigurableMixin import ConfigurableMixin
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Message import translateString
from erp5.component.interface.ISolver import ISolver
from erp5.component.interface.IConfigurable import IConfigurable
import six

@zope.interface.implementer(ISolver,
                            IConfigurable,)
class MovementSplitSolver(SolverMixin, ConfigurableMixin, XMLObject):
  meta_type = 'ERP5 Movement Split Solver'
  portal_type = 'Movement Split Solver'
  add_permission = Permissions.AddPortalContent
  isIndexable = 0 # We do not want to fill the catalog with objects on which we need no reporting

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Arrow
                    , PropertySheet.TargetSolver
                    )

  def _solve(self, activate_kw=None):
    """
    This method splits a Delivery and move movements in to a new
    Delivery. Splitting is done by duplicating the Delivery, removing
    needless lines excess and updating related content.
    """
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      movement = simulation_movement.getDeliveryValue()
      delivery = movement.getRootDeliveryValue()
      delivery_dict.setdefault(delivery, []).append(simulation_movement)

    for delivery, split_simulation_movement_list \
        in six.iteritems(delivery_dict):
      # First, duplicate the whole delivery document including its
      # sub objects.
      old_delivery_url = delivery.getRelativeUrl()
      indexation_tag = 'MovementSplitSolver_solve_' + old_delivery_url
      applied_rule = delivery.getCausalityRelatedValue(
          portal_type='Applied Rule')
      parent = delivery.getParentValue()
      cp, = UnrestrictedMethod(lambda parent, *ids:
          parent._duplicate(parent.manage_copyObjects(ids=ids))
        )(parent, delivery.getId())
      new_delivery = parent[cp['new_id']]
      new_delivery.recursiveReindexObject(activate_kw={'tag': indexation_tag})
      new_delivery_url = new_delivery.getRelativeUrl()

      update_related_content_tag_list = [indexation_tag]

      old_simulation_movement_list = []
      new_simulation_movement_list = []

      def _isDescendant(parent, child):
        """
        /1 and /1/2 => True
        /1 and /1 => True
        /1/2 and /1 => False
        """
        return ('%s/' % child.getRelativeUrl()).startswith(
          '%s/' % parent.getRelativeUrl())

      def _delete(obj):
        parent = obj.getParentValue()
        parent.deleteContent(obj.getId())
        if len(parent) == 0 and parent != parent.getRootDeliveryValue():
          _delete(parent)  # pylint:disable=cell-var-from-loop

      for movement in delivery.getMovementList():
        simulation_movement_list = movement.getDeliveryRelatedValueList()
        old = []
        new = []
        for simulation_movement in simulation_movement_list:
          for parent in split_simulation_movement_list:
            if _isDescendant(parent, simulation_movement):
              new.append(simulation_movement)
              break
          else:
            old.append(simulation_movement)
        if len(new) == 0:
          # Case 1. the movement is only used for the old delivery.
          # * remove from the new delivery
          old_simulation_movement_list.extend(
            [x.getRelativeUrl() for x in simulation_movement_list])
          _delete(delivery.unrestrictedTraverse(
            movement.getRelativeUrl().replace(
            old_delivery_url, new_delivery_url)))
        elif len(old) == 0:
          # Case 2. the movement is only used for the new delivery.
          # * update related content on the new movement
          # * remove from the old delivery
          new_movement_url = movement.getRelativeUrl().replace(
            old_delivery_url, new_delivery_url)
          movement.updateRelatedContent(movement.getRelativeUrl(),
                                        new_movement_url)
          update_related_content_tag_list.append('%s_updateRelatedContent'
                                                 % movement.getPath())
          for simulation_movement in simulation_movement_list:
            # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
            simulation_movement.reindexObject(activate_kw={'tag': indexation_tag})
          new_simulation_movement_list.extend(
            [x.getRelativeUrl() for x in simulation_movement_list])
          _delete(movement)
        else:
          # Case 3. the movement is used for both the old and the new
          # delivery.
          # * modify 'delivery' value on simulation movements that are
          #   related to the new delivery.
          # * recalculate quantity on simulation movements
          for simulation_moment in new:
            simulation_movement.setDelivery(
              simulation_movement.getDelivery().replace(
              '%s/' % old_delivery_url, '%s/' % new_delivery_url))
            simulation_moment.reindexObjec(activate_kw={'tag': indexation_tag})
          quantity_dict = {}
          for simulation_movement in simulation_movement_list:
            delivery_movement = simulation_movement.getDeliveryValue()
            quantity_dict[delivery_movement] = \
                quantity_dict.get(delivery_movement, 0) + \
                simulation_movement.getQuantity()
          for simulation_movement in simulation_movement_list:
            delivery_movement = simulation_movement.getDeliveryValue()
            total_quantity = quantity_dict[delivery_movement]
            quantity = simulation_movement.getQuantity()
            delivery_ratio = quantity / total_quantity
            delivery_error = total_quantity * delivery_ratio - quantity
            simulation_movement.edit(delivery_ratio=delivery_ratio,
                                     delivery_error=delivery_error)
          for movement, quantity in six.iteritems(quantity_dict):
            movement.setQuantity(quantity)

      assert delivery.getMovementList() and new_delivery.getMovementList()

      # check if root applied rule exists and needs to be modified
      if applied_rule is not None:
        movement_list = [x.getRelativeUrl() for x in \
                         applied_rule.objectValues()]
        new_root_simulation_movement_list = \
            [x for x in new_simulation_movement_list if x in movement_list]
        old_root_simulation_movement_list = \
            [x for x in old_simulation_movement_list if x in movement_list]

        if len(new_root_simulation_movement_list) == 0:
          # we need to do nothing
          pass
        elif len(old_root_simulation_movement_list) == 0:
          # we need to modify the causality to the new delivery
          applied_rule.setCausality(new_delivery_url)
        else:
          # we need to split simulation movement tree
          new_applied_rule = delivery.getPortalObject().portal_simulation.newContent(
            portal_type='Applied Rule',
            specialise=applied_rule.getSpecialise(),
            causality=new_delivery_url)
          id_list = [x.rsplit('/', 1)[-1] for x in \
                     new_root_simulation_movement_list]
          cut_data = applied_rule.manage_cutObjects(id_list)
          new_applied_rule.manage_pasteObjects(cut_data)
          new_applied_rule.recursiveReindexObject(activate_kw={'tag': indexation_tag})

      # Update variation category list
      def _updateVariationCategoryList(document):
        line_dict = {}
        for movement in document.getMovementList():
          parent = movement.getParentValue()
          if getattr(parent, 'setVariationCategoryList', None) is not None:
            line_dict.setdefault(parent, []).extend(
              movement.getVariationCategoryList())
        for line, category_list in six.iteritems(line_dict):
          line.setVariationCategoryList(sorted(set(category_list)))
      _updateVariationCategoryList(delivery)
      _updateVariationCategoryList(new_delivery)

      # Set comment on old and new delivery explaining what (and when) happened
      doActionFor = delivery.getPortalObject().portal_workflow.doActionFor
      doActionFor(delivery, 'edit_action', comment=translateString(
        'Split to Delivery ${new_delivery_url}',
        mapping={'new_delivery_url':new_delivery_url}))
      doActionFor(new_delivery, 'edit_action', comment=translateString(
        'Split from Delivery ${old_delivery_url}',
        mapping={'old_delivery_url':old_delivery_url}))

      # Update causality state
      activate_kw = {'after_tag_list': update_related_content_tag_list}
      delivery.activate(**activate_kw).updateCausalityState()
      new_delivery.activate(**activate_kw).updateCausalityState()

      # Update causality values
      delivery.activate(**activate_kw).fixConsistency(
          filter={'id':'causality_validity'})
      new_delivery.activate(**activate_kw).fixConsistency(
          filter={'id':'causality_validity'})
      for related_value in delivery.getCausalityRelatedValueList():
        if related_value.getPortalType() == 'Applied Rule':
          continue
        related_value.activate(**activate_kw).fixConsistency(
            filter={'id':'causality_validity'})

    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
