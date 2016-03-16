"""
  Return the result list of all documents found by specified keyword arguments.
"""
import re
# if language is not specified in search_text, it means any language.
# if language is specified in search_text, the query anyway includes explicit
# language condition.
kw['all_languages'] = True
if re.search(r'\bnewest:yes\b', search_text):
  #...and now we check for only the newest versions
  # but we need to preserve order
  return [doc.getLatestVersionValue(language=doc.getLanguage()) \
          for doc in context.getDocumentValueList(search_text=search_text, **kw)]
else:
  return context.getDocumentValueList(search_text=search_text, **kw)
