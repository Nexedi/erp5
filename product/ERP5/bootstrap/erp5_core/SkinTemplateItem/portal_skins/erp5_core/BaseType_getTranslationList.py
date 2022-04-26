from Products.ERP5Type.Document import newTempBase

translation_list = [
  newTempBase(context, 'property_domain_dict/'+k, uid=k,
              property_name=v.getPropertyName(),
              domain_name=v.getDomainName())
  for k, v in list(context.getPropertyTranslationDomainDict().items())]

translation_list.sort(key=lambda x: x.getId())
return translation_list
