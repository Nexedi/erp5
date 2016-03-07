resource_dict = {}
resource_dict = {'resource_relative_url':resource, 'variation_text':variation_text}

if cache_dict is None:
  cache_dict = {}
cache_title_category_url = cache_dict.setdefault('cache_title_category_url',{})
cache_translated_title_category_url = cache_dict.setdefault('cache_translated_title_category_url',{})
cache_resource_portal_type = cache_dict.setdefault('cache_resource_portal_type', {})
cache_resource = cache_dict.setdefault('cache_resource', {})
cache_translated_portal_type = cache_dict.setdefault('cache_translated_portal_type', {})
cache_translated_simulation_state = cache_dict.setdefault('cache_translated_simulation_state', {})


#def getVariationTitleList(variation_text):
#  return [getTitleFromCategoryUrl(x) for x in variation_text.split('\n')]

def getTitleFromCategoryUrl(category):
  result = cache_title_category_url.get(category, None)
  if result is None:
    result = context.portal_categories.getCategoryValue(category).getTitle()
    cache_title_category_url[category] = result
  return result

def getTranslatedTitleFromCategoryUrl(category):
  result = cache_translated_title_category_url.get(category, None)
  if result is None:
    result = context.portal_categories.getCategoryValue(category).getTranslatedTitle()
    cache_translated_title_category_url[category] = result
  return result


for variation in variation_text.split('\n'):
  if variation.startswith('cash_status'):
    resource_dict['cash_status'] = variation
    resource_dict['cash_status_title'] = getTitleFromCategoryUrl(variation)
    resource_dict['cash_status_translated_title'] = getTranslatedTitleFromCategoryUrl(variation)
  elif variation.startswith('emission_letter'):
    resource_dict['emission_letter'] = variation
    resource_dict['emission_letter_title'] = getTitleFromCategoryUrl(variation)
    resource_dict['emission_letter_translated_title'] = getTranslatedTitleFromCategoryUrl(variation)
  elif variation.startswith('variation'):
    resource_dict['variation'] = variation
    resource_dict['variation_title'] = getTitleFromCategoryUrl(variation)
    resource_dict['variation_translated_title'] = getTranslatedTitleFromCategoryUrl(variation)

#resource_dict['variation_text_title'] = ' '.join(getVariationTitleList(resource))


current_resource_portal_type = cache_resource_portal_type.get(resource, None)
if current_resource_portal_type is None:
  portal = context.getPortalObject()
  resource_value = portal.restrictedTraverse(resource)
  current_resource_portal_type = resource_value.getPortalType()
  cache_resource_portal_type[resource] = current_resource_portal_type
  resource_info_dict = {}
  resource_info_dict['base_price'] = resource_value.getBasePrice()
  resource_info_dict['resource_title'] = resource_value.getTitle()
  resource_info_dict['resource_id'] = resource_value.getId()
  #context.log('resource_value',resource_value.getRelativeUrl())
  try:
    resource_info_dict['resource_translated_title'] = resource_value.getTranslatedTitle()
  except KeyError:
    resource_info_dict['resource_translated_title'] = resource_value.getTitle()
  resource_info_dict['price_currency_title'] = resource_value.getPriceCurrencyTitle()
  resource_info_dict['price_currency_id'] = resource_value.getPriceCurrencyId()
  resource_info_dict['price_currency'] = resource_value.getPriceCurrency()
  resource_info_dict['resource_portal_type'] = current_resource_portal_type
  cache_resource[resource] = resource_info_dict

# Should not be None
resource_dict.update(cache_resource.get(resource))
  
##############
#movement =None
#resource_dict['explanation_translated_relative_url'] = 'xx'
###########
if movement is not None: # case of history
#  movement = portal.restrictedTraverse(movement)
#  explanation_value = movement
#  if getattr(movement,'getExplanationValue',None) is not None:
#    explanation_value = movement.getExplanationValue()
#  resource_dict['explanation_relative_url'] = explanation_value.getRelativeUrl()
#  source_reference = explanation_value.getSourceReference() or ''
#  resource_dict['source_reference'] = source_reference
#  if display_simulation_state:
#    resource_dict['simulation_state_title'] = movement.getTranslatedSimulationStateTitle()
#  resource_dict['explanation_translated_relative_url'] = "%s/%s" % \
#        (explanation_value.getTranslatedPortalType(),source_reference)
  catalog_explanation = cache_dict['cache_explanation'][explanation_uid]
  resource_dict['explanation_relative_url'] = catalog_explanation.relative_url
  source_reference = catalog_explanation.source_reference
  resource_dict['source_reference'] = catalog_explanation.source_reference
  explanation_portal_type = catalog_explanation.portal_type
  if display_simulation_state:
    simulation_state = catalog_explanation.simulation_state
    resource_dict['simulation_state'] = simulation_state
    simulation_state_title = cache_translated_simulation_state.get((explanation_portal_type,simulation_state), None)
    if simulation_state_title is None:
      portal = context.getPortalObject()
      movement = portal.restrictedTraverse(movement)
      simulation_state_title = movement.getTranslatedSimulationStateTitle()
      cache_translated_simulation_state[(explanation_portal_type,simulation_state)] = simulation_state_title
    resource_dict['simulation_state_title'] = simulation_state_title
  translated_portal_type = cache_translated_portal_type.get(explanation_portal_type, None)
  if translated_portal_type is None:
    translated_portal_type = context.Base_translateString(explanation_portal_type)
    cache_translated_portal_type[explanation_portal_type] = translated_portal_type
  resource_dict['explanation_translated_relative_url'] = '%s/%s' % \
      (translated_portal_type, source_reference)



return resource_dict
