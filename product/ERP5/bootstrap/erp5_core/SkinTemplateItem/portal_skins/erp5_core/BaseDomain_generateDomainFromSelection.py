"""This script generates a domain from selected objects in a module.

It's not supposed to be used directly, but wrapped in another script that will pass those parameters:
 * script_id: the ID of the wrapper script (subdomains will be regenerated with this script);
 * selection_name: the selection name used by the listbox;
 * membership_criterion_base_category: base categories that will be set on generated domains.
"""

if depth != 0:
  return []

domain_list = []
portal = context.getPortalObject()
category_list = portal.portal_selections.getSelectionCheckedValueList(selection_name)
if not category_list:
  category_list = portal.portal_selections.callSelectionFor(selection_name)

for category in category_list:
  domain = parent.generateTempDomain(id=category.getId())
  domain.edit(title=category.getTitle(),
              membership_criterion_base_category=membership_criterion_base_category,
              membership_criterion_category=(category.getRelativeUrl(),),
              domain_generator_method_id=script_id,
              uid=category.getUid())

  domain_list.append(domain)

return domain_list
