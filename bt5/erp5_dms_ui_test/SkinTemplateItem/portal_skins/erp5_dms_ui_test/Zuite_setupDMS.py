# Setup System Preference
dms_system_preference_id = 'dms_system_preference_ui_tests'
portal_preferences = context.portal_preferences
dms_preference = portal_preferences.getActiveSystemPreference()
if dms_preference is None:
  dms_preference = portal_preferences.newContent(id = dms_system_preference_id,
                                                 portal_type = 'System Preference')
kw = dict(priority = 1,
          preferred_document_reference_regular_expression = '(?P<reference>[a-zA-Z0-9-_.]+-[a-zA-Z0-9-_.]+)(|-(?P<version>[0-9a-zA-Z.]+))(|-(?P<language>[a-z]{2})[^-]*)?',
          preferred_document_file_name_regular_expression = '(?P<node_reference>[a-zA-Z0-9_-]+)-(?P<local_reference>[a-zA-Z0-9_.]+)-(?P<version>[0-9a-zA-Z.]+)-(?P<language>[a-z]{2})[^-]*?',
          preferred_synchronous_metadata_discovery = True,
          preferred_redirect_to_document = True)
dms_preference.edit(**kw)
if dms_preference.getPreferenceState()=='disabled':
  dms_preference.enable()

# Setup Preference so we can setup Access Tab
dms_preference_id = 'dms_preference_ui_tests'
dms_preference = portal_preferences.getActivePreference()
if dms_preference is None:
  dms_preference = portal_preferences.newContent(
                    id = dms_preference_id,
                    portal_type = 'Preference')
kw=dict(priority = 1,
        preferred_html_style_access_tab=1,
        preferred_listbox_list_mode_line_count=10)
dms_preference.edit(**kw)
if dms_preference.getPreferenceState()=='disabled':
  dms_preference.enable()

# Publish all knowledge pad gadgets
for gadget in context.portal_gadgets.objectValues():
  if gadget.getValidationState() == 'invisible':
    gadget.visible()
    gadget.public()

print "Done"
return printed
