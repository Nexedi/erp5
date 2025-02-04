gate = state_change['object']

me = gate.getCausalityValue(portal_type='Manufacturing Execution')

if me:
  gate.Base_showNextStepQualityOperation(me)
