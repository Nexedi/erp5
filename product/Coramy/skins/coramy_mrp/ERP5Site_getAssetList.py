## Script (Python) "ERP5Site_getAssetList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=group_by_node=0, group_by_section=0, group_by_variation=0
##title=
##
request = context.REQUEST
stock_MP = 0
stock_PF = 1

if stock_MP == 1 :
  inventory_list = context.Resource_zGetStockMPInventoryList(calculate_asset=1,
                    node_category='site/Stock_MP', section_category='group/Coramy',
                    group_by_node=group_by_node, group_by_section=group_by_section,
                    group_by_variation=group_by_variation,
                    simulation_state=['delivered', 'started', 'stopped', 'invoiced','planned','getting_ready','confirmed','ready', 'ordered'])
  print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ('Nature composant', 'Code composant', 'Variante', 'Quantite', 'Prix unitaire', 'Montant total', 'Type composant', 'Fournisseur')
  for b in inventory_list:
    if b.inventory <> 0 :
      amount_object = b.getObject()
      if amount_object is not None :
        unit_price = amount_object.Amount_getSupplierPrice()
      else :
        unit_price = 0
      # AS SOON AS POSSIBLE asset_price should be given by b.asset_price an not unit_price*b.inventory
      if group_by_variation:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (b.resource_relative_url.split('/')[0], b.resource_relative_url.split('/')[-1], b.variation_text.replace('\n', '-'),
                str(b.inventory).replace('.',','), str(unit_price).replace('.',','), str(unit_price*b.inventory).replace('.',','), b.type_title, b.source_title)
      else:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (b.resource_relative_url.split('/')[0], b.resource_relative_url.split('/')[-1], '',
                str(b.inventory).replace('.',','), str(unit_price).replace('.',','), str(unit_price*b.inventory).replace('.',','), b.type_title, b.source_title)

if stock_PF == 1 :
  inventory_list = context.Resource_zGetStockPFInventoryList(calculate_asset=1,
                    node_category='site/Stock_PF', section_category='group/Coramy', collection_url='collection/2004/DIM',
                    group_by_node=group_by_node, group_by_section=group_by_section,
                    group_by_variation=group_by_variation, to_date = "2003/11/30",
                    section_uid=context.portal_categories.group.Coramy.uid,
                    simulation_state=['delivered', 'started', 'stopped', 'invoiced']) # FOR FUTURE INVNETORY add ,'planned','getting_ready','confirmed','ready', 'ordered'
  print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ('Nature produit', 'Code produit', 'Variantes', 'Quantite', 'Prix unitaire', 'Montant total', 'Famille', 'Client')
  for b in inventory_list:
    if b.inventory <> 0 :
      amount_object = b.getObject()
      if amount_object is not None :
        try :
          pri = amount_object.Amount_getPri()
        except :
          pri = -99
      else :
        pri = 0
      if group_by_variation:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (b.resource_relative_url.split('/')[0], b.resource_relative_url.split('/')[-1], b.variation_text.replace('\n', '-'),
                 str(b.inventory).replace('.',','), str(pri).replace('.',','), str(b.inventory*pri).replace('.',','), b.famille_title, b.destination_title, b.section_title)
      else:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (b.resource_relative_url.split('/')[0], b.resource_relative_url.split('/')[-1], '',
                 str(b.inventory).replace('.',','), str(pri).replace('.',','), str(b.inventory*pri).replace('.',','), b.famille_title, b.destination_title, b.section_title)

request.RESPONSE.setHeader('Content-Type','application/text')
return printed
