knowledge_pad = None
portal = context.getPortalObject()
system_pref = context.portal_preferences.getActiveSystemPreference()
user_pref = context.Base_getActiveGlobalKnowledgePadPreference()

is_web_mode = mode in ('web_front', 'web_section',)
if not is_web_mode:
  # leave only those not having a publication_section
  filter_pad = lambda x: x.getPublicationSection() is None and x.getGroup() is None
elif default_pad_group:
  filter_pad = lambda x: x.getGroup() == default_pad_group
else:
  # find from preferences for the same context(site, section, page)
  filter_pad = lambda x: context in x.getPublicationSectionValueList()

# try to find template KnowledgePad from System Preference (and user Preference
# for backward compatibility only).
for pref in (system_pref, user_pref):
  if pref is not None:
    # use template from preferences
    for pref_pad in pref.objectValues(portal_type='Knowledge Pad'):
      if filter_pad(pref_pad):
        break
    else:
      continue
    cp = pref.manage_copyObjects(ids=[pref_pad.getId()])
    new_id = context.knowledge_pad_module.manage_pasteObjects(
                                   cb_copy_data=cp)[0]['new_id']
    knowledge_pad = context.knowledge_pad_module[new_id]
    knowledge_pad.makeTemplateInstance()
    # set each contaned box's state manually to visible
    # by default their state as well pads would be invisible (default state)
    # pad's visibility is fixed in ERP5Site_toggleActiveKnowledgePad()
    for box in knowledge_pad.contentValues(portal_type='Knowledge Box'):
      box.visible()
    break
else:
  # created empty one because no template found
  knowledge_pad = context.knowledge_pad_module.newContent(
                            portal_type = 'Knowledge Pad',
                            title = context.Base_translateString('Tab 1'))
if is_web_mode:
  # in Web Mode we can have a temporary Web Site objects created based on current language
  real_context = context.Base_getRealContext()
  if real_context.getPortalType() == 'Web Site' and not default_pad_group:
    # script is called within Front Page Gadgets view
    knowledge_pad.setPublicationSectionValue(real_context)

  # create a default pad for user belonging to respective pad group
  # this pad will be available globally for other contexes using the same
  # layout definition
  knowledge_pad.setGroup(default_pad_group)

knowledge_pad.visible()
# set owner
if owner is not None:
  current_user = context.portal_membership.getAuthenticatedMember()
  knowledge_pad.manage_setLocalRoles(userid=owner, roles=['Owner'])
  knowledge_pad.manage_delLocalRoles([current_user.getIdOrUserName()])
  knowledge_pad.reindexObject()

# set default gadgets
context.ERP5Site_createDefaultKnowledgeBox(knowledge_pad)

# Calling immediateReindexObject explicitly is a coding crime.
# But it's safe for newly created objects and this script should
# be called rarely enough to not cause any performance issue.
# Any other solution would be more complicated.
# See also ERP5Site_addNewKnowledgePad
knowledge_pad.immediateReindexObject()

if REQUEST is None:
  return knowledge_pad
