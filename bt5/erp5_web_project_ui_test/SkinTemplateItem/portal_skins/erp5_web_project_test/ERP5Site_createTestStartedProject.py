portal = context.getPortalObject()

if home_page:
  module = portal.getDefaultModule('Web Page')
  home_page = module.newContent(portal_type = 'Web Page',
                              reference = 'test-project-Home.Page')
  home_page.publishAlive()

module = portal.getDefaultModule('Project')
project = module.newContent(portal_type = 'Project',
                            reference = 'test-project')
project.validate()
print "Project Created"
return printed
