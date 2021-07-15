"""
================================================================================
Parse a string for images and return a list with image information
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# document_content                     document content in string representation

import re

def setFigureAnchor(my_counter, my_title, my_href):
  return ''.join([
    '<a href="#',
    my_counter,
    '"></a><img src="',
    my_href,
    '" alt="',
    my_title,
    '" /><span>',
    my_counter,
    ' - ',
    my_title,
    '</span>'
  ])

# XXX single quotes?
figure_abbreviation = "Figure"
match_href = 'src="(.*?)"'
match_content = 'alt="(.*?)"'
figure_list = []
figure_count = 0
figure_doubles = {}
blank = ""

for figure in re.findall('(<img.*?/>)', document_content or ''):
  figure_dict = {}

  # no alt attribute = skip an image from being included
  figure_title = re.findall(match_content, figure) or blank
  if figure_title == blank or figure_title[0] == blank:
    continue

  figure_count = figure_count + 1
  figure_href = re.findall(match_href, figure) or [""]
  figure_id = figure_abbreviation + "-" + str(figure_count)
  figure_dict["input"] = figure
  figure_dict["output"] = setFigureAnchor(
    figure_id,
    figure_title[0],
    figure_href[0]
  )
  if figure_doubles.get(figure_title[0], None) is None:
    item_dict = {}
    item_dict["id"] = figure_id
    item_dict["title"] = figure_title[0]
    figure_dict["item"] = item_dict
    figure_list.append(figure_dict)

response_dict = {}
response_dict["figure_list"] = figure_list
return response_dict
