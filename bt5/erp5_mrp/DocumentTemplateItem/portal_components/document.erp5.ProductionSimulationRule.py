from Products.ERP5.Document.DeliverySimulationRule import DeliverySimulationRule
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin

class ProductionSimulationRule(DeliverySimulationRule):
  """
  Create own rule to define the transformation that will be used on production order.
  """

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return DeliveryRuleMovementGenerator(applied_rule=context, rule=self)

class DeliveryRuleMovementGenerator(MovementGeneratorMixin):

  def _getUpdatePropertyDict(self, input_movement):
    # Override default mixin implementation
    return {'order': None,
            'delivery': None,}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    parent_simulation_movement = self._applied_rule.getParentValue().asContext()
    resource_value = parent_simulation_movement.getResourceValue()
    transformation_list = self._applied_rule.getPortalObject().portal_catalog(
                               portal_type="Transformation",
                               default_resource_uid=resource_value.getUid(),
                               validation_state="validated")
    if len(transformation_list) > 0:
      parent_simulation_movement.setSpecialiseValue(transformation_list[0].getObject(),
                                                    portal_type="Transformation")
    # We must always produce positive quantities, this is needed to produce
    # resources consumed by transformation (when this rule is below a transformation rule)
    if parent_simulation_movement.getQuantity() < 0:
      parent_simulation_movement.setQuantity(-parent_simulation_movement.getQuantity())
    return [parent_simulation_movement]