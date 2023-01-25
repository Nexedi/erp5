"""
  Create new report dialog
"""

MARKER = ['', None]
portal_gadgets = context.getPortalObject().portal_gadgets
portal_skins = context.getPortalObject().portal_skins

if create_skin_id not in MARKER:
  # create skin
  skin_folder = context.Base_createSkinFolder(create_skin_id)
else:
  skin_folder = getattr(portal_skins, selected_skin_id)

# create
if view_form_id in MARKER:
  view_form_id = 'ERP5Site_view%sGadget' % gadget_title.replace(' ', '')
if edit_form_id in MARKER:
  edit_form_id = 'ERP5Site_view%sGadgetPreferences' % gadget_title.replace(' ', '')

kw = {'id': gadget_id,
      'title': gadget_title,
      'portal_type': 'Gadget',
      'view_form_id': view_form_id,
      'edit_form_id': edit_form_id,
      'render_type': render_type,
      'gadget_type': ['erp5_front','web_front', 'web_section']}

gadget = portal_gadgets.newContent(**kw)
gadget.visible()

# XXX: set image (not appears?)
erp5_logo = context.logoERP5
image = gadget.newContent(portal_type='Image', id='default_image')
image.setData(str(erp5_logo))

# create code
if gadget_code_type=='erp5':
  skin_folder.manage_addProduct['ERP5Form'].addERP5Form(view_form_id)
  view_form = getattr(skin_folder, view_form_id)
  skin_folder.manage_addProduct['ERP5Form'].addERP5Form(edit_form_id)
  edit_form = getattr(skin_folder, edit_form_id)
  context.editForm(view_form, {'pt': 'gadget_view'})
  context.editForm(edit_form, {'pt': 'gadget_view'})
elif gadget_code_type=='zpt':
  skin_folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(view_form_id, gadget_title)
  skin_folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(edit_form_id, gadget_title)
elif gadget_code_type=='python':
  skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=view_form_id)
  script = getattr(skin_folder, view_form_id)
  script.ZPythonScript_edit('**kw', 'return "Replace this script (%s) with your code."' % view_form_id)
  skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=edit_form_id)
  script = getattr(skin_folder, edit_form_id)
  script.ZPythonScript_edit('**kw', 'return "Replace this script (%s) with your code."' % edit_form_id)

return gadget.Base_redirect('view',
                              keep_items=dict(portal_status_message="Gadget successfuly created"))
