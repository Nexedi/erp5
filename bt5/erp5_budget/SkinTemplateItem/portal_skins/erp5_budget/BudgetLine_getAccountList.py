account_list = [a.getObject() for a in context.getPortalObject().account_module.searchFolder(
               validation_state='validated')]

account_list.sort(key=lambda account: account.Account_getFormattedTitle())
return account_list
