for email in email_recipient_list:
  context.MailHost.send("From: %s\nTo: %s\nContent-Type: text/plain;\n  charset=\"utf-8\"\n\n\n%s" % (email_sender,email,email_text),
                        mto=email, mfrom=email_sender,
                        subject=email_title, encode='8bit')

return context.Base_redirect('view', keep_items={'portal_status_message': "Done"})
