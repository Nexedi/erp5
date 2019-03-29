from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed
site = vault
if same_type(site, ''):
  if site.startswith('site/'):
    site = site[len('site/'):]
  site = context.restrictedTraverse('portal_categories/site/%s' %(site,))

while True:
  if not hasattr(site, 'getVaultTypeList'):
    context.log('no getVaultTypeList on :', site.getRelativeUrl())
    msg = Message(domain = 'ui', message = 'The site value is misconfigured; report this to system administrators.')
    raise ValidationFailed(msg,)
  if 'site' in site.getVaultTypeList():
    break
  site = site.getParentValue()
return site
