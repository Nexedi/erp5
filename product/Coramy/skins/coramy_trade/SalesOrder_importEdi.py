## Script (Python) "SalesOrder_importEdi"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=import_file, segmentation_strategique='2003-2004', incoterm='DAF',delivery_mode='Transporteur', order_type='Approvisionnement', travel_duration=0, batch_mode=0,**kw
##title=
##
# import d'un fichier EDI
# format de fichier attendu
# Traduction .rec du fichier Edifact par NY Net



from DateTime import DateTime


# link between NYNet alias table and python import script
edi_import_script_dict = {
  # 'NYNet alias table name' : import script
  'CAR-ORD':context.SalesOrder_importEdiCarrefour,
  'ORDAUCHAAUCHAN':context.SalesOrder_importEdiAuchan,
  'ORDAUCHA':context.SalesOrder_importEdiAuchan
}


try:
  # read the NY Net file
  file_line_list = import_file.readlines()

  alias_table_name = string.split(file_line_list[0].split(':',1)[1])[0]
  import_script = edi_import_script_dict[alias_table_name] 
except:
  #return None
  return (None,None)



def setLog(item, comment):
  item_comment = item.getComment()
  if item.comment != None:
    item.setComment(item_comment +  comment)
  else:
    item.setComment(comment)

# create a new sales order
item_module = context.getPortalObject().commande_vente
my_id = str(context.getObject().generateNewId())

context.portal_types.constructContent(
  type_name = 'Sales Order',
        container = item_module,
        id = my_id,
  date_reception = DateTime()
)

sales_order = item_module[my_id]



# set some fields
sales_order.setCommandeOrigine('EDI')
#sales_order.setComment('Commentaires générés par l import EDI du fichier: \n')
setLog(sales_order ,'Commentaires générés par l import EDI du fichier ' + import_file.filename  + ' :\n')
setLog(sales_order ,'Sales Order ID: ' + my_id  + '\n')

sales_order.setSegmentationStrategique(segmentation_strategique)
sales_order.setDeliveryMode(delivery_mode)
sales_order.setIncoterm(incoterm)
sales_order.setOrderType(order_type)

# set the source administration
local_user = container.portal_membership.getAuthenticatedMember()
local_user_name = string.replace(local_user.getUserName(), ' ', '_')
local_persons = sales_order.item_by_title_sql_search(title = local_user_name, portal_type = 'Person')
if len(local_persons) > 0:
  sales_order.setSourceAdministration(local_persons[0].relative_url)


# some useful functions ...
def link_with_organisation(code_ean13, link_function, portal_type_name):
  result = context.item_by_ean13_code_sql_search(organisation_ean = code_ean13, portal_type = portal_type_name) 
  try:
    if len(result) == 1:
      link_function( result[0].relative_url )
    
    else:
      raise IndexError
  except IndexError:
    setLog(sales_order, 'Erreur sur le code EAN d une societe:\n\tCode EAN: ' +  code_ean13 + '\n')
  
def link_with_organisation_group(code_ean13, link_function, portal_type_name):
  result = context.item_by_ean13_code_sql_search(organisation_ean = code_ean13, portal_type = portal_type_name) 
  try:
    if len(result) == 1:
      link_function( 'group/'+result[0].getObject().getGroup() )
    
    else:
      raise IndexError
  except IndexError:
    setLog(sales_order, 'Erreur sur le code EAN d un groupe:\n\tCode EAN: ' +  code_ean13 + '\n')


def modele_search(code_ean13):
  result = context.item_by_ean13_code_sql_search(organisation_ean = code_ean13, portal_type = 'Set Mapped Value') 
  try:
    if len(result) == 1:
      result_object = result[0].getObject()
    else:
      raise IndexError
  except IndexError:
    result_object = None
  else:
    return result_object

# dictionnary of those functions, in order to give them to the import script
useful_functions = {
  'modele_search':modele_search,
  'link_with_organisation':link_with_organisation,
  'link_with_organisation_group':link_with_organisation_group
}



request  = context.REQUEST

# item of products_list: tuple (product_ean13_code, [[quantity, price], ...]) 
products_list = []

# read each line of the file
for file_line in file_line_list :
  # save the line in the comment
  #item_module[my_id].setComment(sales_order.getComment()+file_line)
  # get the line header
  sub_line_list = file_line.split(':',1)
  line_header = sub_line_list[0]
  # separate the arguments
  line_item_list = string.split(sub_line_list[1])
  # call the adequat function
  try:
    import_script(line_header, line_item_list, sales_order, products_list , useful_functions)
  except KeyError:
    #sales_order.setComment(sales_order.getComment() + 'Erreur sur la lecture d une ligne:\n\t' + file_line )
    setLog(sales_order, 'Erreur sur la lecture d une ligne:\n\t' + file_line )


# create a dictionary of the desired resource
# { modele_relative_url : [ ( [ predicate_value_list  ] , quantity , price ), (...), ...] , ...}
desired_lines = {}
for product in products_list:
  try:
    # must be a 'Set Mapped Value'
    product_item = modele_search(product[0]).getObject()
  except:
    setLog(sales_order, 'Erreur sur un modèle ! \n\tCode EAN: ' +  product[0] + '\n')
  else:
    # parent: must be a 'Variated Reference'
    father_uid = product_item.getParentUid() 
    father_obj = context.portal_catalog.getObject(father_uid)

    # grand parent: must be a 'Modele'
    grand_father_uid = father_obj.getParentUid()
    grand_father_obj = context.portal_catalog.getObject(grand_father_uid)
  
    grand_father_url = grand_father_obj.getRelativeUrl()

    # calculate the number of piece
    total_quantity = 0
    price = '0'
    for qty in product[1]:
      price = qty[1]
      total_quantity += string.atoi( qty[0] )

    total_quantity = "%i" % total_quantity
    

    if grand_father_url in desired_lines.keys():

      # test if the predicateValueList exists
      predicate_value_list = product_item.getPredicateValueList() 
      trouve = 0
      for tuple in desired_lines[ grand_father_url ]:
        if predicate_value_list == tuple[0]:
          setLog(sales_order, 'Erreur sur un modèle: 2 codes EAN represente le meme modele: \n\t  ' + grand_father_url + ' ' )
          
          for predicate_value in predicate_value_list:
            setLog(sales_order, predicate_value + ' ' )

          setLog(sales_order, '\n' )
          trouve = 1

      if trouve == 0:
        # predicate_value_list : variante de la SetMappedValue
                desired_lines[ grand_father_url ].append((product_item.getPredicateValueList(), total_quantity , price))
      
    else:
              desired_lines[ grand_father_url ] = [ ((product_item.getPredicateValueList(), total_quantity , price )) ]


for modele_relative_url in desired_lines.keys():


  # compute variation_base_category_list and variation_category_list for this line
  line_variation_base_category_dict = {}
  line_variation_category_list = []

  for my_tuple in desired_lines[ modele_relative_url ] :

     for variation_item in my_tuple[0] :

       if not variation_item in line_variation_category_list :
         line_variation_category_list.append(variation_item)
         variation_base_category_items = variation_item.split('/')
         if len(variation_base_category_items) > 0 :
           line_variation_base_category_dict[variation_base_category_items[0]] = 1

  line_variation_base_category_list = line_variation_base_category_dict.keys()

  

  # construct new sales order lines
  sales_order_line_id = str(sales_order.generateNewId())

  # sur le folder, newContent
  sales_order_line = sales_order.newContent(
    portal_type = "Sales Order Line",
    resource = modele_relative_url,
    id = sales_order_line_id,
    comment = ''
  )

  sales_order_line.setResource(modele_relative_url)
  sales_order_line.setVariationBaseCategoryList(line_variation_base_category_list)
  sales_order_line.setVariationCategoryList(line_variation_category_list)

  #sales_order_line_cell_list = sales_order_line.contentValues()
  sales_order_line_cell_list = sales_order_line.objectValues()
  
  for my_tuple in desired_lines[ modele_relative_url ] :
    quantity_updated = 0

    for sales_order_line_cell in sales_order_line_cell_list :
      if sales_order_line_cell.test(context.asContext(categories=my_tuple[0])):
        sales_order_line_cell.setTargetQuantity(my_tuple[1])
        sales_order_line_cell.setPrice(my_tuple[2])
        sales_order_line_cell.flushActivity(invoke=1)
        quantity_updated = 1
        break
    # if no cell according to variation_category_list was found
    # or no variation at all, we update the container_line
    if not quantity_updated :
      sales_order_line.setTargetQuantity(my_tuple[1])
      sales_order_line.flushActivity(invoke=1)




# set the target start date
if sales_order.getTargetStartDate() == None:
  try:
    sales_order.setTargetStartDate( sales_order.getTargetStopDate() - travel_duration )
  except TypeError:
    None

setLog(sales_order,  'Fin des commentaires générés par l import EDI.\n')

sales_order.flushActivity(invoke=1)



# try to apply a sale condition
sales_order.sales_order_apply_condition(my_id, 1)



# and this is the end ....
if batch_mode:
  #return sales_order.getComment()
  return (sales_order.getId(),sales_order.getComment())
else:
  redirect_url = '%s?%s' % ( item_module.absolute_url()+'/'+my_id+'/'+'view', 'portal_status_message=Commande+Vente+créée.')
  request[ 'RESPONSE' ].redirect( redirect_url )
