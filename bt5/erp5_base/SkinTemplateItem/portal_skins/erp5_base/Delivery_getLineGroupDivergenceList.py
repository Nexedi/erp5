from Products.ERP5Type.Document import newTempBase

divergence_list =  context.getDivergenceList()
portal_object = context.getPortalObject()
l = []

for divergence in divergence_list:
  # XXX price is not built by builder, so collect order group is never set for price level divergence
  if divergence.getCollectOrderGroup() != 'line' and divergence.getProperty('tested_property') != 'price':
    continue
  decision_value = divergence.getProperty('decision_value')
  decision_title = divergence.getProperty('decision_title', decision_value)
  prevision_value = divergence.getProperty('prevision_value')
  prevision_title = divergence.getProperty('prevision_title', prevision_value)
  object_relative_url = divergence.getProperty('object_relative_url')
  simulation_movement_url = divergence.getProperty('simulation_movement').getRelativeUrl()
  uid = 'new_%s&%s' % (simulation_movement_url,
                       divergence.getProperty('tested_property'))

  document = portal_object.restrictedTraverse(object_relative_url)
  o = newTempBase(document.getParentValue(), document.getId(), uid=uid,
                  message=str(divergence.getTranslatedMessage()),
                  object_portal_type=document.getTranslatedPortalType(),
                  object_title=document.getTranslatedTitle(),
                  prevision_title=prevision_title,
                  decision_title=decision_title,
                  candidate_list=[(context.Base_translateString('Do nothing'), 'ignore'),
                                  (decision_title, 'accept'),
                                  (prevision_title, 'adopt'),])
  l.append(o)

return l
