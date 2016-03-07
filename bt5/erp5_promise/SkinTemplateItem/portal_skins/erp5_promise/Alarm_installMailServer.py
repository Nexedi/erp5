portal = context.getPortalObject()
mailhost = portal.MailHost
if getattr(mailhost, 'getMessageList', None) is not None:
  # cannot fix wrong MailHost
  return
promise_url = portal.getPromiseParameter('external_service', 'smtp_url')

if promise_url is None:
  return

protocol, promise_url = promise_url.split('://', 1)

if protocol == 'smtps':
  force_tls = True
else:
  force_tls = False

auth_item = promise_url.rsplit('@', 1)
if len(auth_item) == 2:
  auth, promise_url = auth_item
  smtp_uid, smtp_pwd = auth.split(':')
else:
  smtp_uid = ""
  smtp_pwd = ""
  promise_url = auth_item[0]

domain_port = promise_url.split('/', 1)[0]
port = domain_port.split(':')[-1]
domain = domain_port[:-(len(port)+1)]

mailhost.manage_makeChanges(
  'Promise SMTP Server',
  domain,
  port,
  smtp_uid=smtp_uid,
  smtp_pwd=smtp_pwd,
  force_tls=force_tls,
)
