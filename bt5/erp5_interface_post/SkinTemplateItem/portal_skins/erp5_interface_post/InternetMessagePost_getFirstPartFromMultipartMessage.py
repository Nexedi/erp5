"""
This script can be used to give a preview of an Internet Mail Message.
Usually, the data is a multipart message (at least ERP5 only create
multipart message). As for users don't want an accurate representation of
the message, but a preview, we assume that rendering the first part
of the multipart message is enough.
"""
import six
import email

message = email.message_from_string(context.getData().decode())

payload = message.get_payload()

while isinstance(payload, list):
  payload = payload[0].get_payload(decode=True)

if six.PY3:
  payload = payload.decode()
return payload
