## Script (Python) "PieceTissu_findSuspectMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
cr = '\n'
tab = '\t'
movement_log = 'Id pieces'+tab+'piece_relative_url'+tab+'In-Out'+tab+'number'+tab+'relative_url_movement'+cr

piece_list = context.portal_catalog(portal_type=('Piece Tissu',))
#piece_list = context.portal_catalog(id = ('41890','36921') , portal_type="Piece Tissu")

for piece_item in piece_list :
  out_movement_list = ''
  out_count = 0
  in_movement_list = ''
  in_count = 0
  suspect_movement_list = ''
  suspect_count = 0
  piece = piece_item.getObject()
  if piece is not None :
    related_movement_list = piece.getAggregateRelatedValueList()
    for movement in related_movement_list :
      movement_relative_url = movement.getRelativeUrl()
      if movement_relative_url.find('livraison_fabrication') != -1 :
        out_movement_list += movement_relative_url + tab
        out_count += 1
      elif movement_relative_url.find('inventaire_mp') != -1 :
        in_movement_list += movement_relative_url + tab
        in_count += 1
      elif movement_relative_url.find('livraison_achat') != -1 :
        in_movement_list += movement_relative_url + tab
        in_count += 1
      elif movement_relative_url.find('mouvement_mp') != -1 :
        if movement.getProductionQuantity() > 0 :
          in_movement_list += movement_relative_url + tab
          in_count += 1
        elif movement.getConsumptionQuantity() > 0 :
          out_movement_list += movement_relative_url + tab
          out_count += 1
        else :
          suspect_movement_list += movement_relative_url + tab
          suspect_count += 1
      else :
        suspect_movement_list += movement_relative_url + tab
        suspect_count += 1  
  if (in_count==1 and out_count==1 and suspect_count==0) or (in_count==1 and out_count==0 and suspect_count==0) or (in_count==0 and out_count==0 and suspect_count==0):
    pass
  elif (in_count==0 and out_count==1 and suspect_count==0) :
    if piece.aq_parent.getPortalType()=="Piece Tissu" :
      pass
    else :
      movement_log += piece.getId() + tab + piece.getRelativeUrl() + tab + 'OUT' + tab + str(out_count) + tab + out_movement_list + cr
  else :
    if in_count > 0 :
      movement_log += piece.getId() + tab + piece.getRelativeUrl() + tab + 'IN' + tab + str(in_count) + tab + in_movement_list + cr
    if out_count > 0 :
      movement_log += piece.getId() + tab + piece.getRelativeUrl() + tab + 'OUT' + tab + str(out_count) + tab + out_movement_list + cr
    if suspect_count > 0 :
      movement_log += piece.getId() + tab + piece.getRelativeUrl() + tab + 'SUSPECT' + tab + str(suspect_count) + tab + suspect_movement_list + cr

request.RESPONSE.setHeader('Content-Type','application/text')

return movement_log
