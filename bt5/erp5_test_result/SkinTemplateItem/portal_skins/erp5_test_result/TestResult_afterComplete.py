""" Called after test results are saved under ERP5 from workflow transition. """

recipient_list = []
include_link = 1

project = context.getSourceProjectValue()
if project is not None:
  source_administration = project.getSourceAdministrationValue()
  if source_administration is not None:
    recipient_list = [source_administration.getDefaultEmailText()]

# send emails
if recipient_list:
  context.TestResult_sendEmailNotification(mail_to=recipient_list,
                                           mail_from='nobody@svn.erp5.org',
                                           include_link=include_link,
                                           include_diff=True)
  print('Successfully sent to: ', recipient_list)
print('OK')
return printed
