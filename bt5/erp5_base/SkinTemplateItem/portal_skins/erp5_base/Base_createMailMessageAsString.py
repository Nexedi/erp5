"""Build a mail message

 * from_url: the "from" address as UTF-8 encoded string
 * to_url: the "to" header as UTF-8 encoded string
 * subject: the subject of the message as UTF-8 encoded string
 * body: body of the message as UTF-8 encoded string
 * content_type: mime type of this message, can be text/html for
   HTML message or anything else for text/plain message.
 * attachment_list: a list of attachment mapping in format:
    - mime_type (str): mime type of thsi attachment
    - content (bytes): file content of the attachment
    - name (str): displayed name of this attachment
 * embedded_file_list: a list of ERP5 File to use as attachments.
 * extra_header_dict: additional email headers

Notes: for from_url and to_url, we should use email.utils.formataddr
"""
if extra_header_dict is None:
  extra_header_dict = {}

if content_type == 'text/html':
  mail_template = context.Event_viewHtmlMimeMessage
else:
  mail_template = context.Event_viewMimeMessage

attachment_list = list(attachment_list)
for embedded_file in embedded_file_list:
  mime_type, content = embedded_file.getMimeTypeAndContent()
  name = embedded_file.getFilename()

  attachment_list.append({'mime_type':mime_type,
                          'content':content,
                          'name':name})

  # Allow to embed image in HTML by setting the relative URL of the image with FCKeditor
  attachment_url = embedded_file.getRelativeUrl()
  body = body.replace('src="%s"' % attachment_url, 'src="cid:%s"' % ''.join(['%s' % ord(i) for i in name]))

multipart = mail_template.as_message(mfrom=from_url,
                                     mto=to_url,
                                     subject=subject,
                                     body=body,
                                     encoding='utf-8',
                                     headers=extra_header_dict)
for attachment_dict in attachment_list:
  multipart.add_file(data=attachment_dict['content'],
                     content_type=attachment_dict['mime_type'],
                     filename=attachment_dict['name'])

return str(multipart)
