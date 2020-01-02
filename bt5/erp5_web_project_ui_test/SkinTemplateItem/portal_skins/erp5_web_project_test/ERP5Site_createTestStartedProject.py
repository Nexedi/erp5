portal = context.getPortalObject()
project_reference = 'test-project'

module = portal.getDefaultModule('Project')
project = module.newContent(portal_type = 'Project',
                            reference = project_reference)
project.validate()

if home_page:
  system_preference = portal.portal_preferences.getActiveSystemPreference()
  system_preference.setPreferredPublicationSection("project_home_page_for_test")
  publication_section = context.restrictedTraverse('portal_categories/publication_section/project_home_page_for_test')
  module = portal.getDefaultModule('Web Page')
  home_page = module.newContent(portal_type = 'Web Page',
                                reference = project_reference + '-home.page',
                                publication_section_value = publication_section,
                                follow_up_value = project)
  home_page.publishAlive()

print "Project Created"
return printed
