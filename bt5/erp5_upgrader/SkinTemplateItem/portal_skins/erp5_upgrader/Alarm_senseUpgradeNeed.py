"""
  Check if upgrader is required
"""
constraint_type = context.getId().replace("upgrader_check_", "")
context.ERP5Site_checkUpgraderConsistency(
    active_process=context.newActiveProcess(),
    filter_dict={"constraint_type": constraint_type})
