source_trade = context.getSourceTrade()
if source_trade is None or context.getSimulationState() != 'delivered':
  user_id = context.Base_getLastUserIdByTransition(workflow_id='check_payment_workflow', transition_id='deliver_action')
  if user_id is not None:
    site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
    source = context.getSource()
    for site in site_list:
      site_value = context.portal_categories.getCategoryValue(site)
      if site_value.getVaultType().endswith('guichet') and source in site:
        source_trade = site + '/encaisse_des_billets_et_monnaies/sortante'
        # Save it only once we are sure that the document will not change any more
        # and that we will not have many users trying to do deliver_action
        if context.getSourceTrade() != source_trade:
          context.setSourceTrade(source_trade)
return source_trade
