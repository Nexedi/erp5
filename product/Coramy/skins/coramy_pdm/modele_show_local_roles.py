## Script (Python) "modele_show_local_roles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=roles=(), formated=1
##title=
##
raw_local_roles = context.get_local_roles()
used_roles = {}
if len(roles)<>0 :
  if 'ModelisteDesigne' in roles :
    used_roles['ModelisteDesigne']='Modeliste'
if len(roles)<>0 :
  if 'GestionaireDesigne' in roles :
    used_roles['GestionaireDesigne']='Gestionaire client'
else :
  used_roles['ModelisteDesigne']='Modeliste'
  used_roles['GestionaireDesigne']='Gestionaire client'
local_roles = {}
key_roles = used_roles.keys()

for user_roles in raw_local_roles:
  for role in key_roles:
    if role in user_roles[1]:
      local_roles[used_roles[role]]=[]
      local_roles[used_roles[role]].append(user_roles[0])

formated_roles=''

key_roles = local_roles.keys()
for role in key_roles:
  if formated==1 :
    formated_roles += role+':'
  for user in local_roles[role]:
    formated_roles += user +','
  formated_roles += ' '

  return str(formated_roles)
