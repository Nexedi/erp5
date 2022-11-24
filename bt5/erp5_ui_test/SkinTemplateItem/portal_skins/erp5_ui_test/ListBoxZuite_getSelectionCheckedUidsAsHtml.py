"""This scripts prints a table of all checked uids as html.
The title of the html is in the form "len(checked_uids) == %d"
The body contains some /table/tr with td[0] for uid and td[1] for id
"""

if selection_name is None:
  return "selection_name parameter not passed"

portal = context.getPortalObject()
checked_uids = portal.portal_selections\
                    .getSelectionCheckedUidsFor(selection_name)
getObj = portal.portal_catalog.getObject
checked_uids_objs = [getObj(uid) for uid in checked_uids]
checked_uids_objs.sort(key=lambda x:x.getId())

# we produce html for easier Selenium parsing
table = "\n".join(["<tr><td>%s</td><td>%s</td></tr>" % (
                    x.getUid(), x.getId()) for x in checked_uids_objs])
container.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
return """<html>
<head><title>len(checked_uids) == %d</title></head>
<body>
<table>
  %s
</table>
</body>
</html>""" % (len(checked_uids), table)
