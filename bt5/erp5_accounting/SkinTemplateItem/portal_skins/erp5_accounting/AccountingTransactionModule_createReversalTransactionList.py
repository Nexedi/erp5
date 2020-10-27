from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
countMessage = portal.portal_activities.countMessage

portal.portal_selections.updateSelectionCheckedUidList(selection_name, listbox_uid, uids)
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(
                                                       selection_name)
if selection_uid_list:
  object_list = [brain.getObject() for brain in portal.portal_catalog(uid=selection_uid_list)]
else:
  object_list = portal.portal_selections.callSelectionFor(selection_name)

# XXX prevent to call this on the whole module:
if len(object_list) >= 1000:
  return context.Base_redirect(form_id,
    keep_items=dict(
        portal_status_message=translateString('Refusing to process more than 1000 objects, check your selection.'),
        portal_status_level='error',
    ))

tag = 'reversal_creation_%s' % random.randint(0, 1000)
activated = 0
for obj in object_list:
  obj = obj.getObject()
  if countMessage(path=obj.getPath(),
                  method_id='AccountingTransaction_createReversalTransaction'):
    return context.Base_redirect(form_id,
      abort_transaction=True,
      keep_items={
        "portal_status_message": translateString('Reversal creation already in progress, abandon.'),
        "portal_status_level": 'error'
      })
  obj.activate(tag=tag).AccountingTransaction_createReversalTransaction(
                                cancellation_amount=cancellation_amount,
                                date=date,
                                plan=plan)
  activated += 1

if not activated:
  return context.Base_redirect(
      form_id,
      keep_items=dict(
          portal_status_message=translateString('No valid transaction in your selection.'),
          portal_status_level='error',
      ))

# activate something on the folder
context.activate(after_tag=tag).getTitle()

return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=
        translateString(
          'Reversal creation for ${activated_transaction_count} on'
          ' ${total_selection_count} transactions in progress.',
          mapping=dict(activated_transaction_count=activated,
                       total_selection_count=len(object_list)))))
