## Script (Python) "assign_gestionaire_designe_roles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user_name=''
##title=
##
object = context

equipe1=['Michele_Kmiecik', 'Laurence_Caron', 'Veronique_Tronet']
equipe2=['Martine_Cirot', 'Michele_Grisolet']
equipe3=['Maryvonne_Mathon', 'Magdalena_Cousin', 'Carole_Billant']

local_user = object.portal_membership.getAuthenticatedMember().getUserName()

if user_name <> '' :
  if user_name in equipe1 or user_name in equipe2 or user_name in equipe3 :
    local_user = user_name

if local_user in equipe1 :
  object.AssignLocalRole(user_list=equipe1,role_list=['GestionaireDesigne',])
elif local_user in equipe2 :
  object.AssignLocalRole(user_list=equipe2,role_list=['GestionaireDesigne',])
elif local_user in equipe3 :
  object.AssignLocalRole(user_list=equipe3,role_list=['GestionaireDesigne',])
else :
  if user_name == "AnimatriceAppros" :
    local_user = 'Michele_Kmiecik'
  object.AssignLocalRole(user_list=[local_user,],role_list=['GestionaireDesigne',])
