from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
countMessage = portal.portal_activities.countMessage
invoice_type_list = portal.getPortalInvoiceTypeList()

portal.portal_selections.updateSelectionCheckedUidList(selection_name, listbox_uid, uids)
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(
                                                       selection_name)
if selection_uid_list:
  object_list = [brain.getObject() for brain in portal.portal_catalog(uid=selection_uid_list)]
else:
  object_list = portal.portal_selections.callSelectionFor(selection_name)

# update selection params, because it'll be used in the selection dialog.
portal.portal_selections.setSelectionParamsFor('accounting_create_related_payment_selection',
          params=dict(node_for_related_payment=node,
                      payment_mode_for_related_payment=payment_mode,
                      payment_for_related_payment=payment))

# XXX prevent to call this on the whole module:
if len(object_list) >= 1000:
  return context.Base_redirect(
      form_id,
      keep_items={
        'portal_status_message': translateString(
            'Refusing to process more than 1000 objects, check your selection.'),
        'portal_status_level': 'error',
      })

tag = 'payment_creation_%s' % random.randint(0, 1000)
activated = 0
for obj in object_list:
  if obj.portal_type in invoice_type_list:
    obj = obj.getObject()
    if countMessage(path=obj.getPath(),
                    method_id='Invoice_createRelatedPaymentTransaction'):
      return context.Base_redirect(
          form_id,
          abort_transaction=True,
          keep_items={
            'portal_status_message': translateString('Payment creation already in progress, abandon.'),
            'portal_status_level': 'error',
          })
    obj.activate(tag=tag).Invoice_createRelatedPaymentTransaction(
                                                  node=node,
                                                  payment_mode=payment_mode,
                                                  payment=payment,
                                                  batch_mode=1)
    activated += 1

if not activated:
  return context.Base_redirect(
      form_id,
      keep_items={
        'portal_status_message': translateString( 'No invoice in your selection.'),
        'portal_status_level': 'error',
      })

# activate something on the folder
context.activate(after_tag=tag).getTitle()

return context.Base_redirect(
    form_id,
    keep_items={'portal_status_message': translateString(
        'Payments creation for ${activated_invoice_count} on'
        ' ${total_selection_count} invoices in progress.',
        mapping={'activated_invoice_count': activated,
                 'total_selection_count': len(object_list)})})
