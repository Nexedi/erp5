organisation_id = context.restrictedTraverse(request['organisation']).getUid()
account = context.portal_categories.restrictedTraverse('account_module/'+account_name)

extstr = ''
if column == 2:
  extstr='2'

return context.portal_simulation.getInventory(
node_uid = account.getUid(),
section_id = organisation_id,
at_date=request['at_date'+extstr],
from_date=request['from_date'+extstr])
