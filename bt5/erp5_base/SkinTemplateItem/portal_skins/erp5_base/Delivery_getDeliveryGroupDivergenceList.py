from Products.ERP5Type.Document import newTempBase

divergence_list =  context.getDivergenceList()
portal_object = context.getPortalObject()
l = []

candidate_dict = {}

for divergence in divergence_list:
  prop = divergence.getProperty('tested_property')
  if prop in (None, '') or divergence.getCollectOrderGroup() != 'delivery':
    continue
  _, candidate_list, value_list, decision_title_list, prevision_title_list = candidate_dict.get(prop, ['', [], [], [], []])
  decision_value = divergence.getProperty('decision_value')
  decision_title = divergence.getProperty('decision_title', decision_value)
  prevision_value = divergence.getProperty('prevision_value')
  prevision_title = divergence.getProperty('prevision_title', prevision_value)
  object_relative_url = divergence.getProperty('object_relative_url')
  simulation_movement_url = divergence.getProperty('simulation_movement').getRelativeUrl()
  document = portal_object.restrictedTraverse(object_relative_url)
  if decision_value not in value_list:
    candidate_list.append((decision_title, object_relative_url))
    value_list.append(decision_value)
  if decision_title not in decision_title_list:
    decision_title_list.append(decision_title)
  if prevision_value not in value_list:
    candidate_list.append((prevision_title, simulation_movement_url))
    value_list.append(prevision_value)
  if prevision_title not in prevision_title_list:
    prevision_title_list.append(prevision_title)
  candidate_dict[prop] = [divergence.getTranslatedMessage(), candidate_list, value_list, decision_title_list, prevision_title_list]

for prop, candidate_list in candidate_dict.items():
  uid = 'new_%s' % prop
  document = context

  o = newTempBase(context.getParentValue(), context.getId(), uid, uid=uid,
                  message=candidate_list[0],
                  object_title=document.getTranslatedTitle(),
                  decision_title=', '.join([str(x) for x in candidate_list[3]]),
                  prevision_title=', '.join([str(x) for x in candidate_list[4]]),
                  candidate_list=[(context.Base_translateString('Do nothing'), 'ignore')]+candidate_list[1])
  l.append(o)

return l
