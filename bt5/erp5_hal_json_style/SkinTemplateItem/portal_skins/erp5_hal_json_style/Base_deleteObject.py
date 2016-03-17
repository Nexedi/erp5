from ZODB.POSException import ConflictError

"""
some duplicated code with Folder_delete instead of modify Folder_delete
intended to make code easy understanding 
"""

portal = context.getPortalObject()
request=container.REQUEST

def errorHandler():
  request.RESPONSE.setStatus(400)
  form = getattr(context,form_id)
  return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form')
  

if context.isDeletable(check_relation=True):
  if portal.portal_workflow.isTransitionPossible(context, 'delete'):
    try:
      portal.portal_workflow.doActionFor(context, 'delete_action')
    except ConflictError:
      return errorHandler()
    except Exception:
      pass
  else:
    try:
      context.getParentValue().manage_delObjects(
        ids= [context.getId()])
    except ConflictError:
      return errorHandler()
    except Exception:
      pass

else:
  return errorHandler()
