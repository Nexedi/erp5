"""
================================================================================
Create HTML table of content (to be used on web pages instead of xsl for pdf)
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# doc_content                 text content of document being rendered
# doc_url                     absolute url of document
# doc_toc_title               translated title for table of content

import re
from Products.PythonScripts.standard import html_quote

blank = ""
header_current = 1
header_initial = None
table_of_content = blank

for header in re.findall("<h[1-6].*?</h[1-6]>", doc_content or blank):
  header_level = header[2]
  header_initial = header_initial or header_level
  header_reference = re.findall(">(.*)<", header)[0]
  header_lowercase = header_reference.lower()
  header_reference_prefix = header_lowercase.replace(" ", "-")

  if header_level == header_current:
    table_of_content += '</li>'

  # start of a list
  if header_level > header_current:
    header_current = header_level
    table_of_content += '<ol>'

  # end of a list
  if header_level < header_current:
    iterations = (int(header_current) - int(header_level))
    table_of_content += '</li></ol>' * iterations
    header_current = header_level

  # add anchor in content
  snippet = ''.join(['>', header_reference])
  named_snippet = ''.join([
    '>',
    '<a name="', html_quote(header_reference_prefix), '"></a>',
    header_reference,
    '<a class="custom-para" href="', doc_url, '#', header_reference_prefix, '"><span style="font-size:.75em;line-height:1em;padding-left:.5em;">&para;</span></a>' 
  ])
  doc_content = doc_content.replace(snippet, named_snippet)
  
  # create table of content entry
  table_of_content += ''.join([
    '<li><div><a href="#',
    html_quote(header_reference_prefix),
    '">',
    html_quote(header_reference),
    '</div></a>']
  )

closer = int(header_current) * '</ol>'
insert = ''.join([
  '<section class="ci-book-table-of-content">',
  '<p class="ci-book-toc-faux-h1">%s</p>' % (doc_toc_title or "XXX"),
  table_of_content, 
  closer,
  '</section>'
])

return doc_content, insert
