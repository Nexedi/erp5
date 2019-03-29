source_trade = context.getSourceTrade()
if source_trade is None or context.getSimulationState() != 'delivered':
  destination = context.getDestination()
  if destination is None:
    return None
  user_id = context.Base_getLastUserIdByTransition(workflow_id='money_deposit_workflow', transition_id='deliver_action')
  if user_id is None:
    return None
  site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
  for site in site_list:
    if context.portal_categories.getCategoryValue(site).getVaultType().endswith('guichet') and destination in site:
      source_trade = site + '/encaisse_des_billets_et_monnaies/entrante'
      if context.getSourceTrade() != source_trade:
        context.setSourceTrade(source_trade)
      return source_trade
  from Products.ERP5Type.Message import Message
  message = Message(domain="ui", message="The owner is not assigned to the right vault.")
  raise ValueError(message)
else:
  return source_trade
