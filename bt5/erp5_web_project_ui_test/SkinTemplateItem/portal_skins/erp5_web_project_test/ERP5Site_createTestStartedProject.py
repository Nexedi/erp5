portal = context.getPortalObject()
from datetime import datetime
now = datetime.now()
date_time = now.strftime("%m-%d-%Y-%H-%M-%S")
test_id = "test-project-" + date_time
project_reference = 'test-project-' + date_time
page_reference = 'test-home-page-' + date_time

module = portal.getDefaultModule('Project')
project = module.newContent(id = test_id,
                            portal_type = 'Project',
                            reference = project_reference)
project.validate()

if home_page:
  system_preference = portal.portal_preferences.getActiveSystemPreference()
  system_preference.setPreferredPublicationSection("project_home_page_for_test")
  publication_section = context.restrictedTraverse('portal_categories/publication_section/project_home_page_for_test')
  module = portal.getDefaultModule('Web Page')
  home_page = module.newContent(id = test_id,
                                portal_type = 'Web Page',
                                reference = page_reference,
                                publication_section_value = publication_section,
                                follow_up_value = project)
  home_page.publishAlive()

print "Project Created"
return printed
