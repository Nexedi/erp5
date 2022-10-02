vcs_tool = context.getVcsTool()
template_tool = context.getPortalObject().portal_templates
if template_tool.getDiffFilterScriptList():
  DiffFile = template_tool.getFilteredDiff
else:
  from erp5.component.module.DiffUtils import DiffFile

print('<div style="color: black">')

# XXX: ERP5VCS_doCreateJavaScriptStatus should send lists
from six import string_types as basestring
if isinstance(added, basestring):
  added = added != 'none' and filter(None, added.split(',')) or ()
if isinstance(modified, basestring):
  modified = modified != 'none' and filter(None, modified.split(',')) or ''
if isinstance(removed, basestring):
  removed = removed != 'none' and filter(None, removed.split(',')) or ()

for f in modified:
  diff = DiffFile(vcs_tool.diff(f))
  if not diff:
    continue
  print('<input name="modified" value="%s" type="checkbox" checked="checked" />'% f)
  print(vcs_tool.getHeader(f))
  print(diff.toHTML())
  print("<hr/><br/>")

for f in added:
  print('<input name="added" value="%s" type="checkbox" checked="checked" />'% f)
  print(vcs_tool.getHeader(f))
  print("<br/><span style='color: green;'>File Added</span><br/><br/><hr/><br/>")

for f in removed:
  print('<input name="removed" value="%s" type="checkbox" checked="checked" />'% f)
  print(vcs_tool.getHeader(f))
  print("<br/><span style='color: red;'>File Removed</span><br/><br/><hr/><br/>")

print('</div>')
return printed
