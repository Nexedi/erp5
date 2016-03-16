'''
This script is used to copy composition from a related Apparel Fabric Colour
Variation to the current object.
'''

cell_id_list = []
msg = context.Base_translateString('No Composition found.')
colour_range = context.getSpecialiseValue(portal_type='Apparel Colour Range')
if colour_range is None:
  msg = context.Base_translateString('Apparel Colour Range must be defined.')

elif len(colour_range.contentValues(portal_type='Apparel Colour Range Variation')) != 0:
  colour_variation = colour_range.contentValues(portal_type='Apparel Colour Range Variation')[0]
  variation_line_list = colour_variation.contentValues(portal_type="Apparel Colour Range Variation Line",
    sort_on='int_index')
  if len(variation_line_list):
    # the first one is the most important one
    # take composition only from the first one
    variation_line = variation_line_list[0]
    apparel_fabric_colour_variation = variation_line.getSpecialiseValue(portal_type='Apparel Fabric Colour Variation')
    if apparel_fabric_colour_variation is not None:
      fabric = apparel_fabric_colour_variation.getParentValue()
      composition_list = fabric.getCompositionList()
      # get cells
      poly_list = fabric.ApparelFabric_asCellRange(matrixbox=1)[0]
      context.setCompositionList(composition_list)
      #context.setVariationBaseCategoryList(['composition',])
      context.setCellRange(base_id='composition', *context.ApparelFabric_asCellRange(matrixbox=False))

      for cat, title in poly_list:
        cell = fabric.getCell(cat, base_id='composition')
        if cell is not None:
          new_cell = context.newCell(cat, base_id='composition',
                                     portal_type='Mapped Value', # XXX
                                     quantity=cell.getProperty('quantity'))
      if len(poly_list):
        msg = context.Base_translateString('${count} Compositions created.',
            mapping={'count': len(poly_list)})

return context.Base_redirect(form_id=form_id,
                      keep_items = dict(portal_status_message=msg))
