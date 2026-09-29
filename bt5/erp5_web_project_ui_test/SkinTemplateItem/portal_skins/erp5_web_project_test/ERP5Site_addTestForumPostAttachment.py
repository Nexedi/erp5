portal = context.getPortalObject()
thread = portal.portal_catalog.getResultValue(
  portal_type='Discussion Thread',
  title={'query': thread_title, 'key': 'ExactMatch'},
  sort_on=[('creation_date', 'DESC')])
if thread is None:
  raise ValueError('No Discussion Thread titled %r' % thread_title)
post, = thread.contentValues(portal_type='Discussion Post')
attachment = portal.getDefaultModule('File').newContent(
  portal_type='File',
  title=attachment_title,
  content_type='text/plain',
  data='test attachment')
post.setSuccessorValueList([attachment])
print("Attachment Added")
return printed
