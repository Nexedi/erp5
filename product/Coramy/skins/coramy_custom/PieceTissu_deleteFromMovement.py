## Script (Python) "PieceTissu_deleteFromMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
piece_dict = {}
piece_dict['41874']='livraison_fabrication/2004/7/movement_0_0' 
piece_dict['40398']='livraison_fabrication/1838/4/movement_5_0' 
piece_dict['41975']='livraison_fabrication/1873/11/movement_0_0'
piece_dict['42254']='mouvement_mp/102/19/movement_0_0'          
piece_dict['36473']='livraison_fabrication/1967/1/movement_0_0' 
piece_dict['36555']='mouvement_mp/98/9/movement_0_0'            
piece_dict['40226']='mouvement_mp/102/9/movement_0_0'           
piece_dict['40145']='livraison_fabrication/2028/8/movement_3_0' 
piece_dict['40092']='livraison_fabrication/1946/1/movement_0_0' 
piece_dict['41789']='mouvement_mp/82/1/movement_0_0'            
piece_dict['41586']='livraison_fabrication/1950/2/movement_2_0' 

for key in piece_dict.keys() :
  mouvement = context.restrictedTraverse(piece_dict[key])
  if mouvement is not None :
    if piece_dict[key].find('mouvement_mp') != -1 :
      if mouvement.getProductionQuantity() > 0 :
        item_id_list = mouvement.getProducedItemIdList()
        new_item_id_list = filter(lambda k_item: k_item != key, item_id_list)
        mouvement.setProducedItemIdList(new_item_id_list)
      else  :
        item_id_list = mouvement.getConsumedItemIdList()
        new_item_id_list = filter(lambda k_item: k_item != key, item_id_list)
        mouvement.setConsumedItemIdList(new_item_id_list)
    else :
      item_id_list = mouvement.getItemIdList()
      new_item_id_list = filter(lambda k_item: k_item != key, item_id_list)
      mouvement.setItemIdList(new_item_id_list)
    
    print piece_dict[key], item_id_list, new_item_id_list, key

return printed
