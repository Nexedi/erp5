"""
This script can be used to give a preview of an Internet Mail Message.
Usually, the data is a multipart message (at least ERP5 only create
multipart message). As for users don't want an accurate representation of
the message, but a preview, we assume that rendering the first part
of the multipart message is enough.
"""
import six
if six.PY2:
  from email import message_from_string as message_from_bytes
else:
  from email import message_from_bytes

payload = message_from_bytes(context.getData()).get_payload()

while isinstance(payload, list):
  payload = payload[0].get_payload(decode=True)

return payload
