
import six
# pylint:disable=no-name-in-module
if six.PY2:
  from base64 import encodestring as encodebytes
else:
  from base64 import encodebytes
# pylint:enable=no-name-in-module

portal = context.getPortalObject()
expense_record_module = portal.getDefaultModule('Expense Record')
sender = portal.portal_membership.getAuthenticatedMember().getUserValue()
data = bytes(context.getData())
data64 = ''.join(encodebytes(data).decode().splitlines())
photo_data = 'data:%s;base64,%s' % ("image/*", data64)
expense_record_module.newContent(
  comment=comment,
  resource_title=currency,
  quantity=quantity,
  date=date,
  source_value=sender,
  photo_data=photo_data,
  portal_type='Expense Record')
