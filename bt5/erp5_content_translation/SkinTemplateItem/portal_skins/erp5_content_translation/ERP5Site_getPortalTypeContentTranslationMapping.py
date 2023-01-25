from Products.ERP5Type.Cache import CachingMethod

def getPortalTypeContentTranslationMapping():
  result = {}
  for type_information in context.getPortalObject().portal_types.listTypeInfo():
    for property_name, translation_domain in type_information.getPropertyTranslationDomainDict().items():
      domain_name = translation_domain.getDomainName()
      if domain_name:
        result.setdefault(type_information.getId(), []).append(property_name)
  return result

getPortalTypeContentTranslationMapping = CachingMethod(
  getPortalTypeContentTranslationMapping,
      id=script.id,
      cache_factory='erp5_content_long')
return getPortalTypeContentTranslationMapping()
