vcs_tool = context.getVcsTool()
if do_extract:
  vcs_tool.extractBT(context)

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml; charset=utf-8')

root = vcs_tool.getModifiedTree(show_unmodified)
if not root:
  return '''<?xml version='1.0' encoding='UTF-8'?>
<tree id='0'></tree>'''

if REQUEST is not None: # XXX workaround to prevent zodb bloat (bt build)
  # This script is mostly used by javascript, we can abort the transaction
  import transaction
  transaction.doom()
return vcs_tool.treeToXML(root)
