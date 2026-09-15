"""Answer the total of the tokens of one Artificial Task Report.

The script reads every Artificial Task Report Line of this report. The
script adds the quantity of one line when two conditions are true. The
first condition is the quantity unit `unit/token`. The second condition
is the simulation state `stopped`.

A line that is not `stopped` holds no final token count. A line with
another quantity unit holds no token count. The script skips both.

The script answers one float. The script answers 0.0 when no line
matches.

PARAMETER LIST: empty. This script takes no parameter.
"""
TOKEN_QUANTITY_UNIT = 'unit/token'
LINE_PORTAL_TYPE = 'Artificial Task Report Line'
FINAL_SIMULATION_STATE = 'stopped'

total = 0.0
for line in context.contentValues(portal_type=LINE_PORTAL_TYPE):
  if line.getSimulationState() != FINAL_SIMULATION_STATE:
    continue
  if line.getQuantityUnit() != TOKEN_QUANTITY_UNIT:
    continue
  quantity = line.getQuantity()
  if quantity:
    total = total + float(quantity)

return total
