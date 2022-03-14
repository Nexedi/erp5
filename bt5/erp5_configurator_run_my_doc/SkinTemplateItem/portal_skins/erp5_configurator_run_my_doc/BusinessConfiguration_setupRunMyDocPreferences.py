portal = context.getPortalObject()
configuration_save_url = kw.get('configuration_save_url', None)
preferred_event_sender_email = kw.get('preferred_event_sender_email', '')
preferred_date_order = kw.get('preferred_date_order', None)
default_available_language = kw.get('default_available_language', 'en')

context.setGlobalConfigurationAttr(default_available_language=default_available_language)

configuration_save = context.restrictedTraverse(configuration_save_url)
business_configuration = configuration_save.getParentValue()

# if preferred email is not specified used previously saved company email.
company_email = context.getGlobalConfigurationAttr('company_email')
if preferred_event_sender_email in ('', None,):
  preferred_event_sender_email = company_email

# configure preferences
prefs = dict(
  preferred_category_child_item_list_method_id = 'getCategoryChildTranslatedLogicalPathItemList',
  preferred_text_format = 'text/html',
  preferred_text_editor = 'fck_editor',
  preferred_date_order = preferred_date_order,
  preferred_listbox_view_mode_line_count = 20,
  preferred_listbox_list_mode_line_count = 20,
  preferred_string_field_width = 30,
  preferred_textarea_width = 80,
  preferred_textarea_height = 5,
  preferred_report_style = 'ODT',
  preferred_report_format = 'pdf',
  preferred_money_quantity_field_width = 10,
  preferred_html_style_access_tab = 1,
  preferred_quantity_field_width = 8)

configuration_save.addConfigurationItem(
    'Preference Configurator Item',
    object_id = 'default_configurator_preference',
    description = "The default parameters for the site are set on this "
    "preference",
    title = "Default Configurator Site Preference",
    **prefs)

# configure system preferences
# some preparation
system_prefs = dict(
  preferred_event_sender_email = preferred_event_sender_email,
  preferred_event_assessment_form_id_list = [],
  preferred_document_file_name_regular_expression = \
      '(?P<node_reference>[a-zA-Z0-9_-]+)-(?P<local_reference>[a-zA-Z0-9_.]+)'
      '-(?P<version>[0-9a-zA-Z.]+)-(?P<language>[a-z]{2})[^-]*?',
  preferred_document_reference_regular_expression = '(?P<reference>[a-zA-Z0-9'
      '-_.]+-[a-zA-Z0-9-_.]+)(|-(?P<version>[0-9a-zA-Z.]+))(|-(?P<language>[a'
      '-z]{2})[^-]*)?',
  preferred_synchronous_metadata_discovery = True,
  preferred_redirect_to_document = True)

configuration_save.addConfigurationItem('System Preference Configurator Item',
    object_id = 'default_configurator_system_preference',
    description="The default system parameters for the site are set on this '\
    'preference",
    title="Default Configurator System Site Preference",
    **system_prefs)

if default_available_language and default_available_language != "en":
  language_dict = context.BusinessConfiguration_getRunMyDocAvailableL10NBusinessTemplateList()
  bt5 = language_dict.get(default_available_language)
  if bt5:
    configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                             bt5_id=bt5.get("bt5"))
