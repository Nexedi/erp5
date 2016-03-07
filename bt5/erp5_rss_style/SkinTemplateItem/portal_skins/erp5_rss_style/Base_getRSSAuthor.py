"""
  Overwrite this script to get more meaningful information about author
  for RSS feeds.
  It is highly recommended to return a valid email address here, to make the
  feed 100% standard-compliant.
"""

# XXX What is the definition of 'author' value?
# Should it be 'the last person who modified the document'?
return context.getOwnerInfo().get('id', '')
