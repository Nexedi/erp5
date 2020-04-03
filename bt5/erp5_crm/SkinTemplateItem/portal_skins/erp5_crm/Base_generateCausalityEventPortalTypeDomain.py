portal = context.getPortalObject()
portal_type_list = portal.getPortalEventTypeList()
portal_types = portal.portal_types
translateString = portal.Base_translateString
domain_list = []

domain_list_append = domain_list.append

if depth == 0:
  for uid, portal_type in enumerate(portal_type_list):
    domain = parent.generateTempDomain(id='%s_%s' % (depth, uid))
    domain.edit(title=translateString(portal_types[portal_type].getId()),
                domain_generator_method_id=script.id,
                uid=uid)
    domain.setCriterion(property='causality_portal_type', identity=portal_type)
    domain.setCriterionPropertyList(['causality_portal_type'])
    domain_list_append(domain)

return domain_list
