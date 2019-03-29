from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

if simulation_state_list is None:
  simulation_state_list = ['open']

site = context.Baobab_getVaultSite(counter)
counter_list = [x.getObject() for x in context.portal_catalog(portal_type="Counter", 
         simulation_state = simulation_state_list, default_site_uid = site.getUid())]
if same_type(counter, 'a'):
  counter_relative_url = counter
else:
  counter_relative_url = counter.getRelativeUrl()
found = 0
#if "guichet" in counter_relative_url:
for counter_ob in counter_list:
  if "site/%s" %counter_ob.getSite() in counter_relative_url or counter_relative_url in "site/%s" %counter_ob.getSite():
    found = 1
if found == 0:
  msg = Message(domain = "ui", message="Counter is not opened")
  raise ValidationFailed(msg,)
