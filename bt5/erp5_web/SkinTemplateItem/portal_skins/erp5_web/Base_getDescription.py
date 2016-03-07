"""
  Return a description (usually for Web cases like RSS) of arbitrary types.
  XXX: We need to extend and generalize Description property.
"""
portal_type = context.getPortalType()
if portal_type=='Discussion Thread':
  # take description from first Discussion post
  discussion_post_list = context.objectValues()
  if len(discussion_post_list):
    return discussion_post_list[0].getTextContent()

if getattr(context, 'getTextContent', None) is not None:
  return context.getTextContent()

# by default use getDescription
if getattr(context, 'getDescription', None) is not None:
  return context.getDescription()
