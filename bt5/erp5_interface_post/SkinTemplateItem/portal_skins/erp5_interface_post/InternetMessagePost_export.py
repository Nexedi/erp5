# calling ERP5Site_sendMailHostMessage should be done in an activity
# which NEVER retries.

context.activate(
  activity='SQLQueue',
  conflict_retry=False,
  max_retry=0,
).InternetMessagePost_sendMailHostMessage()
