"""
  This script adds bank accounts balances, only if they are debtors
"""

request = context.REQUEST
portal = context.getPortalObject()

kw = dict(kwd)
kw['simulation_state'] = kwd.get('simulation_state', request.get('simulation_state'))
kw["section_category"] = kwd.get('section_category', request.get('section_category'))
at_date = kwd.get('at_date', request['at_date'])
kw['at_date'] = at_date.latestTime()

if request.get('account_id_list_conversion_script_id'):
  account_id_list_conversion_script = getattr(portal, request['account_id_list_conversion_script_id'])
  kw['node_category'] = account_id_list_conversion_script(account_id_list)
else:
  kw['node_category'] = account_id_list

sum_ = 0.0
for inventory in portal.portal_simulation.getInventoryList(
                                    group_by_payment=1,
                                    group_by_node=1,
                                    **kw):
  if inventory.total_price > 0:
    sum_ += inventory.total_price
return sum_
