"""
  This scripts add the balance of every gap account in the list 'accounts'
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

request = context.REQUEST
kw = {}
kw['omit_simulation']   = 1
kw['omit_input']=1
kw["simulation_state"]  = request.get("simulation_state", ['stopped', 'delivered'])
#kw["section_uid"]     = context.restrictedTraverse(request.get("organisation")).getUid()
kw["at_date"]           = request['at_date']
kw["from_date"]         = request['from_date']
kw.update(params_kw)


sum = 0

for account in accounts :
  kw['node_category']= context.shortAccountNumberToFullGapCategory(account, **kw)
  #context.log('KW for getInventory',kw)
  try :
    #val = (context.portal_simulation.getInventory(**kw) or 0)
    val = (context.portal_simulation.getInventoryAssetPrice(**kw) or 0)
    sum += val
  except KeyError : # unknown gap account (i.e. not a category)
    pass
  except AttributeError: # no account of this gap nr has been set up
    return 0
#  except :
#    raise 'error on', (account, shortAccountNumberToFullGapCategory(account))
return float ("%.2f"%(sum))
