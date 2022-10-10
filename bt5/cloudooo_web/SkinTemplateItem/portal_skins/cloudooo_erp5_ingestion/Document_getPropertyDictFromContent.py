"""
This script analyzes the document content (text_content) to find properties that might
be somehow encoded in the text. It is called by Document.getPropertyDictFromContent
method.

To use, write your own method (probably External Method, since it is most likely
to use re) that would analyze text content of the doc
and return a dictionary of properties.
"""
#Proxify to allow discover of metadata when publishing document
import six
information = context.getContentInformation()

result = {}
property_id_list = context.propertyIds()
for k, v in information.items():
  key = k.lower()
  if v:
    if six.PY2 and isinstance(v, six.text_type): v = v.encode('utf-8')
    if key in property_id_list:
      if key == 'reference':
        pass # XXX - We can not trust reference on getContentInformation
      else:
        result[key] = v
    elif key == 'author':
      p = context.portal_catalog.getResultValue(title = v)
      if p is not None:
        result['contributor'] = p.getRelativeUrl()
    elif key == 'keywords':
      result['subject_list'] = v.split()

object = object or context

#try:
#  content = content or context.asText()
#except AttributeError:
#  return result

ptype = ptype or context.getPortalType()

# Erase titles which are meaningless
title = result.get('title', None)
if title:
  if title.startswith('Microsoft Word'):
    # Probably a file generated from MS Word
    del result['title']
  elif title==context.getId() and not context.title:
    # this is not a true title, but just an id.
    del result['title']

return result
