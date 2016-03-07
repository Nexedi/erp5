portal = context.getPortalObject()

# Update roles
portal_type = portal.searchFolder(title='portal_types')[0]
portal_type.searchFolder(title='Person')[0].updateRoleMapping()
portal_type.searchFolder(title='Product')[0].updateRoleMapping()
portal_type.searchFolder(title='Organisation')[0].updateRoleMapping()
portal_type.searchFolder(title='Sale Trade Condition')[0].updateRoleMapping()

# Clone users
module = context.person_module
my_user = module.scalability_user
for i in xrange(0,350):
  new_user = my_user.Base_createCloneDocument(batch_mode=1)
  name = 'scalability_user_%d' %i
  new_user.setId(name)
  new_user.setTitle(name)
  new_user.setReference(name)
  # new_user.setSubordinationValue(some_organisation_document)
  new_user.validate()
  assignment = new_user.objectValues(portal_type='Assignment')[0]
  assignment.open()

# Update roles
portal_type = portal.searchFolder(title='portal_types')[0]
portal_type.searchFolder(title='Person')[0].updateRoleMapping()
portal_type.searchFolder(title='Product')[0].updateRoleMapping()
portal_type.searchFolder(title='Organisation')[0].updateRoleMapping()
portal_type.searchFolder(title='Sale Trade Condition')[0].updateRoleMapping()

# Validate rules in portal_rules
portal_rules = portal.portal_rules
for rule in portal_rules.searchFolder(validation_state = "draft"):
  rule.validate()


# Return 1, at the end of the script.
return 1
