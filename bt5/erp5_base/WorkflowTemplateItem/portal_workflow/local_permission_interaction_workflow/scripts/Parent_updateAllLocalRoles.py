"""
This script updates all local roles on the object. It requires Assignor
proxy role since it may be called by owner in draft state.
"""
state_change['object'].getParentValue().updateLocalRolesOnSecurityGroups()
