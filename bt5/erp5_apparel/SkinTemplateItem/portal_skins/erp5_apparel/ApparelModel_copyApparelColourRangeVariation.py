request = context.REQUEST
apparel_colour_range = context.getSpecialiseValue(portal_type=('Apparel Colour Range',))
msg = context.Base_translateString('No Apparel Model Colour Variation found.')

if apparel_colour_range is None:
  msg = context.Base_translateString('Apparel Colour Range must be defined.')
else:
  apparel_colour_range_variation_list = [x.getObject() for x in apparel_colour_range.searchFolder(portal_type=('Apparel Colour Range Variation',))]

  apparel_model_colour_variation_list  = context.searchFolder(portal_type=('Apparel Model Colour Variation',))
  apparel_model_colour_variation_title_list = [x.getObject().getTitle() for x in apparel_model_colour_variation_list]

  count = 0
  for apparel_colour_range_variation in apparel_colour_range_variation_list:
    if apparel_colour_range_variation.getTitle() not in apparel_model_colour_variation_title_list:
      count += 1
      # Use portal activity for creating lot of variation
      context.activate(activity='SQLQueue').newContent(
        portal_type = 'Apparel Model Colour Variation',
        title = apparel_colour_range_variation.getTitle(),
        description = apparel_colour_range_variation.getDescription(),
        destination_reference = apparel_colour_range_variation.getDestinationReference()
      )

  if count != 0:
    msg = context.Base_translateString('${count} Apparel Colour Range Variations created.',
        mapping={'count': count})

context.Base_redirect(form_id=form_id,
                      keep_items=dict(portal_status_message=msg))
