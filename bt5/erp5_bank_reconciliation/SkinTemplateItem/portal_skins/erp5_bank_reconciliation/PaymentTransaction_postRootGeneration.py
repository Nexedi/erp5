"""
Tries to set aggregate on bank lines when possible. If any issue is
encountered, nothing is set, and reconciliation of the line must be done
manually.

XXX-Titouan: I do not really like this script, which I feel is doing
something simulation could do, but the constraint is: we use aggregate
for matching, and we do not want to set aggregate on both lines.
"""

title = None

for accounting_line_value in context.objectValues():
  simulation_movement_value = accounting_line_value.getDeliveryRelatedValue(portal_type="Simulation Movement")
  trade_model_path_list = simulation_movement_value.getCausalityValueList(portal_type="Trade Model Path")
  if len(trade_model_path_list) == 1:
    if trade_model_path_list[0].getEfficiency() < 0.0 and simulation_movement_value.getAggregate():
      accounting_line_value.setAggregate(simulation_movement_value.getAggregate())
      #accounting_line_value.setId("bank")
      title = simulation_movement_value.getAggregateValue().getTitle()

if title is not None:
  context.setTitle(title)

context.PaymentTransaction_postGeneration(**kw)
