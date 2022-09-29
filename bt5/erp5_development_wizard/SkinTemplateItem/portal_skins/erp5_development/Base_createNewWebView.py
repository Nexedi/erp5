"""
  Create new report dialog
"""

MARKER = ['', None]
portal_skins = context.getPortalObject().portal_skins

if priority in MARKER:
  priority = 100.0

if create_skin_id not in MARKER:
  # create skin
  skin_folder = context.Base_createSkinFolder(create_skin_id)
else:
  skin_folder = getattr(portal_skins, selected_skin_id)

portal_type = context.getPortalType()

# create
if web_form_id in MARKER:
  web_form_id = '%s_view%sAsWeb' % (portal_type.replace(' ', ''),
                                    web_view_title.replace(" ", ""))

skin_folder.manage_addProduct['ERP5Form'].addERP5Form(web_form_id)
web_form = getattr(skin_folder, web_form_id)
context.editForm(web_form, {'action': 'Base_edit'})
context.editForm(web_form, {'pt': 'form_view'})

web_form.manage_addField('my_title', 'Title', 'ProxyField')
field = getattr(web_form, 'my_title')
field.manage_edit_xmlrpc(dict(
      form_id='Base_viewFieldLibrary', field_id='my_title'))

portal_type_document = context.portal_types[portal_type]
action = portal_type_document.newContent(portal_type="Action Information")
action.edit(reference="%s_view_as_web" % (web_view_title.lower().replace(" ", "_")),
            title=web_view_title,
            action="string:${object_url}/%s" % web_form_id,
            action_type="object_view",
            priority=priority,
            action_permission="View")

return context.Base_redirect(web_form_id,
                             keep_items=dict(portal_status_message="Web View Successfuly created"))
