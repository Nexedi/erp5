# pylint:disable=redefined-builtin
"""
  Adds a chapter in the listbox, and upload an image if necessary (it doesn't generate the html code corresponding to the text)
"""

from Products.ERP5Type.Document import newTempBase

portal_status_message = ""

if image_caption in [None, ""]:
  image_caption = chapter_title

session = context.ERP5Site_acquireRunMyDocsSession()
if 'listbox' in session and len(session['listbox']) > 0:
  listbox = session['listbox']
  int_index = listbox[-1].int_index + 1
else:
  listbox = []
  int_index = 1

image_id = ''

if slide_type in ['Illustration','Screenshot']:
  test_page_path = session['test_page_path']
  test_page = context.restrictedTraverse(test_page_path)

if slide_type in ['Illustration', 'Screenshot']:
  if image_url != "":
    image_id = image_url
  else:
    image_id = test_page.TestPage_getNextImageID(chapter_title, slide_type)
    test_page.TestPage_uploadImage(image_id, file, batch_mode=True, image_caption=image_caption)

listbox.append(newTempBase(context.getPortalObject(),
                   '',
                   title = chapter_title,
                   uid = str(int_index),
                   int_index = int_index,
                   image_id = image_id,
                   image_title = image_caption,
                   slide_type = slide_type,
                   text_content = text_content,
                   slide_content = slide_content,
                   file = not(file is None or not file),
                   tested = bool(tested)
                 ))

session['listbox'] = listbox
return context.Base_redirect('TestPageModule_viewChapterCreationWizardDialog',
                             keep_items = dict(portal_status_message=portal_status_message))
