from Products.ERP5Type.Message import translateString
from zExceptions import Redirect
portal = context.getPortalObject()
stool = portal.portal_selections
countMessage = portal.portal_activities.countMessage

stool.updateSelectionCheckedUidList(selection_name, listbox_uid, uids)
selection_uid_list = context.portal_selections.getSelectionCheckedUidsFor(
                                                       selection_name)
if selection_uid_list:
  object_list = [brain.getObject() for brain in portal.portal_catalog(uid=selection_uid_list)]
else:
  object_list = stool.callSelectionFor(selection_name)

# XXX prevent to call this on the whole module:
if len(object_list) >= 1000:
  return context.Base_redirect(form_id,
    keep_items=dict(portal_status_message=
        translateString(
         'Refusing to process more than 1000 objects, check your selection.')))

tag = 'reversal_creation_%s' % random.randint(0, 1000)
activated = 0
for obj in object_list:
  obj = obj.getObject()
  if countMessage(path=obj.getPath(),
                  method_id='AccountingTransaction_createReversalTransaction'):
    raise Redirect, "%s/view?portal_status_message=%s" % (
              context.absolute_url(), translateString(
      'Reversal creation already in progress, abandon.'))
  obj.activate(tag=tag).AccountingTransaction_createReversalTransaction(
                                cancellation_amount=cancellation_amount,
                                date=date,
                                plan=plan)
  activated += 1

if not activated:
  return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=
          translateString('No valid transaction in your selection.')))

# activate something on the folder
context.activate(after_tag=tag).getTitle()

return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=
        translateString(
          'Reversal creation for ${activated_transaction_count} on'
          ' ${total_selection_count} transactions in progress.',
          mapping=dict(activated_transaction_count=activated,
                       total_selection_count=len(object_list)))))
