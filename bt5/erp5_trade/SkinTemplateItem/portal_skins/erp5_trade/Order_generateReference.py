"""
This script is called to generate references for all order lines
and milestones.
"""

translateString = context.Base_translateString
if not reference:
  reference='SO'

def generateReference(prefix, order, portal_type):
  for order_line in order.contentValues(portal_type=portal_type):
    new_prefix = "%s-%s" % (prefix, order_line.getIntIndex(order_line.getId()))
    generateReference(new_prefix, order_line, portal_type)
    order_line.setReference(new_prefix)

generateReference(reference, context, "%s Line" % context.getPortalType())
generateReference('%s-M' % reference, context, "%s Milestone" % context.getPortalType())

msg = translateString('Reference generated for all order lines and milestones.')

# Return to view mode
kw['keep_items'] = {'portal_status_message' : msg}
return context.Base_redirect(form_id, **kw)
