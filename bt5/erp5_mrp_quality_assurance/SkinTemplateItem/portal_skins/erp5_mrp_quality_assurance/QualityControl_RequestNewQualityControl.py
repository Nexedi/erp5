clone_one = context.getFollowUpRelatedValue(portal_type='Quality Control')
if not clone_one:
  me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
  clone_one = context.Base_createCloneDocument(batch_mode=True)
  clone_one.setFollowUpValueList(clone_one.getFollowUpValueList(portal_type='Manufacturing Execution') + [context])
  clone_one.setDestinationDecisionValue(None)

  clone_line = me_line.Base_createCloneDocument(batch_mode=True)
  clone_line.setAggregateValue(clone_one)

  clone_one.plan()
  clone_one.confirm()

if batch:
  return clone_one

return clone_one.Base_redirect('view', keep_items={"portal_status_message":context.Base_translateString("New Quality Control is created")})
