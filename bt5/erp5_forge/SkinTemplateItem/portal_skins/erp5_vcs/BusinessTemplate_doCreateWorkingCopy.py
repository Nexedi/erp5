from ZTUtils import make_query
form_results = context.BusinessTemplate_viewCreateWorkingCopy.validate_all(REQUEST)
working_copy = form_results['your_repository']
context.getVcsTool(path=working_copy).createBusinessTemplateWorkingCopy()

query_string = make_query(portal_status_message='Business Template Working Copy created')
REQUEST.response.redirect('%s/BusinessTemplate_viewVcsStatus?%s' % 
                          (context.absolute_url_path(), query_string))
