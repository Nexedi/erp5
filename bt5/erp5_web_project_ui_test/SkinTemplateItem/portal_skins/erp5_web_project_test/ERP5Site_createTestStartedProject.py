portal = context.getPortalObject()
from datetime import datetime
now = datetime.now()
date_time = now.strftime("%m-%d-%Y-%H-%M-%S")
test_id = "documented-project-" if create_project_documents else "test-project-"
test_id += date_time
project_reference = 'test-project-home' if home_page else 'documented-project' if create_project_documents else 'test-project'
page_reference = 'test-home-page-' + date_time

module = portal.getDefaultModule('Project')
project = module.newContent(id = test_id,
                            portal_type = 'Project',
                            reference = project_reference)
project.validate()

if home_page:
  system_preference = portal.portal_preferences.getActiveSystemPreference()
  system_preference.setPreferredProjectHomePagePublicationSectionCategory("project_home_page_for_test")
  publication_section = context.restrictedTraverse('portal_categories/publication_section/project_home_page_for_test')
  module = portal.getDefaultModule('Web Page')
  home_page = module.newContent(id = test_id,
                                portal_type = 'Web Page',
                                reference = page_reference,
                                publication_section_value = publication_section,
                                follow_up_value = project)
  home_page.publishAlive()

if create_project_documents:
  # EMPTY PROJECT
  module = portal.getDefaultModule('Project')
  empty_project = module.newContent(id = "empty-project-" + date_time,
                                    portal_type = 'Project',
                                    reference = "empty-project")
  empty_project.validate()

  # DRAFT PROJECT
  module = portal.getDefaultModule('Project')
  empty_project = module.newContent(id = "draf-project-" + date_time,
                                    portal_type = 'Project',
                                    reference = "draf-project")


print "Project Created"
return printed
