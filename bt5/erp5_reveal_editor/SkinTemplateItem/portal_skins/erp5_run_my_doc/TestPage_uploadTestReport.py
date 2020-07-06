context.setTestReport(context.REQUEST.form.get('test_report', 'default').read())
return "Report successfully uploaded\n" + context.getTestReport()
