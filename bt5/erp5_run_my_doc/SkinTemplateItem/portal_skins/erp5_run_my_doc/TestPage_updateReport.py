"""
  Update the test report
"""

result_list = context.restrictedTraverse('/erp5/portal_tests/' + zuite_id).objectValues('Zuite Results')
result_list = sorted(result_list, key=lambda x: x.getId())
context.setTestReport(sorted(result_list[-1].objectValues(), key=lambda x: x.getId())[-1])

return context.Base_redirect('TestPage_viewTestReport', portal_status_message=context.Base_translateString('Test Report updated'))
