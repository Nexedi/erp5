"""
  Translate message into another language.
  If 'lang' is omitted a selected user interface language is used.
  Can use any of existing message catalogs (default is 'ui').
"""

from Products.CMFCore.utils import getToolByName
translation_service = getToolByName(context, 'Localizer', None)
if translation_service is not None :
  import six
  try:
    if not encoding:
      return translation_service.translate(catalog, msg, lang=lang, **kw)
    msg = translation_service.translate(catalog, msg, lang=lang, **kw)
    if six.PY2 and isinstance(msg, six.text_type):
      msg = msg.encode(encoding)
    elif six.PY3 and isinstance(msg, six.binary_type):
      msg = msg.decode(encoding)
    return msg
  except AttributeError: # This happens in unit testing, because it is not able to find something with get_context()
    pass

return msg
