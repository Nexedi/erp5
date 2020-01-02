portal = context.getPortalObject()
project_reference = 'test-project'

module = portal.getDefaultModule('Project')
project = module.newContent(portal_type = 'Project',
                            reference = project_reference)
project.validate()

if home_page:
  module = portal.getDefaultModule('Web Page')
  home_page = module.newContent(portal_type = 'Web Page',
                                reference = project_reference + '-home.page',
                                publication_section = 'project_home_page',
                                follow_up = project.getRelativeUrl())
  home_page.publishAlive()

print "Project Created"
return printed
