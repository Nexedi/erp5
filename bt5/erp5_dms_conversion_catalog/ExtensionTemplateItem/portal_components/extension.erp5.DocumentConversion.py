import re

def Base_extractImageUrlList(self, text_content=None):
  """
    Extract list of image URLS used in a Text document (i.e. Web Page)
  """
  if text_content is None:
    text_content = self.getTextContent()
  if text_content is not None:
    return re.findall('src=[\"\'](.[^\"\']+)[\"\']', text_content, re.I)
  return []
