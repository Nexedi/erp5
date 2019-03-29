request  = context.REQUEST
N_ = context.Base_translateString

from AccessControl import getSecurityManager
u=getSecurityManager().getUser()
ADD_PERMISSION =  'Add portal content'
if not u.has_permission(ADD_PERMISSION,context):
  request[ 'RESPONSE' ].redirect('%s/view?portal_status_message=%s' % (context.absolute_url(), N_("You can't modify that document any longer.")))
  return

def recurse(document):
  result = document.hasActivity()
  if not result:
    for subdocument in document.objectValues():
      result = recurse(subdocument)
      if result:
        break
  return result

def deleteContent(container, document_id):
  document = container[document_id]
  if recurse(document):
    return True
  else:
    container.deleteContent(document_id)
    return False

cell_base_id = 'movement'
line_kwd = {'base_id':cell_base_id}

variation_list       = kw['variation_list']
emission_letter_list = kw['emission_letter_list']
cash_status_list     = kw['cash_status_list']
other_parameter_list = kw['other_parameter']
operation_currency   = other_parameter_list[0]
line_portal_type     = other_parameter_list[1]
read_only            = other_parameter_list[2]
column_base_category = other_parameter_list[3]
use_inventory        = other_parameter_list[4]
check_float          = int(other_parameter_list[7])

# get the column base list
if column_base_category == 'cash_status':
  columne_base_list = cash_status_list
elif column_base_category == 'emission_letter':
  column_base_list = emission_letter_list
else:
  column_base_list = variation_list

base_category_list = ('emission_letter', 'cash_status', 'variation')
per_resource_dict = {}

error = 0
negative_quantity = 0
float_quantity = 0
variation_not_defined = 0
remaining_activity = None
# remove previous line
# specific case for monetary issue
if context.getPortalType() == "Monetary Issue":
  old_line = [id for id in context.objectIds()]
else:
  old_line = [x.getObject().getId() for x in context.objectValues(portal_type=[line_portal_type,])]
if len(old_line)>0:
  for line_id in old_line:
    if deleteContent(context, line_id):
      error = 1
      remaining_activity = '%s/%s' % (context.getPath(), line_id)
      break

if not error:
  # get the list of movement we need to create
  for line in listbox:
    for counter in xrange(1, len(column_base_list)+1):
      quantity = line["column%s" %(str(counter),)]
      if quantity != 0 and quantity != '':
        if quantity < 0:
          error = 1
          negative_quantity = 1
        if check_float:
          if int("%i" % quantity) != quantity:
            error = 1
            float_quantity = 1
        #context.log("listboxline", line)
        movement = {}
        movement['quantity'] = quantity
        # get variation for the cell
        if column_base_category == 'cash_status':
          movement['cash_status'] =  "cash_status/%s" %cash_status_list[counter-1]
          if line.has_key('emission_letter'):
            movement['emission_letter'] = "emission_letter/%s" %line['emission_letter']
          elif len(emission_letter_list) == 1:
            movement['emission_letter'] =  "emission_letter/%s" %(emission_letter_list[0].lower(),)
          else:
            movement['emission_letter'] = "emission_letter/not_defined" %line['emission_letter']
          if line.has_key('variation'):
            movement['variation'] = "variation/%s" %line['variation']
          elif len(variation_list) == 1:
            movement['variation'] = "variation/%s" %(variation_list[0],)
          else:
            movement['variation'] = "variation/not_defined"
        elif column_base_category == 'emission_letter':
          if line.has_key('cash_status'):
            movement['cash_status'] =  "cash_status/%s" %line['cash_status']
          elif len(cash_status_list) == 1:
            movement['cash_status'] =  "cash_status/%s" %(cash_status_list[0],)
          else:
            movement['cash_status'] =  "cash_status/not_defined"
          movement['emission_letter'] = "emission_letter/%s" %emission_letter_list[counter-1]
          if line.has_key('variation'):
            movement['variation'] = "variation/%s" %line['variation']
          elif len(variation_list) == 1:
            movement['variation'] = "variation/%s" %(variation_list[0],)
          else:
            movement['variation'] = "variation/not_defined"
        else:
          if line.has_key('cash_status'):
            movement['cash_status'] =  "cash_status/%s" %line['cash_status']
          elif len(cash_status_list) == 1:
            movement['cash_status'] =  "cash_status/%s" %(cash_status_list[0],)
          else:
            movement['cash_status'] =  "cash_status/not_defined"
          if line.has_key('emission_letter'):
            movement['emission_letter'] = "emission_letter/%s" %line['emission_letter']
          elif len(emission_letter_list) == 1:
            movement['emission_letter'] =  "emission_letter/%s" %(emission_letter_list[0].lower(),)
          else:
            movement['emission_letter'] = "emission_letter/not_defined"
          movement['variation'] = "variation/%s" %variation_list[counter-1]
        #context.log("movement", movement)
        # generate a key based on variation
        # this will allow us to check if there is multiple line for the same resource + variation
        movement_key = '%s_%s_%s' %(movement['cash_status'], movement['emission_letter'], movement['variation'])
        resource_id = line["resource_id"]
        if per_resource_dict.has_key(resource_id) and per_resource_dict[resource_id].has_key(movement_key):
          # add quantity in case af same movement
          per_resource_dict[resource_id][movement_key]['quantity'] = per_resource_dict[resource_id][movement_key]['quantity'] + movement['quantity']
        elif per_resource_dict.has_key(resource_id):
          # add variation for this resource
          per_resource_dict[resource_id][movement_key] = movement
        else:
          # create a dict of variation for this resource
          per_resource_dict[resource_id] = {movement_key:movement,}
  #context.log("resource", per_resource_dict)
  # create the movement
  variation_not_defined = 0
  for resource_id in per_resource_dict.keys():
    if error == 1:
      break
    variation_list_dict = per_resource_dict[resource_id].values()
    # get the resource
    #resource_list = context.portal_catalog(portal_type = ('Banknote','Coin'), id = resource_id)
    #if len(resource_list) == 0:
    #  #context.log('CashDetail_saveFastInputLine', 'Cannot get the resource object for id = %s' %(resource_id,))
    #  continue
    resource_object = context.currency_cash_module[resource_id]
    # get the variation
    emission_letter_dict = {}
    cash_status_dict = {}
    variation_dict = {}
    for variation in variation_list_dict:
      letter = variation['emission_letter']
      status = variation['cash_status']
      variation = variation['variation']
      # check if variation exist for the resource
      if column_base_category == "variation":
  #       if variation != 'variation/not_defined' and variation.replace('variation/','') not in resource_object.getVariationList():
  #         variation_not_defined = 1
  #         break
        if variation.replace('variation/','') not in resource_object.getVariationList():
          variation_not_defined = 1
          error = 1
          break
      # for the letter, if coin, must always be not_defined
      if letter != 'emission_letter/not_defined' and letter.replace('emission_letter/','') not in resource_object.getEmissionLetterList()+['mixed']:
        old_letter = letter
        letter = 'emission_letter/not_defined'
        # replace key in per_resource_dict
        old_key = '%s_%s_%s' %(status, old_letter, variation)
        key = '%s_%s_%s' %(status, letter, variation)
        #context.log("change key, old/new", str((old_key, key)))
        per_resource_dict[resource_id][key] = per_resource_dict[resource_id].pop(old_key)
        per_resource_dict[resource_id][key]['emission_letter'] = letter
        #context.log('per_resource_dict[resource_id][key]', per_resource_dict[resource_id][key])
      if not emission_letter_dict.has_key(letter):
        emission_letter_dict[letter] = 1
      if not cash_status_dict.has_key(status):
        cash_status_dict[status] = 1
      if not variation_dict.has_key(variation):
        variation_dict[variation] = 1
    # get new list dict in case wa had modified it
    variation_list_dict = per_resource_dict[resource_id].values()
    #ontext.log("cariation_list_dict after modif", variation_list_dict)
    variation_category_list = emission_letter_dict.keys() + cash_status_dict.keys() + variation_dict.keys()
    # create the cash line
    #context.log("variation_category_list", variation_category_list)
    line = context.newContent(portal_type           = line_portal_type
                              , resource      = resource_object.getRelativeUrl() # banknote or coin
                              , quantity_unit = 'unit'
                              )
    # set base category list on line
    line.setVariationBaseCategoryList(base_category_list)
    # set category list line
    line.setVariationCategoryList(variation_category_list)
    line.updateCellRange(script_id='CashDetail_asCellRange', base_id=cell_base_id)
    # create cell
    cell_range_key_list = line.getCellRangeKeyList(base_id=cell_base_id)
    if cell_range_key_list != [[None, None]] :
      for k in cell_range_key_list:
        # check we don't create a cell for variation which is not defined
        key = "%s_%s_%s" %(k[2], k[0], k[1])
        if not per_resource_dict[resource_id].has_key(key):
          #context.log("not", key)
          continue
        category_list = filter(lambda k_item: k_item is not None, k)
        c = line.newCell(*k, **line_kwd)
        if use_inventory == 'True':
          mapped_value_list = ['price', 'inventory']
        else:
          mapped_value_list = ['price', 'quantity']
        #context.log("creating", str((category_list, mapped_value_list)))
        c.edit(membership_criterion_category_list = category_list
              , mapped_value_property_list       = mapped_value_list
              , category_list                    = category_list
              , price                            = resource_object.getBasePrice()
              , force_update                     = 1
              )
    # set quantity on cell to define quantity of bank notes / coins
    #context.log("variation_list_dict before browse", variation_list_dict)
    for variation_item in variation_list_dict:
      variation = variation_item[column_base_category]
      if column_base_category == "cash_status":
        cell = line.getCell(variation_item["emission_letter"],
                            variation_item["variation"],
                            variation,
                            base_id=cell_base_id)
      elif column_base_category == "emission_letter":
        cell = line.getCell(variation,
                            variation_item["variation"],
                            variation_item["cash_status"],
                            base_id=cell_base_id)
      else:
        #context.log("variation_item['emission_letter']", variation_item["emission_letter"])
        cell = line.getCell(variation_item["emission_letter"],
                            variation,
                            variation_item["cash_status"],
                            base_id=cell_base_id)
      # set quantity
      #context.log('cell, variation', str((cell, variation)))
      if cell is not None:
        if use_inventory == 'True':
          cell.setInventory(variation_item["quantity"])
        else:
          cell.setQuantity(variation_item["quantity"])
    line.getPrice() # Call getPrice now because it will be called on reindexation and it modifies the line.
                    # So better modify it here so it's only saved once to ZODB.
  if error:
    # Delete what was already created
    old_line = [x.getObject() for x in context.objectValues(portal_type=[line_portal_type,])]
    if len(old_line)>0:
      for object_list in old_line:
        context.deleteContent(object_list.getId())


if error:
  if variation_not_defined:
    message = N_("$title doesn't exist for $variation", mapping = {'title':resource_object.getTranslatedTitle(), 'variation':variation.replace('variation/','')})
  if negative_quantity:
    message = N_("You must not enter negative values")
  if float_quantity:
    message = N_("You must enter integer values")
  if remaining_activity is not None:
    message = N_("There are operations pending on $path. Please try again later.", mapping={'path': remaining_activity})
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , "portal_status_message=%s" %message
                                  )
  request[ 'RESPONSE' ].redirect( redirect_url )
else:
  message = N_("Lines Created")
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s' %(message,)
                                  )
  request[ 'RESPONSE' ].redirect( redirect_url )
