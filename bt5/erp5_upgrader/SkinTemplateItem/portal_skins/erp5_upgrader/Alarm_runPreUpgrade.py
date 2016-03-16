"""
  Run Pre upgrade
"""
context.ERP5Site_checkUpgraderConsistency(fixit=True,
  activate_kw=activate_kw,
  active_process=context.newActiveProcess(),
  filter_dict={"constraint_type": "pre_upgrade"})

context.setEnabled(False)
return
