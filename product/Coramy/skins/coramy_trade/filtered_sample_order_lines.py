## Script (Python) "filtered_sample_order_lines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
filtered_models = {}
filtered_dates = {}
lines_list = context.sample_order_line_search()

for line in lines_list :
  line_object = line.getObject()
  if line_object <> None :
    order = line_object.aq_parent
    client = order.getDefaultValue('destination',portal_type=['Organisation'])
    modele = line_object.getDefaultValue('resource',portal_type=['Modele'])
    if modele <>None :
      etat_modele = modele.portal_workflow.getInfoFor(modele, 'modele_state')
      if etat_modele=='demande_etude' or etat_modele=='etude_modelisme' or etat_modele=='prototypage' or etat_modele=='brouillon':
        if not filtered_models.has_key(modele.getId()) :
          filtered_models[modele.getId()] = {}
          filtered_models[modele.getId()]['date'] = order.getStopDate()
          filtered_models[modele.getId()]['client'] = str(client.getTitle())
          filtered_models[modele.getId()]['etat'] = modele.portal_workflow.getInfoFor(modele, 'modele_state')
        else :
          filtered_models[modele.getId()]['client'] = filtered_models[modele.getId()]['client']+', '+str(client.getTitle())
          if filtered_models[modele.getId()]['date'] > order.getStopDate() :
            filtered_models[modele.getId()]['date'] = order.getStopDate()

return filtered_models
