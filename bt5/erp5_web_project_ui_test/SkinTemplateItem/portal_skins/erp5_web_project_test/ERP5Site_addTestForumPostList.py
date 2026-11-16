portal = context.getPortalObject()
thread = portal.portal_catalog.getResultValue(
  portal_type='Discussion Thread',
  title={'query': thread_title, 'key': 'ExactMatch'},
  sort_on=[('creation_date', 'DESC')])
if thread is None:
  raise ValueError('No Discussion Thread titled %r' % thread_title)
for i in range(int(post_count)):
  thread.newContent(portal_type='Discussion Post',
                    title='Extra post %d' % (i + 1),
                    text_content='<p>Extra post %d</p>' % (i + 1))
print("Posts Added")
return printed
