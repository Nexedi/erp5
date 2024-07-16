import six
text = context.asText()
LENGTH = 25

# In PY3, this is utf-8 str(), so no need to worry to cut in the middle of
# multibyte character
if six.PY3:
  return text[:LENGTH]

# But in PY2, this must be converted to unicode() first...
from Products.ERP5Type.Utils import unicode2str
try:
  return unicode2str(six.text_type(text, 'utf-8')[:LENGTH])
except UnicodeDecodeError:
  return text[:LENGTH]
