"""
  Run Pre upgrade
"""
activate_kw = params or {}

with context.defaultActivateParameterDict(activate_kw, placeless=True):
  active_process = context.newActiveProcess(activate_kw=activate_kw)

context.ERP5Site_checkUpgraderConsistency(fixit=fixit,
  activate_kw=activate_kw,
  active_process=active_process,
  filter_dict={"constraint_type": "pre_upgrade"})

context.setEnabled(False)
