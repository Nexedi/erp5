"""
  This script is called before a Role Definition object is about to be deleted.
  It is responsible to trigger an activity (later not within this transaction)
  that will update security groups.
"""
role_definition_parent = state_change['object'].getParentValue()
role_definition_parent.activate().updateLocalRolesOnSecurityGroups()
