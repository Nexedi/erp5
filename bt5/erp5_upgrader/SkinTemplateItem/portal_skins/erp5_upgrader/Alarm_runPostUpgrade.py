"""
  Run Post upgrade
"""
activate_kw = params or {}

with context.defaultActivateParameterDict(activate_kw, placeless=True):
  active_process = context.newActiveProcess()

context.ERP5Site_checkUpgraderConsistency(fixit=fixit,
  activate_kw=activate_kw,
  active_process=active_process,
  filter_dict={"constraint_type": "post_upgrade"})

context.setEnabled(False)
