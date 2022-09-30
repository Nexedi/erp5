vcs_list = context['vcs_repository_list']
test_suite_repository = context.TestSuiteRepository.newContent(
                  branch = vcs_list['branch'],
                  buildout_section_id = vcs_list['buildout_section_id'],
                  git_url = vcs_list['git_url'],
                  profile_path = vcs_list['profile_path']
             )

test_suite = context.newContent(
                    title=title,
                    test_suite_title = config['test_suite_title'],
                    test_suite = config['test_suite'],
                    int_index = config['int_index'],
                    vcs_repository = test_suite_repository
                    )

if batch_mode:
  return test_suite
