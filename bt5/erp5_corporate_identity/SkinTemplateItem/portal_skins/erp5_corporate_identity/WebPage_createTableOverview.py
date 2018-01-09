"""
================================================================================
Parse a string for tables and return a list with tables information
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# document_content                     document content in string representation

import re

def setTableCaption(my_counter, my_title):
  return ''.join([
    '<a href="#',
    my_counter,
    '"></a><caption>',
    my_counter,
    ' - ',
    my_title,
    '</caption>'
  ])

# XXX single quotes?
caption_abbreviation = "TBL"
caption_list = []
caption_count = 1
match_doubles = {}

for caption in re.findall('(<caption.*?>.*?</caption>)', document_content or ''):
  caption_title = re.findall('<caption.*?>(.*?)</caption>', caption)[0]
  if match_doubles.get(caption_title, None) is None:
    match_doubles[caption_title] = caption_count
    caption_relevant_count = caption_count
  else:
    caption_relevant_count = match_doubles[caption_title]
  caption_id = caption_abbreviation + "-" + str(caption_relevant_count)
  caption_dict = {}
  caption_dict["input"] = caption
  caption_dict["item"] = {}
  caption_dict["item"]["id"] = caption_id
  caption_dict["item"]["title"] = caption_title
  caption_dict["output"] = setTableCaption(
    caption_id,
    caption_title
  )
  caption_list.append(caption_dict)
  caption_count = caption_count + 1

response_dict = {}
response_dict["table_list"] = caption_list
return response_dict
