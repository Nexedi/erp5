"""
Usage:

formatAttachmentListToMIMEMultipartString(
  subtype="related",
  header_dict={
    "From": "<Saved by ERP5>",
    "Subject": "Document Title",
  },
  param_list=[("type", "text/html")],
  attachment_list=[
    {
      "mime_type": "text/html",
      "charset": "utf-8",
      "encoding": "quoted-printable",
      "header_dict": {"Content-Location": "https://www.erp5.com/My.Web.Page"},  # only add headers
      "data": "<!DOCTYPE ...>.....................</...>",
    },
    {
      "mime_type": "image/png",
      "add_header_list": [("Content-Location", "https://www.erp5.com/My.Image")],
      "data": "\x00............\x01",
    }
  ]
);

Any header_dict or attachtment_list[x] properties are optional.

Note: text/* content will not be automatically encoded to quoted-printable
because this encoding can lose some characters like "\r" and possibly others.

To send specific encoded data, please make your attachment dict look like:

{
  "mime_type": "text/html",
  "encoding": "noop",
  "replace_header_list": [("Content-Transfer-Encoding", "my-encoding")],
  "data": encodestring(html_data),
}
"""

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import quopri

def formatMultipartMessageToRFC2822String(msg):
  """
  The `msg.as_string()` method does not exactly follow the RFC2822. The EOL are
  not CRLF ("\r\n") by default, so we have to replace the actual newlines
  (LF "\n") by CRLF if necessary.

  Note: The first space in each line of a multiline header will be replaced by a
  tabulation to make some mhtml viewers able to parse it, even if a simple space
  follows the RFC2822.
  """
  as_string = msg.as_string()  # it also forces the boundary generation
  if as_string.split("\n", 1)[0].endswith("\r"):
    return as_string
  boundary = msg.get_boundary()
  parts = as_string.split("\n" + boundary)
  parts[0] = "\r\n".join(parts[0].split("\n")).replace("\r\n ", "\r\n\t")
  i = 0
  for part in parts[1:]:
    i += 1
    partsplit = part.split("\n\n", 1)
    partsplit[0] = "\r\n".join(partsplit[0].split("\n")).replace("\r\n ", "\r\n\t")
    parts[i] = "\r\n\r\n".join(partsplit)
  return ("\r\n" + boundary).join(parts)

def encode_quopri_with_spaces(msg):
  """Encode the message's payload in quoted-printable.

  Also, add an appropriate Content-Transfer-Encoding header.
  """
  orig = msg.get_payload()
  encdata = quopri.encodestring(orig)
  msg.set_payload(encdata)
  msg['Content-Transfer-Encoding'] = 'quoted-printable'



outer = MIMEMultipart(subtype)
for key, value in param_list:
  outer.set_param(key, value)
if boundary is not None:
  outer.set_boundary(boundary)
if replace_header_list is not None:
  for key, value in replace_header_list:
    outer.replace_header(key, value)
if header_dict is not None:
  for key, value in header_dict.items():
    outer[key] = value
if add_header_list is not None:
  for key, value in add_header_list:
    outer.add_header(key, value)
for attachment in attachment_list:
  mime_type = attachment.get("mime_type", "application/octet-stream")
  data = attachment.get("data", "")
  encoding = attachment.get("encoding")
  if encoding not in ("base64", "quopri", "quoted-printable", "7or8bit", "noop", None):
    raise ValueError("unknown attachment encoding %r" % encoding)
  main_type, sub_type = mime_type.split("/")
  if encoding is None:
    if main_type == "image":
      part = MIMEImage(data, sub_type)
    elif main_type == "text":
      part = MIMEText(data, sub_type, attachment.get("charset", "us-ascii"))
    elif main_type == "audio":
      part = MIMEAudio(data, sub_type)
    elif main_type == "application":
      part = MIMEApplication(data, sub_type, encoders.encode_noop)
      if sub_type == "javascript":
        encoders.encode_quopri(part)
      else:
        encoders.encode_base64(part)
    else:
      part = MIMEBase(main_type, sub_type)
      part.set_payload(data)
      encoders.encode_base64(part)
  else:
    part = MIMEBase(main_type, sub_type)
    part.set_payload(data)
    if encoding == "base64":
      encoders.encode_base64(part)
    elif encoding == "quopri":
      encode_quopri_with_spaces(part)
    elif encoding == "quoted-printable":
      encoders.encode_quopri(part)
    elif encoding == "7or8bit":
      encoders.encode_7or8bit(part)
    else:  # elif encoding == "noop":
      encoders.encode_noop(part)
  for key, value in attachment.get("replace_header_list", []):
    part.replace_header(key, value)
  for key, value in attachment.get("header_dict", {}).items():  # adds headers, does not replace or set
    part[key] = value
  for key, value in attachment.get("add_header_list", []):
    part.add_header(key, value)
  if attachment.get("filename", None) is not None:
    part.add_header("Content-Disposition", "attachment", attachment["filename"])
  outer.attach(part)

#return outer.as_string()
return formatMultipartMessageToRFC2822String(outer)
