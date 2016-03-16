"""
  Get author details.
"""
portal = context.getPortalObject()

author = context.getSourceValue()
result = {'author_url': None,
          'author_signature': None,
          'author_title': context.Base_translateString('Unknown User'),
          'author_thumbnail_url': None}

if author is not None:
  result['author_url'] = '%s/view' %author.getAbsoluteUrl()
  result['author_signature'] = portal.ERP5Site_getUserPreferredForumSettingsDict(author.getReference())['preferred_forum_signature']
  result['author_title'] = author.getTitle()
  thumbnail = author.getDefaultImage()
  if thumbnail is not None and thumbnail.hasData():
    result['author_thumbnail_url'] = thumbnail.absolute_url()

return result
