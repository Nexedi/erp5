import time
from datetime import datetime
portal = context.getPortalObject()
now = datetime.now()
date_time = now.strftime("%m-%d-%Y-%H-%M-%S")
test_id = "documented-project-" if create_project_documents else "test-project-"
test_id += date_time
project_reference = 'test-project-home' if home_page else 'documented-project' if create_project_documents else 'test-project'
page_reference = 'test-home-page-' + date_time
failed_project = "failed-project"
empty_project = "empty-project"
draft_project = "draft-project"

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
  project.setForumLinkUrlString("test-forum-link")
  # MILESTONES
  project.newContent(id = test_id + "-1",
                     portal_type = 'Project Milestone',
                     reference = 'test-project-milestone')
  # TASKS
  module = portal.getDefaultModule('Task')
  task = module.newContent(id = test_id + "-1",
                           portal_type = 'Task',
                           reference = 'lonely-task')
  task.plan()
  task = module.newContent(id = test_id + "-2",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task = module.newContent(id = test_id + "-3",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task.order()
  task = module.newContent(id = test_id + "-4",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task.confirm()
  task = module.newContent(id = test_id + "-5",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task.cancel()
  task = module.newContent(id = test_id + "-6",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task.delete()
  task = module.newContent(id = test_id + "-7",
                           portal_type = 'Task',
                           reference = 'task-' + project_reference,
                           source_project_value = project)
  task.plan()

  # BUGS
  module = portal.getDefaultModule('Bug')
  bug = module.newContent(id = test_id + "-1",
                           portal_type = 'Bug',
                           reference = 'lonely-bug')
  bug.confirm()
  bug = module.newContent(id = test_id + "-2",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug = module.newContent(id = test_id + "-3",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.confirm()
  bug = module.newContent(id = test_id + "-4",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.confirm()
  bug.stop()
  bug = module.newContent(id = test_id + "-5",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.confirm()
  bug.setReady()
  bug = module.newContent(id = test_id + "-6",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.confirm()
  bug.cancel()
  bug = module.newContent(id = test_id + "-7",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.delete()
  bug = module.newContent(id = test_id + "-8",
                           portal_type = 'Bug',
                           reference = 'bug-' + project_reference,
                           source_project_value = project)
  bug.confirm()
  bug.stop()
  bug.deliver()

  # TASK REPORTS
  module = portal.getDefaultModule('Task Report')
  task_report = module.newContent(id = test_id + "-1",
                           portal_type = 'Task Report',
                           reference = 'lonely-task-report')
  task_report.confirm()
  task_report = module.newContent(id = test_id + "-2",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report = module.newContent(id = test_id + "-3",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.confirm()
  task_report = module.newContent(id = test_id + "-4",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.stop()
  task_report = module.newContent(id = test_id + "-5",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.confirm()
  task_report.start()
  task_report = module.newContent(id = test_id + "-6",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.stop()
  task_report.deliver()
  task_report = module.newContent(id = test_id + "-7",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.delete()
  task_report = module.newContent(id = test_id + "-8",
                           portal_type = 'Task Report',
                           reference = 'task-report-' + project_reference,
                           source_project_value = project)
  task_report.cancel()

  # TEST RESULTS
  module = context.portal_catalog.getDefaultModule('Test Result')
  test_result = module.newContent(id = test_id + "-1",
                                  portal_type = 'Test Result',
                                  source_project_value = project)
  test_result.newContent(id = "1",
                         portal_type = 'Test Result Line',
                         reference = "test-result-line")
  test_result = module.newContent(id = test_id + "-2",
                                  portal_type = 'Test Result',
                                  source_project_value = project)
  test_result.newContent(id = "1",
                         portal_type = 'Test Result Line',
                         reference = "test-result-line")
  test_result.start()
  test_result = module.newContent(id = test_id + "-3",
                                  portal_type = 'Test Result',
                                  source_project_value = project)
  test_result.newContent(id = "1",
                         portal_type = 'Test Result Line',
                         reference = "test-result-line")
  test_result.start()
  test_result.fail()
  test_result = module.newContent(id = test_id + "-4",
                                  portal_type = 'Test Result',
                                  source_project_value = project)
  test_result_line = test_result.newContent(id = "1",
                                            portal_type = 'Test Result Line',
                                            reference = "test-result-line")
  test_result_line.start()
  test_result_line.stop(test_count=20)
  time.sleep(5)
  test_result.start()
  test_result.stop()

  # FAILED PROJECT
  module = portal.getDefaultModule('Project')
  failed_project = module.newContent(id = failed_project + "-" + date_time,
                                     portal_type = 'Project',
                                     reference = failed_project)
  failed_project.validate()
  module = context.portal_catalog.getDefaultModule('Test Result')
  test_result = module.newContent(id = test_id + "-failed",
                                  portal_type = 'Test Result',
                                  source_project_value = failed_project)
  test_result_line = test_result.newContent(id = "1",
                                            portal_type = 'Test Result Line',
                                            reference = "test-result-line")
  test_result_line.start()
  test_result_line.stop(test_count=15, error_count=10, failure_count=10)
  time.sleep(5)
  test_result.start()
  test_result.fail()

  # EMPTY PROJECT
  module = portal.getDefaultModule('Project')
  empty_project = module.newContent(id = empty_project + "-" + date_time,
                                    portal_type = 'Project',
                                    reference = empty_project)
  empty_project.validate()

  # DRAFT PROJECT
  module = portal.getDefaultModule('Project')
  empty_project = module.newContent(id = draft_project + "-" + date_time,
                                    portal_type = 'Project',
                                    reference = draft_project)

print("Project Created")
return printed
