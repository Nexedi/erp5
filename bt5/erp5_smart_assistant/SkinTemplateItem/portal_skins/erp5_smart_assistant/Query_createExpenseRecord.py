import base64
portal = context.getPortalObject()
expense_record_module = portal.getDefaultModule('Expense Record')
sender = portal.portal_membership.getAuthenticatedMember().getUserValue()
data = bytes(context.getData())
data64 = u''.join(base64.encodebytes(data).decode().splitlines())
photo_data = u'data:%s;base64,%s' % ("image/*", data64)
expense_record_module.newContent(
  comment=comment,
  resource_title=currency,
  quantity=quantity,
  date=date,
  source_value=sender,
  photo_data=photo_data,
  portal_type='Expense Record')
