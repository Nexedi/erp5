"""
  This script creates edit actions for the admin toolbox
  and adds some extra actions taken from the action_list
  defined in portal_types tool.

  The script is able to rewrite some actions by looking at the
  editable_absolute_url property stored on Context objects
  which are created for virtual pages. (ie. pages which
  are obtained through _aq_dynamic from Web Section or Web Page)
"""
# Init some variables
translateString = context.Base_translateString
result = []
portal_type = context.getPortalType()
translated_portal_type = context.getTranslatedPortalType()
request = context.REQUEST
current_web_section = request.current_web_section
current_web_section_translated_portal_type = current_web_section.getTranslatedPortalType()
action_dict = request.get('actions', {}) # XXX actions needs to be renamed to action_dict
exchange_action_list = action_dict.get('object_exchange', [])
button_action_list = action_dict.get('object_button', [])
portal_url = (context.getWebSiteValue() or context.getPortalObject()).absolute_url()
http_parameters = request.get('http_parameters', '')
http_parameters = http_parameters.replace('editable_mode', 'dummy_editable_mode')

# Try to get the original absolute_url if this is a permanent URL
absolute_url = context.absolute_url()
editable_absolute_url = getattr(context, 'editable_absolute_url', absolute_url)

# action title based on security

editable_mode = int(request.form.get('editable_mode',
                                     request.get('editable_mode', 0)))
edit_permission = context.portal_membership.checkPermission('Modify portal content', context)

# Append a button to edit the content of the current document for Web Page
if not editable_mode and edit_permission and portal_type == 'Web Page':
  result.append(dict(
    url = "%s/WebPage_viewEditor?editable_mode:int=1&%s"
            %(editable_absolute_url, http_parameters),
    icon = "%s/%s" % (portal_url, context.getIcon(relative_to_portal=True) or 'file_icon.gif'),
    title = translateString("Edit ${portal_type} content",
                                 mapping=dict(portal_type=translated_portal_type)),
    label = ""))

# Append a button to edit the current document
if not editable_mode:
  if edit_permission:
    edit_title = translateString("Edit ${portal_type} details",
                                 mapping=dict(portal_type=translated_portal_type))
  else:
    edit_title = translateString("Access ${portal_type} details",
                                 mapping=dict(portal_type=translated_portal_type))
  result.append(dict(
    url = "%s/view?editable_mode:int=1&%s"
            %(editable_absolute_url, http_parameters),
    icon = "%s/%s" % (portal_url, context.getIcon(relative_to_portal=True) or 'file_icon.gif'),
    title = edit_title,
    label = ""))
else:
  result.append(dict(
    url = "%s/view?editable_mode:int=0&%s" % (absolute_url, http_parameters),
    icon = "%s/%s" % (portal_url, context.getIcon(relative_to_portal=True) or 'file_icon.gif'),
    title = translateString("View ${portal_type}",
                            mapping=dict(portal_type=translated_portal_type)),
                            label = ""))

# Append a button to edit the parent section
if portal_type not in ('Web Section', 'Web Site'):
  result.append(dict(
    url = "%s/view?editable_mode=1" % current_web_section.absolute_url(),
    icon = "%s/%s" % (portal_url, current_web_section.getIcon(relative_to_portal=True)),
    title = translateString("Edit Parent ${portal_type}",
                             mapping=dict(portal_type=current_web_section_translated_portal_type)),
    label = ""))

# Append all icon buttons
for action in button_action_list:
  if action['id'] == 'webdav':
    result.append(dict(
      url = action['url'].replace(absolute_url, editable_absolute_url),
      icon = action['icon'],
      title = translateString(action['title']),
      label = ""))

# Append an exchange button
if len(exchange_action_list):
  action = exchange_action_list[0]
  url = action['url'].replace(absolute_url, editable_absolute_url)
  url = '%s?dialog_category=object_exchange&cancel_url=%s/view' % (url, absolute_url)
  result.append(dict(
    url = url,
    icon  = '%s/import_export.png' % portal_url,
    title = translateString('Import / Export'),
    label = ""))

return result
