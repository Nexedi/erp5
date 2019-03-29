source = context.getSource()
if source is not None:
  return source
# calculate the source
# must use owner to know site letter
site_list = context.Baobab_getUserAssignedSiteList(user_id=context.Base_getOwnerId())
for site in site_list:
  if context.portal_categories.getCategoryValue(site).getVaultType().endswith('/guichet'):
    return site
from Products.ERP5Type.Message import Message
message = Message(domain="ui", message="Object owner is not assigned to a counter.")
raise ValueError(message)
