"""This script generates a domain containing only the current document.
This is usefull for planning box, where a domain is always required.

It's not supposed to be used directly, but wrapped in another script that will pass those parameters:
 * script_id: the ID of the wrapper script (subdomains will be regenerated with this script);
 * membership_criterion_base_category: base categories that will be set on generated domains.
"""

if depth != 0:
  return []

domain_list = []
portal = context.getPortalObject()
request = portal.REQUEST
here = request.get('here', None)
if here is None:
  # Sometimes the object is not in the request, when you edit for example.
  here = request['PUBLISHED'].aq_parent

for category in (here, ):
  domain = parent.generateTempDomain(id=category.getId())
  domain.edit(title=category.getTitle(),
              membership_criterion_base_category=membership_criterion_base_category,
              membership_criterion_category=(category.getRelativeUrl(),),
              domain_generator_method_id=script_id,
              uid=category.getUid())

  domain_list.append(domain)

return domain_list
