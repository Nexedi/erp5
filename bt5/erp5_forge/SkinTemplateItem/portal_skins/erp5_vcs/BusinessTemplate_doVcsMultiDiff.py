# XXX: This does not show anything for folders.
#      A recursive diff should be displayed instead.
# XXX: Consider merging BusinessTemplate_{do,view}VcsMultiDiff
# TODO: handle Svn SSL/login exceptions, preferably reusing vcs_dialog(_error)
# TODO: Git support

from erp5.component.module.DiffUtils import DiffFile

request = context.REQUEST
try:
  revision_list = [uid.split('.', 1) for uid in request['uids']]
  revision_list.sort()
  rev2, rev1 = revision_list
except (KeyError, ValueError):
  request.set('portal_status_message', 'You must select TWO revisions.')
  return context.BusinessTemplate_viewVcsLogDialog()

vcs_tool = context.getVcsTool()
diff = vcs_tool.getHeader(added)
diff += '<hr/>'
diff += DiffFile(vcs_tool.diff(added, revision1=rev1[1], revision2=rev2[1])).toHTML()
return context.asContext(diff=diff).BusinessTemplate_viewVcsMultiDiff()
