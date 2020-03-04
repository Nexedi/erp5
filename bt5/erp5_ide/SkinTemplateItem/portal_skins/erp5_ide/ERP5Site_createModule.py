request = container.REQUEST

portal = context.getPortalObject()
portal_types = portal.portal_types
object_portal_type_id = object_portal_type

# Create a new portal_type for the module
module_portal_type_value = portal_types.newContent(id=module_portal_type, portal_type='Base Type')
# Set icon and allowed content types
module_portal_type_value.edit(
  type_factory_method_id='addFolder',
  type_icon='folder_icon.gif',
  type_filter_content_type=1,
  type_allowed_content_type_list=(object_portal_type_id,),
  type_base_category_list=('business_application',),
  type_group='module')
# initialize translation domains
module_portal_type_value.setTranslationDomain('title', 'erp5_ui')
module_portal_type_value.setTranslationDomain('short_title', 'erp5_ui')

module_list_form_id = ('%s_view%sList' % (module_portal_type,
                        object_portal_type)).replace(' ', '')

module_portal_type_value.newContent(portal_type='Action Information',
  reference="view",
  title="View",
  action="string:${object_url}/%s" % module_list_form_id,
  action_type="object_list")

# Create the skin folder if does not exist yet
portal_skins_folder_name = portal_skins_folder
portal_skins = portal.portal_skins
if not portal_skins_folder_name in portal.portal_skins.objectIds():
  portal_skins.manage_addFolder(portal_skins_folder_name)
skin_folder = portal.portal_skins[portal_skins_folder_name]
# Add new folders into skin paths.
for skin_name, selection in portal_skins.getSkinPaths():
  selection = selection.split(',')
  if portal_skins_folder_name not in selection:
    new_selection = [portal_skins_folder_name,]
    new_selection.extend(selection)
    portal_skins.manage_skinLayers( skinpath = tuple(new_selection)
                                  , skinname = skin_name
                                  , add_skin = 1
                                  )

factory = skin_folder.manage_addProduct['ERP5Form']

# Create a form for the module
factory.addERP5Form(module_list_form_id, title=module_title)
form = skin_folder[module_list_form_id]
default_groups = ['bottom', 'hidden']
for group in default_groups:
  form.add_group(group)

# XXX this is too low level, but we don't have an API available from restricted
# environment. Afterall, this script should not use restricted environment
form.manage_settings(
    dict(field_title=form.title,
         field_name=form.name,
         field_description=form.description,
         field_action='Base_doSelect',
         field_action_title=form.action_title,
         field_update_action=form.update_action,
         field_update_action_title=form.update_action_title,
         field_enctype=form.enctype,
         field_encoding=form.encoding,
         field_stored_encoding=form.stored_encoding,
         field_unicode_mode=form.unicode_mode,
         field_method=form.method,
         field_row_length=str(form.row_length),
         field_pt='form_list',
         field_edit_order=[]))

form.manage_addField(
         id='listbox',
         fieldname='ProxyField',
         title='')
form.move_field_group(('listbox',), 'left', 'bottom')

form.listbox.manage_edit_xmlrpc(
    dict(form_id='Base_viewFieldLibrary',
         field_id='my_list_mode_listbox'))

form.listbox.manage_edit_surcharged_xmlrpc(
    dict(selection_name=('_'.join(module_portal_type.split())).lower() + '_selection',
         title=module_title,
         portal_type=[(object_portal_type, object_portal_type), ], ))


# Create a form for the document
form_view_id = object_portal_type_id.replace(' ','') + '_view'
factory.addERP5Form(form_view_id, title=object_title)
form = skin_folder[form_view_id]
form.rename_group('Default', 'left')
default_groups = ['right', 'center', 'bottom', 'hidden']
for group in default_groups:
  form.add_group(group)

form.manage_settings(
    dict(field_title=form.title,
         field_name=form.name,
         field_description=form.description,
         field_action='Base_edit',
         field_action_title=form.action_title,
         field_update_action=form.update_action,
         field_update_action_title=form.update_action_title,
         field_enctype=form.enctype,
         field_encoding=form.encoding,
         field_stored_encoding=form.stored_encoding,
         field_unicode_mode=form.unicode_mode,
         field_method=form.method,
         field_row_length=str(form.row_length),
         field_pt='form_view',
         field_edit_order=[]))

form.manage_addField(
         id='my_title',
         fieldname='StringField',
         title='Title')


# Then add the portal_type corresponding to the new object
object_portal_type_value = portal_types.newContent(id=object_portal_type_id, portal_type='Base Type', type_factory_method_id='addXMLObject')

# Chain to edit_workflow
portal.portal_workflow.setChainForPortalTypes([object_portal_type_id],
                                              'edit_workflow')

# Set default actions
object_portal_type_value.newContent(portal_type='Action Information',
  reference="view",
  title="View",
  action="string:${object_url}/%s" % form_view_id,
  action_type="object_view")

# Finally add the module to the site
module_object = portal.newContent( portal_type = module_portal_type
                                   , id          = module_id
                                   , title       = module_title
                                   )
module_object.Base_setDefaultSecurity()

# Clear caches so that module is immediatly visible
portal.changeSkin(None)
portal.portal_caches.clearAllCache()

if not selection_index:
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Module+Created.'
                              )
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( context.absolute_url()
                          , form_id
                          , selection_index
                          , selection_name
                          , 'portal_status_message=Module+Created.'
                          )


request[ 'RESPONSE' ].redirect( redirect_url )
