context.REQUEST.response.setHeader('Access-Control-Allow-Origin', '*')

error = []
#We should verify if the project actually exists
if context.getTitle() is None:
  error.append('ERROR: No project associated!')
if context.getTestSuite() is None:
  error.append('ERROR: No test-suite associated!')
if context.getTestSuiteTitle() is None:
  error.append('ERROR: No test-suite-title associated!')
vcs_repository_list = context.objectValues(portal_type="Test Suite Repository")
if len(vcs_repository_list) == 0 :
  error.append("No vcs_repository_list! (minimum 1)")
else:
  profile_count = 0
  for vcs_list in vcs_repository_list:
    for property_name in ['git_url','buildout_section_id','branch']:
      property_value = vcs_list.getProperty(property_name)
      if property_value is None:
        error.append('ERROR: No '+property_name+'!')
    if not(vcs_list.getProperty('profile_path') is None):
      profile_count += 1
  if profile_count == 0:
    error.append('ERROR: No profile_path in any vcs_repository! (minimum 1)')

return len(error) >0
