bt5_list, keep_bt5_id_set = context.Base_getUpgradeBusinessTemplateList()

template_tool = context.getPortalObject().portal_templates
return template_tool.upgradeSite(bt5_list,
  delete_orphaned=True,
  keep_bt5_id_set=keep_bt5_id_set,
  dry_run=(not fixit))
