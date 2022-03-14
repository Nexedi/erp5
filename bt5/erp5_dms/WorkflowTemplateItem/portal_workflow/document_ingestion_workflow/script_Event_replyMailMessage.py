message = state_change.kwargs['reply_body']
subject = state_change.kwargs['reply_subject']
recipient = state_change.kwargs['reply_to']
event = state_change['object']

event.MailHost.send(
    message,
    mto=recipient,
    mfrom=event.portal_preferences.getPreferredEventSenderEmail(),
    subject=subject)
