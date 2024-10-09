import six
if six.PY2:
  from base64 import encodestring as encodebytes
else:
  from base64 import encodebytes
from Products.ERP5Type.Utils import bytes2str

portal = context.getPortalObject()
expense_record_module = portal.getDefaultModule('Expense Record')
sender = portal.portal_membership.getAuthenticatedMember().getUserValue()
data = bytes(context.getData())
data64 = ''.join(bytes2str(encodebytes(data)).splitlines())
photo_data = 'data:%s;base64,%s' % ("image/*", data64)
expense_record_module.newContent(
  comment=comment,
  resource_title=currency,
  quantity=quantity,
  date=date,
  source_value=sender,
  photo_data=photo_data,
  portal_type='Expense Record')
