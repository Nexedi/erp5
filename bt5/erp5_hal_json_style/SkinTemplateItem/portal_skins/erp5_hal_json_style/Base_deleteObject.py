from ZODB.POSException import ConflictError

"""
some duplicated code with Folder_delete instead of modify Folder_delete
intended to make code easy understanding 
"""

portal = context.getPortalObject()


if context.isDeletable(check_relation=True):
  parent = context.getParentValue()
  try:
    if parent.portal_type != 'Preference' and \
       portal.portal_workflow.isTransitionPossible(context, 'delete'):
      portal.portal_workflow.doActionFor(context, 'delete_action')
    else:
      parent.manage_delObjects(ids= [context.getId()])
    return
  except ConflictError:
    raise
  except Exception:
    pass

request = portal.REQUEST
request.RESPONSE.setStatus(400)
form = getattr(context,form_id)
return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form')
