"""
  Creates a Test|Web Page (with no text) and generates the first chapter/slide
"""

portal_type = 'Test Page'

if context.getPortalType() == "Web Page Module":
  # This should be much more clever
  portal_type = 'Web Page'

from Products.ERP5Type.Document import newTempBase
translateString = context.Base_translateString
portal_status_message = translateString("%s created. You can now add your first chapter." % portal_type)

page = context.newContent(portal_type=portal_type,
                          title = title)

session = context.ERP5Site_acquireRunMyDocsSession()
session['title'] = title
session['author'] = author
session['author_mail'] = author_mail
session['test_page_path'] = page.getPath()
session['listbox'] = [newTempBase(context.getPortalObject(), '',
                   title = title,
                   uid = '0',
                   int_index = 0,
                   image_id = '',
                   slide_type = 'Master',
                   text_content = text_content,
                   slide_content = slide_content,
                   file = False,
                   tested = False
                 )]

return context.Base_redirect('TestPageModule_viewChapterCreationWizardDialog',
                             keep_items = dict(portal_status_message=portal_status_message))
