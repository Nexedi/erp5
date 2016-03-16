# this script set the email of the form using the accountant email :
form = state_change['object']
email = form.getAccountantEmail()
form.setDefaultEmailText(email)
