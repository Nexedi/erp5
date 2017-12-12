"""
================================================================================
Parse a string for links and return a list with link information
================================================================================
"""
import re

def setCitation(my_counter, my_title):
  return ''.join([
    '<a href="#',
    my_counter,
    '" title="',
    my_title,
    '">',
    my_counter,
    '</a>'
  ])

# XXX single quotes?
blank = ''
na = 'N/A'
match_citation_type = '<a.*?>(.*)</a>'
match_href = 'href="(.*?)"'
match_content = 'title="(.*?)"'

citation_ad_list = []
citation_ab_list = []
citation_rd_list = []
citation_ab_count = 1
citation_ad_count = 1
citation_rd_count = 1
citation_ab_doubles = {}
citation_ad_doubles = {}
citation_rd_doubles = {}

for citation in re.findall('\[(.*?)\]', document_content or ''):
  
  # disregard empty brackets
  if citation == blank:
    continue

  citation_href = (re.findall(match_href, citation) or [""])[0]

  # RD = Referenced Document / AD = Applicable Document
  # input:  bla linked document [<a href="" title="title;version;number">RD</a>]
  # output: bla linked document [<a href="#RD-1">RD-1</a>]
  # -------------------------------------------------------------------
  # | <a id="RD-1">RD-1</a> | <a href="">title</a> | version | number |
  # -------------------------------------------------------------------
  # AB = Abbreviation    
  # input:  bla ERP5 [<a href="" title="title;description">ERP5</a>]
  # output: bla ERP5 [<a href="#AB-1">#AB-1</a>]
  # -------------------------------------------------------------------
  # | <a id="AB-1">AB-1</a> | ERP5 | title | description              |
  # -------------------------------------------------------------------

  # XXX swalloing missing titles, not very elaborate
  citation_content = (re.findall(match_content, citation) or ["XXX"])[0]
  citation_content_list = citation_content.split(";")
  citation_info = []

  if len(citation_content_list) >= 3:
    citation_info = citation_content_list
  if len(citation_content_list) == 2:
    citation_info = [citation_content_list[0], citation_content_list[1], na]
  if len(citation_content_list) == 1:
    citation_info = [citation_content_list[0], na, na]
  if len(citation_content_list) == 0:
    citation_info = [na, na, na]

  citation_dict = {}
  citation_dict["input"] = citation
  citation_type = re.findall(match_citation_type, citation)[0]
  

  if citation_type == "AD":
    item_dict = {}
    item_dict["type"] = citation_type
    item_dict["title"] = citation_info[0]
    item_dict["number"] = citation_info[1]
    item_dict["version"] = citation_info[2]
    item_dict["href"] = citation_href
    if citation_ad_doubles.get(citation_href, None) is None:
      citation_ad_doubles[citation_href] = citation_ad_count
      citation_relevant_count = citation_ad_count
    else:
      citation_relevant_count = citation_ad_doubles[citation_href]
    citation_id = ''.join([citation_type, "-", str(citation_relevant_count)])
    item_dict["id"] = citation_id
    citation_dict["item"] = item_dict
    citation_dict["output"] = setCitation(citation_id, citation_info[0])
    citation_ad_list.append(citation_dict)
    citation_ad_count = citation_ad_count + 1
  elif citation_type == "RD":
    item_dict = {}
    item_dict["type"] = citation_type
    item_dict["title"] = citation_info[0]
    item_dict["number"] = citation_info[1]
    item_dict["version"] = citation_info[2]
    item_dict["href"] = citation_href
    if citation_rd_doubles.get(citation_href, None) is None:
      citation_rd_doubles[citation_href] = citation_rd_count
      citation_relevant_count = citation_rd_count
    else:
      citation_relevant_count = citation_rd_double[citation_href]
    citation_id = ''.join([citation_type, "-", str(citation_relevant_count)])
    item_dict["id"] = citation_id
    citation_dict["item"] = item_dict
    citation_dict["output"] = setCitation(
      citation_id,
      item_dict.get("title")
    )
    citation_rd_list.append(citation_dict)
    citation_rd_count = citation_rd_count + 1
  else:
    citation_abbreviation = citation_type
    citation_type = "AB"
    item_dict = {}
    item_dict["type"] = citation_type
    item_dict["abbreviation"] = citation_abbreviation
    item_dict["title"] = citation_info[0]
    item_dict["description"] = citation_info[1]
    item_dict["href"] = citation_href
    if citation_ab_doubles.get(citation_href, None) is None:
      citation_ab_doubles[citation_href] = citation_ab_count
      citation_relevant_count = citation_ab_count
    else:
      citation_relevant_count = citation_ab_doubles[citation_href]
    citation_id = ''.join([citation_type, "-", str(citation_relevant_count)])
    item_dict["id"] = citation_id
    citation_dict["item"] = item_dict
    citation_dict["output"] = setCitation(
      citation_id,
      item_dict.get("title")
    )
    citation_ab_list.append(citation_dict)
    citation_ab_count = citation_ab_count + 1

response_dict = {}
response_dict["reference_list"] = citation_rd_list
response_dict["applicable_list"] = citation_ad_list
response_dict["abbreviation_list"] = citation_ab_list
return response_dict
