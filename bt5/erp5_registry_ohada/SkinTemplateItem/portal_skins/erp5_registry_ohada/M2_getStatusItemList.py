portal = context.getPortalObject()
result = []
result.append(('Nouveau', '_new_action'))
result.append(('Partant', '_go_action'))
result.append(('Maintenu', '_action_maintain'))
result.append(('Modifié', '_action_modify'))
return result
