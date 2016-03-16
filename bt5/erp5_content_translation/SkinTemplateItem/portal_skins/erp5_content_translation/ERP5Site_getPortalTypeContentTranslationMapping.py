from Products.ERP5Type.Cache import CachingMethod

def getPortalTypeContentTranslationMapping():
  result = {}
  for type_information in context.getPortalObject().portal_types.listTypeInfo():
    content_translation_domain_property_name_list =\
      type_information.getContentTranslationDomainPropertyNameList()
    if content_translation_domain_property_name_list:
      result[type_information.getId()] = content_translation_domain_property_name_list
  return result    

getPortalTypeContentTranslationMapping = CachingMethod(
  getPortalTypeContentTranslationMapping,
      id=script.id, 
      cache_factory='erp5_content_long')
return getPortalTypeContentTranslationMapping()
