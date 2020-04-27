request = context.REQUEST
variation = request.get('variation', None)
image_id = request.get('image_id', None)
if variation:
  variation = context.getWebSiteValue().restrictedTraverse(variation)
  if image_id:
    image = variation.restrictedTraverse(image_id)
  else:
    image = variation.getDefaultImageValue()
  if image is not None:
    return image.absolute_url()

if image_id:
  default_image = context.restrictedTraverse(image_id)
else:
  default_image = context.getDefaultImageValue()

if default_image is not None:
  # if current product has image, consider that it has no variation
  return default_image.absolute_url()

def getAvailableVariation(individual_variation_list):
  for individual_variation in individual_variation_list:
    return individual_variation
    #if context.Resource_getInventoryStatus(variation=individual_variation.getRelativeUrl()) in ("STOCK", "AVAILABLE"):
    #  return individual_variation
  return None

individual_variation_list = [x for x in context.contentValues(portal_type='Product Individual Variation') if x.getVisibilityState() == "visible" ]
random.shuffle(individual_variation_list)
individual_variation = getAvailableVariation(individual_variation_list)
if individual_variation:
  if image_id:
    default_image = individual_variation.restrictedTraverse(image_id)
  else:
    default_image = individual_variation.getDefaultImageValue()
  if default_image:
    context.REQUEST.set('default_displayed_variation', individual_variation.getRelativeUrl())
    return default_image.absolute_url()

else:
  return None
