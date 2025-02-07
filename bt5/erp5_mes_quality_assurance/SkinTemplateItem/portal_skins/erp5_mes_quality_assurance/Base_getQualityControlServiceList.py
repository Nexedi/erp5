from Products.ERP5Type.Cache import CachingMethod
from AccessControl import getSecurityManager

portal = context.getPortalObject()

def getQualityControlServiceList():
  service_list = portal.portal_catalog(
    portal_type='Service',
    strict_use_uid=portal.portal_categories.use.manufacturing.quality_control.getUid(),
    validation_state = ('draft', 'validated'),
    sort_on = (('creation_date', 'descending'),)
  )
  new_service_list = []

  for x in service_list:
    transformation_line = x.getResourceRelatedValue(portal_type='Transformation Operation')
    if transformation_line and transformation_line.getTradePhase() == 'manufacturing/electronic_insurance':
      continue
    new_service_list.append(x.getId())
  return new_service_list

getQualityControlServiceList = CachingMethod(
  getQualityControlServiceList,
  id='getQualityControlServiceList-%s-%s' % (
    portal.service_module.getLastId(),
    getSecurityManager().getUser().getIdOrUserName()),
  cache_factory='erp5_ui_long')

id_list = getQualityControlServiceList()
return [portal.service_module[service_id] for service_id in id_list]
