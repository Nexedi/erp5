# try to get the repository URL, else redirect to the dialog for creating a working copy in one of the configured repositories
from erp5.component.module.WorkingCopy import NotAWorkingCopyError
try:
  return context.getVcsTool().getRemoteUrl()
except NotAWorkingCopyError:
  from ZTUtils import make_query
  from zExceptions import Redirect
  dialog = context.BusinessTemplate_viewCreateWorkingCopy
  context_url = context.absolute_url_path()
  query_string = make_query(
    cancel_url=context_url,
    portal_status_message=dialog.description
  )
  raise Redirect("%s/%s?%s" % (context_url, dialog.getId(), query_string))
