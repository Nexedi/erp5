import re
from Products.PythonScripts.standard import html_quote

document = context
document_content = content
websection = document.getWebSectionValue()
document_url = html_quote(websection.getPermanentURL(context))

# table of content
# XXX we are back to adding TOC to all documents, which we don't want
# XXX fix this to be applied only if a page is viewed as chapter
document_header_list = re.findall("<h[1-6].*?</h[1-6]>", document_content or "")

if len(document_header_list) > 0:
  header_current = 1
  header_initial = None
  table_of_content = ''

  for header in document_header_list:
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
      table_of_content += '<ul>'

    # end of a list
    if header_level < header_current:
      iterations = (int(header_current) - int(header_level))
      table_of_content += '</li></ul>' * iterations
      header_current = header_level

    # add anchor in content
    snippet = ''.join(['>', header_reference])
    named_snippet = ''.join([
      '>',
      '<a name="', html_quote(header_reference_prefix), '"></a>',
      header_reference,
      '<a class="custom-para" href="', document_url, '#', header_reference_prefix, '"><span style="font-size:.75em;line-height:1em;padding-left:.5em;">&para;</span></a>'
    ])
    document_content = document_content.replace(snippet, named_snippet)

    # create table of content entry
    table_of_content += ''.join([
      '<li><a href="#',
      html_quote(header_reference_prefix),
      '">',
      html_quote(header_reference),
      '</a>']
    )

  closer = int(header_current) * '</ul>'
  insert = ''.join(['<p class="custom-table-of-contents">Table of Contents</p>', table_of_content, closer])

  document_content = document_content.replace('${table_of_content}', insert)

return document_content
