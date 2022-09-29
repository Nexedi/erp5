"""
================================================================================
Create A Webbook Layout Based on Websection Predicate and keywords
================================================================================
"""
from Products.PythonScripts.standard import html_quote

web_section = context
web_section_document_list = web_section.getDocumentValueList() or []
web_section_default_document = web_section.getDefaultDocumentValue() or None
web_section_default_document_content = ''

section_entry = '''<h%(digit)s class="ci-web-page-book-toc-group">%(title)s</h%(digit)s><ul>'''
group_entry = '''<li class="ci-web-page-book-toc-element"><a href="#%(reference)s">%(title)s</a></li>'''
section_close = '''</ul>'''
content_title_entry = '''<h%(digit)s class="ci-web-page-book-content-title">%(title)s</h%(digit)s><a id="%(reference)s">&para;</a>'''

if web_section_default_document is not None:
  web_section_default_document_content = web_section_default_document.getTextContent()

if len(web_section_document_list) > 0:
  book_toc = []
  book_content = []

  # First grouping order is by web_section keywords
  web_section_keyword_list = web_section.getSubjectList() or ["ungrouped"]
  if len(web_section_keyword_list) > 0:
    web_section_keyword_dict = {
      "rule": [],
      "recommendation": [],
      "crime": [],
      "ungrouped": []
    }
    for web_section_keyword in web_section_keyword_list:
      web_section_keyword_dict[web_section_keyword] = web_section_keyword_dict.get(web_section_keyword, [])

    # get keywords of all pages
    for page in web_section_document_list:
      page_subject_list = page.getSubjectList() or []
      if len(page_subject_list) > 0:

        # find out which section keyword a page belongs to
        page_subject_in_section_subject = None
        for subject in page_subject_list:
          if subject in web_section_keyword_list:
            page_subject_in_section_subject = subject
        page_subject_in_section_subject = page_subject_in_section_subject or "ungrouped"

        page_dict = {}
        page_dict["title"] = html_quote(page.getTitle())
        page_dict["short_title"] = html_quote(page.getShortTitle())
        page_dict["description"] = html_quote(page.getDescription())
        page_dict["subject_list"] = page_subject_list
        page_dict["reference"] = html_quote(page.getReference())
        page_dict["text_content"] = page.getTextContent()

        # now add all keywords and the page to this group
        web_section_keyword_dict[page_subject_in_section_subject].append(page_dict)

    # group_count
    group_count = 0
    for group in web_section_keyword_dict:
      group_count += 1

    for group in web_section_keyword_dict:
      has_entry = None
      group_page_list = web_section_keyword_dict[group]
      group_keyword_list = []
      if len(group_page_list) > 0:
        if group == "ungrouped" and group_count == 1:
          group_header_init = 0
        else:
          group_header_init = 1

          if group == "ungrouped":
            group_title = "additional rules"
          else:
            group_title = group

          # initialize group header
          book_toc.append(section_entry % {
            "digit": group_header_init,
            "title": group_title.title()
          })
          has_entry = True

        # build list of keywords per page
        for page in group_page_list:
          for keyword in page.get("subject_list"):
            if (keyword not in web_section_keyword_list):
              if (keyword not in group_keyword_list):
                group_keyword_list.append(keyword)

        # add entries
        group_keyword_list.sort()
        for keyword in group_keyword_list:
          group_title_dict = {
            "digit": group_header_init + 1,
            "reference": "reference-" + keyword.replace(" ", "_"),
            "title": keyword.title()
          }
          book_toc.append(group_entry % group_title_dict)
          book_content.append(content_title_entry % group_title_dict)

          # XXX cumbersome - add all pages listed on this keyword
          for page in group_page_list:
            if keyword in page.get("subject_list"):
              book_content.append(page.get("text_content"))

        if has_entry is not None:
          book_toc.append(section_close)

  return web_section_default_document_content + ''.join(book_toc) + ''.join(book_content)

return web_section_default_document_content


#===============================================================================

# ======================================================================

#        def pushDown(level):
#          return ''.join(["h", str(level), ">"])
#
#        def downgradeHeader(my_content, my_downgrade):
#          if my_downgrade is None:
#            my_downgrade = 1
#
#          header_list = re.findall("<h[1-6].*</h[1-6]>", my_content or "")
#          for header in header_list:
#            header_tag = re.findall("<(h[1-6]>)", header)[0] #h2>
#            header_key = header_tag[1]
#            new_header = header.replace(header_tag, pushDown(int(header_key) + my_downgrade))
#            my_content = my_content.replace(header, new_header)
#
#          return my_content or ""
#
#        web_section = document.getWebSectionValue()
#        web_section_document_list = web_section.getDocumentValueList() or []
#        page_keyword_ignore_list = ["rule", "crime", "recommendation"]
#
#        book_anchor = '''<a name="reference-main-anchor"></a><br/><br/>'''
#        section_placeholder = '''<span class="ci-web-page-book-toc-group"></span>'''
#        section_start = '''<hr/><ul>'''
#        section_entry = '''
#          <h%(digit)s class="ci-web-page-book-toc-group">
#            <a href="#%(reference)s">%(title)s</a>
#          </h%(digit)s>'''
#        section_pointer = '''
#          <a name="%(reference)s"></a>
#          <h%(digit)s class="ci-web-page-book-content-group">%(title)s</h%(digit)s>
#          <span>
#            [<a href="%(local_url)s#%(reference)s">&para;</a>]
#            [<a href="%(local_url)s#reference-main-anchor">top</a>]
#          </span>'''
#        section_end = '''</ul><hr/>'''
#        keyword_entry = '''
#          <li class="ci-web-page-book-keyword-toc-element">
#            <a href="%(url)s">%(title)s</a>&nbsp;
#            [<a href="#%(reference)s">
#              <span style="font-size:10px;">goto</span>
#            </a>]&nbsp;-&nbsp;%(description)s
#          </li>'''
#        group_anchor = ''
#        group_entry = '''
#          <li class="ci-web-page-book-toc-element">
#            <a href="#%(reference)s">%(title)s</a>&nbsp;(%(count)s)
#          </li>'''
#
#        content_title_entry = '''
#          <a name="%(reference)s"></a>
#          <h%(digit)s class="ci-web-page-book-content-title">%(title)s</h%(digit)s>
#          <span>
#            [<a href="%(local_url)s#%(reference)s">&para;</a>]
#            [<a href="%(local_url)s#%(group_anchor)s">section</a>]
#          </span>
#          '''
#
#        if len(web_section_document_list) > 0:
#          book_toc = []
#          book_content = []
#          web_section_url = document.absolute_url()
#
#          # group by websection keywords if specified
#          web_section_keyword_list = web_section.getSubjectList() or []
#          web_section_keyword_dict = {"ungrouped": []}
#          #web_section_keyword_dict = {
#          #  "rule": [],
#          #  "crime": [],
#          #  "recommendation": []
#          #}
#          for web_section_keyword in web_section_keyword_list:
#            web_section_keyword_dict[web_section_keyword] = web_section_keyword_dict.get(web_section_keyword, [])
#
#          # add predicate pages by their keyword to web section keyword dict
#          for page in web_section_document_list:
#            page_subject_list = page.getSubjectList() or []
#            #page_matched_to_websection_keyword = None
#            page_dict = {}
#            page_dict["title"] = html_quote(page.getTitle())
#            page_dict["short_title"] = html_quote(page.getShortTitle())
#            page_dict["description"] = html_quote(page.getDescription())
#            page_dict["subject_list"] = page_subject_list
#            page_dict["reference"] = html_quote(page.getReference())
#            page_dict["text_content"] = page.getTextContent()
#
#            if len(web_section_keyword_list) == 0:
#              web_section_keyword_dict["ungrouped"].append(page_dict)
#            else:
#              if len(page_subject_list) > 0:
#                for subject in page_subject_list:
#                  if web_section_keyword_dict.get(subject) is not None:
#                    #page_matched_to_websection_keyword = True
#                    web_section_keyword_dict[subject].append(page_dict)
#
#              # no keywords set on page or keyword not matching websection keyword
#              #if len(page_subject_list) == 0 or page_matched_to_websection_keyword is None:
#              #  web_section_keyword_dict["ungrouped"].append(page_dict)
#
#
#          # all pages allocated to web section keywords, now split by page keyword
#          # override for JP and split into rule recommendation and crime
#          for group in web_section_keyword_dict:
#            group_page_list = web_section_keyword_dict.get(group)
#            group_has_header = None
#            group_keyword_list = []
#
#            if len(group_page_list) > 0:
#
#              # web section keywords are first grouping order
#              if len(web_section_keyword_list) > 0:
#                if group == "ungrouped":
#                  group_title = "additional rules"
#                else:
#                  group_title = group
#                group_anchor = "anchor-" + group_title.replace(" ", "_")
#                section_config = {
#                  "digit": 2,
#                  "title": group_title.title(),
#                  "reference": group_anchor,
#                  "local_url": web_section_url
#                }
#                book_toc.append(section_entry % section_config)
#                book_content.append(section_pointer % section_config)
#                group_has_header = True
#              else:
#                book_toc.append(section_placeholder)
#
#              book_toc.append(section_start)
#
#              # build list of keywords per group, exclude web section keywords
#              for page_dict in group_page_list:
#                for keyword in page_dict.get("subject_list"):
#                  if keyword not in web_section_keyword_list:
#                    if keyword not in page_keyword_ignore_list:
#                      if (keyword not in group_keyword_list):
#                        group_keyword_list.append(keyword)
#
#              group_keyword_list.sort()
#              for keyword in group_keyword_list:
#                book_keyword_toc = []
#                book_keyword_content = []
#                keyword_page_count = 0
#
#                group_title_dict = {
#                  "digit": 3 if group_has_header else 2,
#                  "reference": group_anchor + "_" + keyword.replace(" ", "_"),
#                  "title": keyword.title(),
#                  "local_url": web_section_url,
#                  "count": "",
#                  "group_anchor": group_anchor
#                }
#                book_keyword_toc.append(content_title_entry % group_title_dict)
#                book_keyword_toc.append("<hr/><ul>")
#
#                # XXX improve - match pages in the web section keyword to the page group keyword
#                for page in group_page_list:
#                  page_reference = page.get("reference")
#                  page_anchor = group_anchor + "-" + page_reference.replace(" ", "_")
#                  page_url = "../" + page_reference
#
#                  if keyword in page.get("subject_list"):
#                    keyword_page_count += 1
#                    book_keyword_toc.append(keyword_entry % {
#                      "reference": "reference-" + page_anchor,
#                      "title": page.get("short_title"),
#                      "description": page.get("description"),
#                      "url": page_url
#                    })
#                    book_keyword_content.append(
#                      '<a name="reference-' + page_anchor + '"></a>' +
#                      downgradeHeader(page.get("text_content"), 3 if group_has_header else 2)
#                    )
#                group_title_dict["count"] = keyword_page_count
#                book_toc.append(group_entry % group_title_dict)
#                book_keyword_toc.append("</ul><hr/>")
#                book_content.append(''.join(book_keyword_toc) + ''.join(book_keyword_content))
#              book_toc.append(section_end)
#
#          document_content = document_content.replace(
#           '${predicate_view_as_book}',
#            book_anchor + ''.join(book_toc) + '<br/><br/>' + ''.join(book_content)
#          )

#===============================================================================


#def generateBookByKeyword(complete_keyword_dict):
#  keyword_list = complete_keyword_dict.keys()
#  keyword_list.sort()
#
#  return_value_list = []
#  for keyword in keyword_list:
#    return_value_list.append(list_start % (keyword.title()))
#    for page in complete_keyword_dict[keyword]:
#      return_value_list.append(
#        list_item_template % (
#          html_quote(page.getReference()),
#          html_quote(page.getTitle()),
#          html_quote(page.getShortTitle() or page.getTitle()),
#          html_quote(page.getDescription())
#        )
#      )
#    return_value_list.append(list_end)
#
#  return ''.join(return_value_list)
#
#web_section = context
#web_section_document_list = web_section.getDocumentValueList() or []
#web_section_default_document = web_section.getDefaultDocumentValue() or None
#web_section_default_document_content = ''
#
#section_start = '''<h1 class="ci-web-page-content-section">%s</h1>'''
#list_start = '''<h2 class="ci-web-page-content-book">%s</h2><ul class="ci-web-page-content-book-list">'''
#list_item_template = '''<li><a href="%s" title="%s">%s</a>&nbsp;-&nbsp;%s</li>'''
#list_end = '</ul>'
#
#if web_section_default_document is not None:
#  web_section_default_document_content = web_section_default_document.getTextContent()
#
#if len(web_section_document_list) > 0:
#  book_content = []
#
#  # First grouping order is by web_section keywords
#  web_section_keyword_list = web_section.getSubjectList() or []
#  if len(web_section_keyword_list) > 0:
#    web_section_keyword_dict = {
#      "rule": [],
#      "recommendation": [],
#      "crime": []
#    }
#    for web_section_keyword in web_section_keyword_list:
#      web_section_keyword_dict[web_section_keyword] = web_section_keyword_dict.get(web_section_keyword, [])
#
#    for page in web_section_document_list:
#      page_subject_list = page.getSubjectList() or []
#      if len(page_subject_list) > 0:
#
#        # find correct section keyword to add page to
#        for subject in page_subject_list:
#          if subject in web_section_keyword_list:
#            web_section_keyword_dict[subject].append(page)
#
#    for group in web_section_keyword_dict:
#      group_page_list = web_section_keyword_dict[group]
#      if len(group_page_list) > 0:
#        keyword_dict = {}
#        for page in group_page_list:
#          page_subject_list = page.getSubjectList() or []
#          if len(page_subject_list) > 0:
#            for subject in page_subject_list:
#              key = subject
#              if key not in web_section_keyword_list:
#                page_list = keyword_dict[key] = keyword_dict.get(key, [])
#                page_list.append(page)
#        book_content.append(section_start % (group.title()))
#        book_content.append(generateBookByKeyword(keyword_dict))
#
#    book_content = ''.join(book_content)
#
#  return web_section_default_document_content + book_content
#
#  keyword_dict = {}
#  for page in web_section_document_list:
#    page_subject_list = page.getSubjectList() or []
#
#    if len(page_subject_list):
#      for subject in page_subject_list:
#        key = subject
#        # get or initialize a list for pages of this keyword
#        page_list = keyword_dict[key] = keyword_dict.get(key, [])
#        page_list.append(page)
#
#  book_content = generateBookByKeyword(keyword_dict)
#
#  return web_section_default_document_content + book_content
