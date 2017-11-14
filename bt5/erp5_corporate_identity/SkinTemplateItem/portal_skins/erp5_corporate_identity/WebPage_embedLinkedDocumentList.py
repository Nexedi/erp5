"""
================================================================================
Replace plain links (no [reference document links]) with linked document
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# doc_content                    string representation of document content

import re

blank = ""
for link in re.findall('([^[]<a.*?</a>[^]])', doc_content or blank):
  link_reference_list = re.findall('href=\"(.*?)\"', link)
  if len(link_reference_list) == 0:
    link_reference = re.findall("href=\'(.*?)\'", link)
  if len(link_reference_list) == 0:
    link_reference = None
  else:
    link_reference = link_reference_list[0]
  if link_reference.find("report=") > -1:
    link_reference = None

  # only internal references can be embedded
  if link_reference is not None and link_reference.find("http") == -1:
    try:
      link_doc = context.restrictedTraverse(link_reference.split("?")[0])
      doc_content = doc_content.replace(link, link_doc.asStrippedHTML())
    except LookupError:
      raise LookupError(link_reference)

doc_content = doc_content.replace("${related_subject_list}", blank)
doc_content = doc_content.replace("${table_of_content", blank)
return doc_content
