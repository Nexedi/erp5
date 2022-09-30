knowledge_pads = context.ERP5Site_getKnowledgePadListForUser(
  mode=mode, default_pad_group=default_pad_group)
real_context = context.Base_getRealContext()
real_context_url = real_context.getRelativeUrl()

visible_pads = [x for x in knowledge_pads
  if x.getValidationState() in ('visible', 'public')]

# first filter if we have a custom Pad for the context
for knowledge_pad in visible_pads:
  publication_section_list = knowledge_pad.getPublicationSectionList()
  if real_context_url in publication_section_list:
    if real_context.getPortalType() == 'Web Site' and not default_pad_group:
      # ERP5 Web Site front gadget
      return knowledge_pad, knowledge_pads
    if knowledge_pad.getGroup() == default_pad_group:
      # some Web Section can have a customized EXPLICILY "sticked" Pad
      return knowledge_pad, knowledge_pads
  elif not publication_section_list and not default_pad_group:
    # ERP5 Site front gadget
    return knowledge_pad, knowledge_pads

# no customized version found for this context so
# try finding pad by group
for knowledge_pad in visible_pads:
  if knowledge_pad.getGroup() == default_pad_group:
    break
else:
  if create_default_pad and context.Base_isUserAllowedToUseKnowledgePad():
    knowledge_pad = context.ERP5Site_createDefaultKnowledgePadListForUser(
      default_pad_group=default_pad_group, mode=mode)
    knowledge_pads.append(knowledge_pad)
  else:
    knowledge_pad = None

return knowledge_pad, knowledge_pads
