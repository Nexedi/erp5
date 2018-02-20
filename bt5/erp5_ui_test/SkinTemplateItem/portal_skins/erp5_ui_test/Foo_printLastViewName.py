# This script simulates a standard Print action
#
# Print action expects the previous view to be accessible in `form_id`
# and it prints it out in both UI compatible way - as a redirect message.
context.REQUEST.form['last_form_id'] = form_id
return context.Base_renderForm('Foo_viewPrintoutForm')
