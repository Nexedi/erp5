portal = context.getPortalObject()

module = portal.getDefaultModule('Project')
project = module.newContent(portal_type = 'Project',
                            reference = 'test-project')
project.validate()
print "Project Created"
return printed
