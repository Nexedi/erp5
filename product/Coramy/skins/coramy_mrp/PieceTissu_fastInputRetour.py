## Script (Python) "PieceTissu_fastInputRetour"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id_and_weight_list=[]
##title=
##
# updates location property for all given items
from Products.Formulator.Errors import ValidationError, FormValidationError

request = context.REQUEST
compteur = 0
error_item_list = []

try :

  item_nb = int(len(id_and_weight_list)/2)
  for i in range(item_nb) :
    item_result_list = context.portal_catalog(id = str(int(id_and_weight_list[i*2])), portal_type="Piece Tissu")
    try :
      item = item_result_list[0].getObject()
    except :
      item = None
    try :
      weight = float(id_and_weight_list[i*2+1].replace(',','.'))
    except :
      weight = None

    if item is not None :
      if weight is not None :
        # find the delivery_cell_movements in relation with the item
        cell_movement_list = item.getAggregateRelatedValueList(portal_type=['Delivery Cell','Inventory Cell'])
        # keep only production movements and outgoing movements
        movement_list = []
        for movement in cell_movement_list :
          if movement.aq_parent.getPortalType() == 'Production Packing List Line' :
            movement_list.append(movement)
          elif movement.aq_parent.getPortalType() == 'Movement MP Line' and movement.getConsumptionQuantity() > 0 :
            movement_list.append(movement)
        # add Production packing List Line movements in relation with the item
        movement_list+=item.getAggregateRelatedValueList(portal_type=['Production packing List Line'])

        # movement_list should contain only one movement
        if len(movement_list) == 1 :
          aggregated_item_list = movement_list[0].getAggregateValueList()
          new_aggregated_item_id_list = []
          for aggregate_item in aggregated_item_list :
            if aggregate_item.getId() <> item.getId() :
              new_aggregated_item_id_list.append(aggregate_item.getId())

          # now build the new item
          # first compute the quantity of the new item
          try :
            tissu = item.getResourceValue()
            quantity = item.getRemainingQuantity()-(weight/((tissu.getLaizeTotale()/100)*(tissu.getBaseWeight()/1000)))
          except :
            quantity = 0

          if not quantity in (0, 0.0, '0') :
            # create the new item
            new_id = str(item.generateNewId(default = 40000))
            item.portal_types.constructContent(type_name = 'Piece Tissu',
                                              container = item,
                                              quantity = quantity,
                                              laize_utile = item.getLaizeUtile(),
                                              source_reference = item.getSourceReference(),
                                              bain_teinture = item.getBainTeinture(),
                                              id=new_id)
            item[new_id].flushActivity(invoke=1)

            # reset location on returned item
            item.edit(location='')

            # append new_id to new_aggregate_item_id_list and build relation with movement
            new_aggregated_item_id_list.append(new_id)
            if movement_list[0].aq_parent.getPortalType() in ('Movement MP Line', 'Movement PF Line') or movement_list[0].getPortalType() in ('Movement MP Line', 'Movement PF Line') :
              movement_list[0].setConsumedItemIdList(new_aggregated_item_id_list)
            else :
              movement_list[0].setItemIdList(new_aggregated_item_id_list)
            compteur += 1
          else :
            error_item_list.append(id_and_weight_list[i*2]+'(conversion)')
        else :
          error_item_list.append(id_and_weight_list[i*2]+'(non sortie ou plusieurs sorties)')
      else :
        error_item_list.append(id_and_weight_list[i*2]+'(quantité)')
    else :
      error_item_list.append(id_and_weight_list[i*2]+'(inconnue)')

except FormValidationError, validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=La+saisie+a+échoué.'
                                  )
else:
  if len(error_item_list) == 0 : # no errors
    redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+pièces+créées.' % compteur
                                  )
  else :
    pretty_error_list = ''
    for error_item in error_item_list :
      pretty_error_list += error_item + ' '
    redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+pièces+créées.+Problèmes+:+%s.' % (compteur,
                                  pretty_error_list))

request[ 'RESPONSE' ].redirect( redirect_url )
