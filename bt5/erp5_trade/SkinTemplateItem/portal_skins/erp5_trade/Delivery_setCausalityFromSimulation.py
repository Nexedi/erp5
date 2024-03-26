"""
  Sets the causality relation on a delivery from the order it comes from.
This script should be called in the after generation script of the DeliveryBuilder.

IMPORTANT WARNING: this script will not work if your simulation movements are not
reindexed yet ()
It will also not work if strict security is set on simulation. It's recommended to use
(Delivery) Causality Movement Group as delivery level movement group in the corresponding
delivery builder.
"""
from erp5.component.module.Log import log
from Products.ERP5Type.Utils import ensure_list
LOG = lambda msg:log(
          "Delivery_setCausalityFromSimulation on %s" % context.getPath(), msg)
LOG = lambda msg:'DISABLED'

delivery = context

# get the list of simulation movement which have built this delivery
simulation_movement_list = []
for movement in delivery.getMovementList() :
  LOG("movement %s " % movement.getPath())
  simulation_movement_list.extend(
        movement.getDeliveryRelatedValueList(
          portal_type = 'Simulation Movement'))

LOG("simulation_movement_list %s " % simulation_movement_list)

causality_value_set = {}
for simulation_movement in simulation_movement_list :
  LOG("simulation_movement %s " % simulation_movement.getPath())
  if simulation_movement.getParentValue() != simulation_movement.getRootAppliedRule():
    explanation_value = simulation_movement.getParentValue().getParentValue().getExplanationValue()
  else :
    explanation_value = simulation_movement.getExplanationValue()
  if explanation_value is not None :
    causality_value_set[explanation_value] = 1

LOG('setCausalityValueList %s'%causality_value_set.keys())
delivery.setCausalityValueList(ensure_list(causality_value_set.keys()) + ensure_list(delivery.getCausalityValueList()))
