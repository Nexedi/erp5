import six
text = context.asText()
LENGTH = 25

# TODO: Think about the display length of multibyte characters.
if six.PY3:
  return text[:LENGTH]
try:
  return six.text_type(text, 'utf-8')[:LENGTH].encode('utf-8')
except UnicodeDecodeError:
  return text[:LENGTH]
