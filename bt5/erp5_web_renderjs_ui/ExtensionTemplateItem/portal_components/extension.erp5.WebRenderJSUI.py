import lxml
import io
import re

def TextDocument_substituteTextContent(self, text, **kw):
  """ XXXX"""
  return self._substituteTextContent(text, **kw)


def ERP5Site_extractTranslationMessageListFromHTML(self, text_content):
  """Extract messages from the text content of html text_content
  """
  if not text_content:
    return
  if isinstance(text_content, bytes):
    text_content = text_content.decode('utf-8')

  parser = lxml.etree.HTMLParser()
  tree = lxml.etree.parse(io.StringIO(text_content), parser)
  if tree.getroot() is None:
    return

  # find data-i18n attributes in HTML
  # message can be data-i18n="[value]Submit", in that case we return only Submit
  tag_re = re.compile(r'^\[.*?\]')
  for e in tree.xpath("//*[@data-i18n]"):
    yield tag_re.sub("", e.attrib["data-i18n"], 1)

  # find data-i18n= in comments
  comment_data_i18n_re = re.compile(r'data-i18n=(.*)')
  # if message is quoted, strip quotes to keep only message
  remove_quote_re = re.compile(r"^[\"']+(.*)[\"']+$")

  for comment in tree.xpath("//comment()"):
    for message in comment_data_i18n_re.findall(comment.text):
      remove_quote_match = remove_quote_re.match(message)
      yield remove_quote_match.groups()[0] if remove_quote_match else message

  # extract messages in scripts, they can be html templates
  for script in tree.xpath("//script"):
    for message in ERP5Site_extractTranslationMessageListFromHTML(self, script.text):
      yield message
