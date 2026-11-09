portal = context.getPortalObject()

account_uid_list = dict()
account_list = [("", None)]
result_list = portal.portal_catalog(
  portal_type="Purchase Invoice Transaction Line",
  simulation_state=context.getPortalAccountedTransactionStateList(),
  select_list=("stock.node_uid",),
  mirror_section_uid=context.getSourceSectionUid(),
  quantity={
    "query": (0.0,),
    "range": "min",
  }
)

for result in result_list:
  if result["node_uid"] not in account_uid_list:
    account_uid_list[result["node_uid"]] = 0
  account_uid_list[result["node_uid"]] = account_uid_list[result["node_uid"]] + 1

for (account_uid, _) in sorted(account_uid_list.items(), key=lambda item: -item[1]):
  account = portal.portal_catalog(
    uid=account_uid,
    limit=2,
  )[0].getObject()
  account_list.append((account.Account_getFormattedTitle(), account_uid))

return account_list
