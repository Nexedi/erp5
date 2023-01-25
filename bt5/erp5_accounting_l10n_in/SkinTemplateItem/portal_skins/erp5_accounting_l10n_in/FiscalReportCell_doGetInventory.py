"""
  This scripts add the balance of every gap account in the list 'accounts'
  it use portal_simulation.getInventoryAssetPrice.
  The following REQUEST keys are mandatory :
      at_date

  those are optional :
      gap_base
      simulation_state
      section_category

  those are ignored from the request and should explicitely passed as keywords args to this script :
      from_date

  parameters keywords to this script overrides REQUEST keys

"""

def shortAccountNameToFullGapCategory(accountName) :
  """ translates a short account name (eg asset/current_assets) to a full gap category url
    (eg gap/in/sme1/asset/current_assets) """
  accountName = accountName.strip()
  gap = request.get("gap_base", "gap/in/sme1")
  if gap[-1] == '/':
    gap = gap[:-1]
  return gap+'/'+accountName


request = context.REQUEST
kw = {}
kw['omit_simulation']   = 1
kw["simulation_state"]  = request.get("simulation_state", ['confirmed','stopped', 'delivered'])
kw["section_uid"]       = context.restrictedTraverse(request.get("organisation")).getUid()
kw["at_date"]           = request['at_date']
kw.update(params_kw)

sum = 0

for account in accounts :
  kw["node_category"] = shortAccountNameToFullGapCategory(account)

  # checks the node category exists
  if context.restrictedTraverse('portal_categories/%s' % kw["node_category"], None) is not None :
    val = (context.portal_simulation.getInventoryAssetPrice(**kw) or 0)
    sum += val
context.log('sum',str(sum))
return float ("%.2f"%(sum))
# vim: syntax=python
