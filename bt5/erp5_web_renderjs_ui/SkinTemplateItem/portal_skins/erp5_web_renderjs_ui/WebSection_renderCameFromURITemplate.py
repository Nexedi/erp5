import re
from ZTUtils import make_query

portal = context.getPortalObject()

# XXX Hardcoded behaviour for JS app.
# Expect came_from to be an URL template
person = portal.portal_membership.getAuthenticatedMember().getUserValue()
url_parameter = "n.me"
pattern = '{[&|?]%s}' % url_parameter
if (person is None or not portal.portal_membership.checkPermission('View', person)):
  came_from = re.sub(pattern, '', came_from)
else:
  prefix = "&" if "&%s" % url_parameter in came_from else "?"
  came_from = re.sub(pattern, '%s%s' % (prefix, make_query({url_parameter: person.getRelativeUrl()})), came_from)

return came_from
