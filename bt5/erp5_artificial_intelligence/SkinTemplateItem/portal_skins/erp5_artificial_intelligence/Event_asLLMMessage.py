"""Return the representation of one Event for one Large Language Model.

Skin folder: `erp5_artificial_intelligence`.
Parameter line: empty. The context is one Event.

The portal type
`Artificial Task Line` holds the type class `Event`.
`product/ERP5Type/Base.py` lines 3101 to
3108 look the script up by the class. This script therefore serves every
`Artificial Task Line`. This script serves every other Event that holds no
closer script.

The script answers the title and the text content. The script answers
`is_file = 0`. This script never answers one file.

WARNING: this script must never raise. A raise ends the whole run with one
`error` line.

The script writes nothing. The script calls no provider.
"""

# About 5000 tokens. A long text costs tokens and can pass the request limit
# of the provider.
MAXIMUM_TEXT_LENGTH = 20000

event = context


def decodeText(value):
  """Return one unicode text of one value. This function never raises.

  WARNING: an ERP5 accessor answers UTF-8 bytes on Python 2. A byte string
  inside one unicode format makes Python 2 decode with the ASCII codec. A
  German text then raises `UnicodeDecodeError`.

  The function answers one `unicode` value without one change. The function
  decodes one byte string with the codec `utf-8` and the error handler
  `replace`. The function answers `u''` on any defect.
  """
  if value is None:
    return u''
  try:
    if isinstance(value, unicode):
      return value
  except Exception:
    return u''
  try:
    if isinstance(value, str):
      return value.decode('utf-8', 'replace')
  except Exception:
    return u''
  try:
    return u'%s' % (value, )
  except Exception:
    return u''


def safeText(method_name):
  """Return the answer of one text accessor of the Event as unicode.

  `method_name` is one literal of this script. No value of the model reaches
  this function.

  WARNING: the answer of the accessor can be UTF-8 bytes. The function decodes
  the answer. Read the docstring of `decodeText`. This function never raises.
  """
  try:
    method = getattr(event, method_name, None)
    if method is None:
      return u''
    return decodeText(method())
  except Exception:
    return u''


def boundText(value):
  """Return one unicode text of at most MAXIMUM_TEXT_LENGTH characters."""
  text = decodeText(value)
  if len(text) > MAXIMUM_TEXT_LENGTH:
    return text[:MAXIMUM_TEXT_LENGTH] + u'\n[the text is cut here]'
  return text


title = boundText(safeText('getTitle'))
text_content = boundText(safeText('getTextContent'))

if title and text_content:
  text = u'%s\n\n%s' % (title, text_content)
else:
  text = title or text_content

return {
  'role': 'user',
  'text': text,
  'is_file': 0,
}
