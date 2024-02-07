"""
  This script is used in listbox allowing when switching 'table' --> 'search' mode.
  It will try to generate parts of the document's text
  containing searched words as well highlighting the searched
  words in the text itself.
"""
import six
from erp5.component.document.Document import NotConvertedError

encoding = 'utf-8'
is_gadget_mode = context.REQUEST.get('is_gadget_mode', 0)

if is_gadget_mode:
  # in gadget mode less space is available thus show less text
  max_text_length = 100
  max_lines = 1

def getRandomDocumentTextExcerpt(document_text):
  # try to get somewhat arbitrary choice of searchable attrs
  if isinstance(document_text, str) and document_text!='':
    if six.PY2:
      document_text = document_text.decode(encoding, 'ignore')
    start = min(len(document_text) - 300, 200)
    result = '... %s ...' %document_text[start:start + max_text_length]
    if six.PY2:
      result = result.encode(encoding)
    return result
  else:
    return ''

if document_text is None:
  try:
    # if SearchableText is joinned as it is, we use it for better performance.
    document_text = getattr(context, 'SearchableText', None)
    if not isinstance(document_text, six.string_types):
      document_text = context.getSearchableText()
  except NotConvertedError:
    return context.Base_translateString("This document is not converted yet.")

search_string = context.Base_getSearchText(selection)

if search_string != '':
  search_argument_list = context.Base_parseSearchString(search_string)
  search_string = search_argument_list.get('searchabletext', '')

if search_string == '':
  # the searched words are empty (e.g. because we used only parameters
  # without pure searchable text)
  return getRandomDocumentTextExcerpt(document_text)
else:
  found_text_fragments = context.Base_getExcerptText(
                           context, \
                           document_text, \
                           search_string, \
                           tags = ('<em>', '</em>'), \
                           trail = 5, \
                           maxlines = max_lines)
  result = ' '.join(map(str, found_text_fragments))

  # Document may contains charactors which utf8 codec cannot decode.
  if six.PY2:
    unicode_result = result.decode(encoding, 'ignore')
    result = unicode_result.encode(encoding)

  return result
