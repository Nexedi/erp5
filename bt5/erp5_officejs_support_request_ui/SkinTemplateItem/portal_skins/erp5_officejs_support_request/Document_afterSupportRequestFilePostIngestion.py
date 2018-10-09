"""Called on a document ingested from a file post on support request app,
after the document is ingested and metadata are discovered.
"""
post = context.getPortalObject().restrictedTraverse(post_relative_url)
# set relation between post and document
post.setSuccessorValueList([context])
post.publish()

context.share()
