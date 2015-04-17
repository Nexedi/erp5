if REQUEST is not None and 0:
  from zExceptions import Unauthorized
  raise Unauthorized(script.id)
from Products.ERP5Type.Message import translateString

if context.getSimulationState() == "draft":
  context.plan(comment=translateString('Initialised by Delivery Builder.'))
if context.getSimulationState() == "planned":
  # Make sure that we are not going to receive more lines later, this could
  # happen if global builder took only partially the movement of an applied
  # rule.
  # We assume here that a Delivery is not going to receive movements from
  # different applied rules.
  # To check if we are not going to receive more simulation movement, we check
  # for all simulation movement of the same level as the simulation movement
  # used to construct this current delivery have all a delivery link.
  # If there is more than one packing list, do not confirm because it might mean
  # that we are in a split, so if the user splits again we want to also recieve
  # the movements of further splits.
  movement_list = context.getMovementList()
  assert len(movement_list) > 0
  simulation_movement = movement_list[0].getDeliveryRelatedValue(portal_type="Simulation Movement")
  getSpecialise = simulation_movement.getParentValue().getSpecialise()
  root_applied_rule = simulation_movement.getRootAppliedRule()
 
  def getSimilarSimulationMovementList(simulation_object):
    current_list = []
    if simulation_object.getPortalType() == "Applied Rule" and \
         simulation_object.getSpecialise() == getSpecialise:
      current_list.extend([x for x in simulation_object.objectValues()])
    else:
      for sub_simulation_object in simulation_object.objectValues():
        current_list.extend(getSimilarSimulationMovementList(sub_simulation_object))
    return current_list
 
  is_complete = True
  packing_list_set = set()
  for simulation_movement in getSimilarSimulationMovementList(root_applied_rule):
    delivery = simulation_movement.getDeliveryValue()
    if delivery is None:
      is_complete = False
      break
    packing_list_set.add(delivery.getRootDeliveryValue())
  if is_complete and len(packing_list_set) == 1:
    context.confirm(comment=translateString('Initialised by Delivery Builder.'))
