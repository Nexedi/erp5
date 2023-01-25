"""
  This scripts add the balance of every gap account in the list 'account_id_list'
  it use portal_simulation.getInventory.

  The following REQUEST keys are mandatory :
      at_date

  those are optional :
      gap_base
      simulation_state
      resource
      section_category

  those are ignored from the request and should explicitely passed as keywords args to this script :
      from_date

  parameters keywords to this script overrides REQUEST keys

"""
portal = context.getPortalObject()
request = context.REQUEST

kw = dict(kwd)
kw['simulation_state'] = kwd.get('simulation_state', request.get('simulation_state'))
kw["section_category"] = kwd.get('section_category', request.get('section_category'))
kw["at_date"] = request['at_date'].latestTime()
at_date = kwd.get('at_date', request['at_date'])
kw['at_date'] = at_date.latestTime()

if request.get('account_id_list_conversion_script_id'):
  account_id_list_conversion_script = getattr(portal, request['account_id_list_conversion_script_id'])
  kw['node_category'] = account_id_list_conversion_script(account_id_list)
else:
  kw['node_category'] = account_id_list

context.log(kw)

return portal.portal_simulation.getInventoryAssetPrice(**kw) or 0.0
