'''Adds accounting transaction lines in an accounting transaction
and redirects to the accounting transaction view which is easier to
use.
'''
from Products.ERP5Type.Message import translateString
request = container.REQUEST

for i in range(line_count):
  context.newContent(portal_type=line_portal_type)

request.set('portal_status_message',
    translateString('Accounting Transaction Lines added.'),)
return getattr(context, form_id)()
