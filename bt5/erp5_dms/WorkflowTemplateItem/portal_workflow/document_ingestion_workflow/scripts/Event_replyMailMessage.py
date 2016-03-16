message = state_change.kwargs['reply_body']
subject = state_change.kwargs['reply_subject']
recipient = state_change.kwargs['reply_to']
object = state_change['object']

state_change['object'].MailHost.send(message, mto=recipient, 
                                     mfrom=object.portal_preferences.getPreferredEventSenderEmail(),
                                     subject=subject)
