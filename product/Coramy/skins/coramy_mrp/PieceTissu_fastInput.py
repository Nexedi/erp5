## Script (Python) "PieceTissu_fastInput"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=piece_tissu_list
##title=
##
# creates Piece Tissu items
from Products.Formulator.Errors import ValidationError, FormValidationError

text_list = context.PieceTissu_fastInputList()[0]

if context.getPortalType() == 'Piece Tissu' : # we create a sub_item
  my_container = context
else : # we create a master_item
  my_container = context.getPortalObject().piece_tissu

my_quantity = None
request = context.REQUEST
compteur = 0
created_item_id_list = []

try :

  for line in piece_tissu_list :

    if line.find(text_list[0]) <> (-1) : # quantity
      # create previous item
      if my_quantity is not None :
        compteur += 1
        new_id = str(my_container.generateNewId(default = 40000))
        my_container.portal_types.constructContent(type_name = 'Piece Tissu',
                                                              container = my_container,
                                                              quantity = my_quantity,
                                                              laize_utile = my_laize_utile,
                                                              source_reference = my_source_reference,
                                                              bain_teinture = my_bain_teinture,
                                                              comment = my_comment,
                                                              id=new_id)
        if context.getPortalType() == 'Delivery Cell' or context.getPortalType() == 'Inventory Cell' :
          my_container[new_id].edit(resource_value = context.getResource(),
                                    source_value = context.getSource(),
                                    variation_category_list = context.getVariationCategoryList())
        my_container[new_id].flushActivity(invoke=1)
        # print label
        my_container[new_id].PieceTissu_printMetoLabel()
        created_item_id_list.append(new_id)

      # initialize new piece
      my_quantity = None
      my_laize_utile = None
      my_source_reference = None
      my_bain_teinture = None
      my_comment = None

      # find quantity value
      input_items = line.split('_:')
      if len(input_items) > 1 :
        if input_items[1] <> '' :
          my_quantity = float(input_items[1].replace(',','.'))
        else :
          break

    elif line.find(text_list[1]) <> (-1) : # laize_utile
      input_items = line.split('_:')
      if len(input_items) > 1 :
        if input_items[1] <> '' :
          my_laize_utile = float(input_items[1].replace(',','.'))

    elif line.find(text_list[2]) <> (-1) : # no fournisseur
      input_items = line.split('_:')
      if len(input_items) > 1 :
        if input_items[1] <> '' :
          my_source_reference = input_items[1]

    elif line.find(text_list[3]) <> (-1) : # bain teinture
      input_items = line.split('_:')
      if len(input_items) > 1 :
        if input_items[1] <> '' :
          my_bain_teinture = input_items[1]

    elif line.find(text_list[4]) <> (-1) : # comment
      input_items = line.split('_:')
      if len(input_items) > 1 :
        if input_items[1] <> '' :
          my_comment = input_items[1]

  # if we create items on a delivery cell or inventory cell
  # we update item_id_list or produced_item_id_list
  if context.getPortalType() == 'Delivery Cell' or context.getPortalType() == 'Inventory Cell' :
    if context.aq_parent.getPortalType() in ('Movement MP Line', 'Movement PF Line') or context.getPortalType() in ('Movement MP Line', 'Movement PF Line'):
      if context.getItemIdList() is not None :
        context.setProducedItemIdList(created_item_id_list+context.getItemIdList())
      else :
        context.setProducedItemIdList(created_item_id_list)
    else:
      if context.getItemIdList() is not None :
        context.setItemIdList(created_item_id_list+context.getItemIdList())
      else :
        context.setItemIdList(created_item_id_list)

except FormValidationError, validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=La+saisie+a+échoué.'
                                  )
else:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+pièces+créées.' % compteur
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
