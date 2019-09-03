"""
================================================================================
Parse a string for links and return a list with link information
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# document_content                 string representation of document content

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

for citation in re.findall(r'\[(.*?)\]', document_content or ''):

  # disregard empty brackets
  if citation == blank:
    continue

  citation_href = (re.findall(match_href, citation) or [""])[0]

  # disregard non-links:
  if citation_href == blank:
    continue

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

  # XXX swallowing missing title. not very elaborate
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
  # Those 3 parts has similar codes, leave as it so that it's easy to customize for each other
  if citation_type == "AD":
    if citation_href not in citation_ad_doubles:
      citation_ad_doubles[citation_href] = citation_ad_count
      citation_id = ''.join([citation_type, "-", str(citation_ad_count)])
      citation_dict["item"] = {
        "type": citation_type,
        "title": citation_info[0],
        "number": citation_info[1],
        "version": citation_info[2],
        "href": citation_href,
        "id": citation_id
      }
      citation_dict["output"] = setCitation(citation_id, citation_info[0])
      citation_ad_list.append(citation_dict)
      citation_ad_count = citation_ad_count + 1
  elif citation_type == "RD":
    if citation_href not in citation_rd_doubles:
      citation_rd_doubles[citation_href] = citation_rd_count
      citation_id = ''.join([citation_type, "-", str(citation_rd_count)])
      citation_dict["item"] = {
        "type": citation_type,
        "title": citation_info[0],
        "number": citation_info[1],
        "version": citation_info[2],
        "href": citation_href,
        "id" : citation_id
      }
      citation_dict["output"] = setCitation(citation_id,citation_info[0])
      citation_rd_list.append(citation_dict)
      citation_rd_count = citation_rd_count + 1
  else:
    if citation_href not in citation_ab_doubles:
      citation_ab_doubles[citation_href] = citation_ab_count
      citation_abbreviation = citation_type
      citation_type = "AB"
      citation_id = ''.join([citation_type, "-", str(citation_ab_count)])
      citation_dict["item"] = {
        "type": citation_type,
        "abbreviation": citation_abbreviation,
        "title": citation_info[0],
        "description": citation_info[1],
        "href": citation_href,
        "id": citation_id
      }
      citation_dict["output"] = setCitation(citation_id, citation_info[0])
      citation_ab_list.append(citation_dict)
      citation_ab_count = citation_ab_count + 1

response_dict = {}
response_dict["reference_list"] = citation_rd_list
response_dict["applicable_list"] = citation_ad_list
response_dict["abbreviation_list"] = citation_ab_list
return response_dict
