from DateTime import DateTime
import json
now = DateTime()

portal = context.getPortalObject()

translateString = portal.Base_translateString

if not portal.portal_membership.checkPermission('Modify portal content', context):
  result_dict = {
    'portal_status_message': translateString("No Permission"),
    'portal_status_level': 'error'
  }
  if batch or fast_post:
    return json.dumps(result_dict)
  return context.Base_redirect('view', keep_items = result_dict)


if not portal.portal_workflow.isTransitionPossible(context, 'post'):
  result_dict = {
    'portal_status_message': translateString("Quality Control is already in ${state} state", mapping={"state": context.getValidationState()}),
    'portal_status_level': 'error'
  }
  if batch or fast_post:
    return json.dumps(result_dict)
  return context.Base_redirect('view', keep_items = result_dict)

user_value = portal.portal_membership.getAuthenticatedMember().getUserValue()


if result == 'ok':
  context.edit(
    destination_decision_value = user_value,
    quality_assurance = "result/ok",
    effective_date = now
  )
elif result == 'nok':
  if fast_post:
    return json.dumps({
      'portal_status_message': translateString("Only OK is allowed"),
      'portal_status_level': 'error'
    })
  if not context.getCausalityRelatedValue(portal_type='Defect Item') and redirect_to_defect_dialog:
    return context.Base_redirect(form_id = 'declare_defect', keep_items={
      'post_quality_control': True,
      "portal_status_message":context.Base_translateString("Defect needs to be input firstly for NOK Quality Control"),
      'portal_status_level': 'error'
    })

  clone_one = context.Base_createCloneDocument(batch_mode=True)
  clone_one.setFollowUpValueList(clone_one.getFollowUpValueList(portal_type='Manufacturing Execution') + [context])
  clone_one.setDestinationDecisionValue(None)

  me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
  clone_line = me_line.Base_createCloneDocument(batch_mode=True)
  clone_line.setAggregateValue(clone_one)


  clone_one.plan()
  clone_one.confirm()
  clone_one.pending()
  context.edit(
    destination_decision_value = user_value,
    quality_assurance = "result/nok",
    effective_date = now
  )
else:
  result_dict = {
    'portal_status_message': translateString("Unknown Value: ${result}", mapping = {'result': result}),
    'portal_status_level': 'error'
  }
  if batch or fast_post:
    return json.dumps(result_dict)
  return context.Base_redirect('view', keep_items = result_dict)

me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
if me_line:
  me_line.edit(
    start_date = now,
    stop_date = now
  )
context.post()

if batch or fast_post:
  return json.dumps({
    'portal_status_message': 'OK',
    'portal_status_level': 'success'
  })

ME = context.getCausalityValue(portal_type='Manufacturing Execution')
if ME.getSimulationState() != 'delivered':
  return ME.Base_redirect(
    'view',
    keep_items={
      "portal_status_message":context.Base_translateString("Result is posted for ${title}", mapping={"title": context.getTitle()})
    })

po = ME.getCausalityValue(portal_type='Production Order')
ppl = po.getCausalityRelatedValue(portal_type='Production Packing List')
return ppl.Base_redirect(
  'view',
  keep_items={
    "portal_status_message":context.Base_translateString("Result is posted for ${title}", mapping={"title": context.getTitle()})
  })
