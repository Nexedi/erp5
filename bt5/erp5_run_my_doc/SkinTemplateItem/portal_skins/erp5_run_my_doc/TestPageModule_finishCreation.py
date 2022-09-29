# pylint:disable=redefined-builtin
"""
   Generate the html code from the listbox after adding the current chapter to the listbox
"""

# Add the last chapter to the listbox
context.TestPageModule_createChapter(chapter_title, slide_type, image_url, image_caption,
                                     file, text_content, slide_content, tested, **kw)

portal_status_message = ""

session = context.ERP5Site_acquireRunMyDocsSession()
test_page = context.restrictedTraverse(session['test_page_path'])
listbox = session['listbox']
title = session['title']
author = session['author']
author_mail = session['author_mail']

# Headers and first chapter/slide
text_content = """<section class="master">
  <h1>""" + title + """</h1>
  """ + listbox[0].slide_content

if not (author is None or not author):
  if author_mail is None or not author:
    text_content +="""
  <footer>by """+ author +""".</footer>"""
  else:
    text_content +="""
  <footer>by <a href="mailto:"""+ author_mail +"""">"""+ author +"""</a>.</footer>"""

text_content +="""
  <details open="true">
    """+ listbox[0].text_content +"""
  </details>
</section>
"""

first = True
for chapter in listbox[1:]:
  title = chapter.title
  image_id = chapter.image_id
  text = chapter.text_content
  slide_content = chapter.slide_content
  slide_type = chapter.slide_type

  # title of this slide and content to appear in the slide
  text_content += '''
<section class="'''+ slide_type.lower() +"""">
  <h1>"""+ title +"""</h1>"""
  if not(image_id is None or not image_id):
    text_content +='''
  <img type="image/svg+xml" title="''' + chapter.image_title + '''" alt="''' + chapter.image_title + '''" src="'''+ image_id + '''?format=" width="90%"/>'''
  if not(slide_content is None or not slide_content):
    text_content += """
  """+ slide_content

  # details will only appear in the web page version of the tutorial
  text_content +="""
  <details open="true">
    """+ text +"""
  </details>"""

  # let's add a template test to this chapter
  if chapter.tested:
    text_content +="""
  <test>"""
    if first:
      text_content +="""
    <span metal:use-macro="container/ERP5Site_initRunMyDocsTest/macros/init_test_environment" style="display:none;"> init</span>"""
      first = False

    text_content +="""
    <table class="test" cellpadding="1" cellspacing="1" border="1" style="display:none;">
      <tbody>"""


    text_content += """
        <tr>
	  <td>selectAndWait</td>
	  <td>name=select_module</td>
	  <td>label=Test Pages</td>
        </tr>
        <tr>
          <td>verifyTextPresent</td>
          <td>Test Pages</td>
          <td></td>
        </tr>"""
    if slide_type == "Screenshot":
      text_content +="""
        <tr>
          <td>captureEntirePageScreenshot</td>
          <td>"""+ image_id +"""</td>
          <td></td>
        </tr>"""
    text_content += """
      </tbody>
    </table>
  </test>"""
  text_content +="""
</section>
"""

test_page.setTextContent(text_content)

return test_page.Base_redirect('view',
                               keep_items = dict(portal_status_message=portal_status_message))
