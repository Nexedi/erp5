"""
================================================================================
Parse a string for tables and return a list with tables information
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# document_content                     document content in string representation
#
# Note: also handles reports which look like tables and have a caption.

import re

def setTableCaption(my_counter, my_title, my_shift):
  return ''.join([
    '<a href="#',
    my_counter,
    '"></a>',
    caption_filler[0 + my_shift],
    my_counter,
    ' - ',
    my_title,
    caption_filler[1 + my_shift]
  ])

def digestCaption(my_caption, my_caption_title, my_count, my_shift):
  if match_doubles.get(my_caption_title, None) is None:
    match_doubles[my_caption_title] = my_count
    caption_relevant_count = my_count
    my_count += 1

    #caption_relevant_count = match_doubles[my_caption_title]
    caption_id = caption_abbreviation + "-" + str(caption_relevant_count)
    caption_dict = {}
    caption_dict["input"] = my_caption
    caption_dict["item"] = {}
    caption_dict["item"]["id"] = caption_id
    caption_dict["item"]["title"] = my_caption_title
    caption_dict["output"] = setTableCaption(
      caption_id,
      my_caption_title,
      my_shift
    )
    caption_list.append(caption_dict)

  return my_count

# XXX single quotes?
caption_abbreviation = "Table"
caption_filler = ['<caption>', '</caption>', '<div class="ci-book-caption">','</div>']
caption_list = []
caption_count = 1
match_doubles = {}

for caption in re.findall('(<caption.*?>.*?</caption>)', document_content or ''):
  caption_title = re.findall('<caption.*?>(.*?)</caption>', caption)[0]
  caption_count = digestCaption(caption, caption_title, caption_count, 0)
  #if match_doubles.get(caption_title, None) is None:
  #  match_doubles[caption_title] = caption_count
  #  caption_relevant_count = caption_count
  #else:
  #  caption_relevant_count = match_doubles[caption_title]
  #caption_id = caption_abbreviation + "-" + str(caption_relevant_count)
  #caption_dict = {}
  #caption_dict["input"] = caption
  #caption_dict["item"] = {}
  #caption_dict["item"]["id"] = caption_id
  #caption_dict["item"]["title"] = caption_title
  #caption_dict["output"] = setTableCaption(
  #  caption_id,
  #  caption_title
  #)
  #caption_list.append(caption_dict)
  #caption_count = caption_count + 1

for fake_caption in re.findall('(<div class="ci-book-caption".*?>.*?</div>)', document_content or ''):
  fake_caption_title = re.findall('<div class="ci-book-caption".*?>(.*?)</div>', fake_caption)[0]
  caption_count = digestCaption(fake_caption, fake_caption_title, caption_count, 2)

response_dict = {}
response_dict["table_list"] = caption_list
return response_dict
