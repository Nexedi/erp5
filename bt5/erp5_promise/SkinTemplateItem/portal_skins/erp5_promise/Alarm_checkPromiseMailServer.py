from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
mailhost = portal.MailHost
if getattr(mailhost, 'getMessageList', None) is not None:
  context.newActiveProcess().postResult(ActiveResult(
    severity=1,
    summary="%s/MailHost is not real MailHost" % portal.getPath(),
    detail="Possibly comes from DummyMailHost. The object has to be fixed by recreating it."
  ))
  return

promise_url = portal.getPromiseParameter('external_service', 'smtp_url')

if promise_url is None:
  return

promise_url = promise_url.rstrip('/')
if mailhost.force_tls:
  protocol = 'smtps'
else:
  protocol = 'smtp'

if mailhost.smtp_uid:
  auth = '%s:%s@' % (mailhost.smtp_uid, mailhost.smtp_pwd)
else:
  auth = ''

url = "%s://%s%s:%s" % (protocol, auth, mailhost.smtp_host, mailhost.smtp_port)

active_result = ActiveResult()

if promise_url != url:
  severity = 1
  summary = "SMTP Server not configured as expected"
  detail = "Expect %s\nGot %s" % (promise_url, url)
else:
  severity = 0
  summary = "Nothing to do."
  detail = ""

active_result.edit(
  summary=summary,
  severity=severity,
  detail=detail)

context.newActiveProcess().postResult(active_result)
