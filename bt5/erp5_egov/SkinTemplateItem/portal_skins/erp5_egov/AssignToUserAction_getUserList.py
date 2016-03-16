'''This script return the list of all users that is possible to assign the application'''

group = context.getTypeInfo().getOrganisationDirectionService()

cat = context.restrictedTraverse('portal_categories/group/%s' % group)

if cat is not None:
  cat_uid = cat.getUid()
  agent_list = context.portal_catalog(portal_type='Assignment',
                                      group_uid=cat_uid)

  return [(agent.getParentValue().getReference(), agent.getParentValue().getReference()) for agent in agent_list if agent.getParentValue().getReference()]
else:
  return []
