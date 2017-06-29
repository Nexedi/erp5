from Products.ERP5Type.Message import translateString
from zExceptions import Redirect

portal = context.getPortalObject()
stool = portal.portal_selections
getObject = portal.portal_catalog.getObject
countMessage = portal.portal_activities.countMessage
invoice_type_list = portal.getPortalInvoiceTypeList()

stool.updateSelectionCheckedUidList(selection_name, listbox_uid, uids)
selection_uid_list = context.portal_selections.getSelectionCheckedUidsFor(
                                                       selection_name)
if selection_uid_list:
  object_list = [getObject(uid) for uid in selection_uid_list]
else:
  object_list = stool.callSelectionFor(selection_name)

# update selection params, because it'll be used in the selection dialog.
stool.setSelectionParamsFor('accounting_create_related_payment_selection',
          params=dict(node_for_related_payment=node,
                      payment_mode_for_related_payment=payment_mode,
                      payment_for_related_payment=payment))

# XXX prevent to call this on the whole module:
if len(object_list) >= 1000:
  return context.REQUEST.RESPONSE.redirect(
    "%s/view?portal_status_message=%s" % (
        context.absolute_url(), translateString(
         'Refusing to process more than 1000 objects, check your selection.')))

tag = 'payment_creation_%s' % random.randint(0, 1000)
activated = 0
for obj in object_list:
  if obj.portal_type in invoice_type_list:
    obj = obj.getObject()
    if countMessage(path=obj.getPath(),
                    method_id='Invoice_createRelatedPaymentTransaction'):
      raise Redirect, "%s/view?portal_status_message=%s" % (
                context.absolute_url(), translateString(
        'Payment creation already in progress, abandon.'))
    obj.activate(tag=tag).Invoice_createRelatedPaymentTransaction(
                                                  node=node,
                                                  payment_mode=payment_mode,
                                                  payment=payment,
                                                  batch_mode=1)
    activated += 1

if not activated:
  return context.REQUEST.RESPONSE.redirect(
    "%s/view?portal_status_message=%s" % (
        context.absolute_url(), translateString('No invoice in your selection.')))

# activate something on the folder
context.activate(after_tag=tag).getTitle()

return context.REQUEST.RESPONSE.redirect(
    "%s/view?portal_status_message=%s" % (
        context.absolute_url(), translateString(
          'Payments creation for ${activated_invoice_count} on'
          ' ${total_selection_count} invoices in progress.',
          mapping=dict(activated_invoice_count=activated,
                       total_selection_count=len(object_list)))))
