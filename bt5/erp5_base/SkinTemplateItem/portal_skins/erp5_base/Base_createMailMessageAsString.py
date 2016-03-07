if content_type == 'text/html':
  mail_template = context.Event_viewHtmlMimeMessage
else:
  mail_template = context.Event_viewMimeMessage

attachment_list = attachment_list[:]
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
                                     encoding='utf-8')
for attachment_dict in attachment_list:
  multipart.add_file(data=attachment_dict['content'],
                     content_type=attachment_dict['mime_type'],
                     filename=attachment_dict['name'])

return str(multipart)
