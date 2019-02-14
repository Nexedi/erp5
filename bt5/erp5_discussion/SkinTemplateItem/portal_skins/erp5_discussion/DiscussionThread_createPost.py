post = context.PostModule_createHTMLPost(
          title = title,
          source_reference = context.getReference(),
          data = text_content,
          follow_up = context.getRelativeUrl(),
          predecessor = None
)

attached_file = None
web_site_relative_url = None
if attached_file not in ("undefined", None):
  pass # TODO attached file
else:
  post.publish()

after_ingest_document_tag = 'after-ingest-%s' % post.getId()
post.activate(
        after_tag=after_ingest_document_tag
    ).Post_ingestAndCreateEvent(
        web_site_relative_url=web_site_relative_url)
