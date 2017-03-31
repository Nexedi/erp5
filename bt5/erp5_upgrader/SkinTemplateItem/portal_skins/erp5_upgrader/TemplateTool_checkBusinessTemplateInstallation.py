bt5_list, keep_bt5_id_set = context.Base_getUpgradeBusinessTemplateList()

template_tool = context.getPortalObject().portal_templates

# First, upgrade business templates
message_list = template_tool.upgradeSite(bt5_list,
  delete_orphaned=True,
  keep_bt5_id_set=keep_bt5_id_set,
  dry_run=(not fixit))

if fixit:
  # if We have installed some business templates, we must also update
  # the catalog tables structures in the same transaction, because these tables
  # might be required for alarm framework to work and we may not be able to
  # execute the post upgrade alarm.
  message_list.extend(
    template_tool.TemplateTool_checkTableConsistency(fixit=fixit))

return message_list
