from zLOG import LOG
from Products.ERP5Type.Message import Message
from Ft.Xml import Parse

def CheckbookReception_importItemFile(self, import_file=None, REQUEST=None, **kw):
  reference_dict = {}
  reference_dict['CHEQUIER_COMPTE_COURANT_ORDINAIRE'] = 'CHCCO'
  reference_dict['CHEQUIER_COMPTE_ORDINAIRE_DU_PERSONNEL'] = 'CHCOP'
  reference_dict['BON_VIREMENT'] = 'BV'
  # We will build a several listbox like it is already done into the user interface
  # A listbox will be build for every resource
  xml_content = Parse(import_file)
  file_item_list = xml_content.xpath('//object')
  # First, construct a dictionnary for every resource
  import_dict = {}
  for item in file_item_list:
    checkbook_id = item.xpath("string(@id)")
    check_quantity = str(item.xpath("string(./check_quantity)"))
    reference_min = str(item.xpath("string(./reference_min)"))
    reference_max = str(item.xpath("string(./reference_max)"))
    internal_account_number = item.xpath("string(./numero_interne)")
    checkbook_type = item.xpath("string(./checkbook_type)")
    type = str(item.xpath("string(./checkbook_type)"))
    gid = str(item.xpath("string(./gid)"))
    checkbook_dict = import_dict.setdefault(checkbook_type, {})
    account_dict = checkbook_dict.setdefault(internal_account_number, {})
    item_dict = account_dict.setdefault(gid, {})
    item_dict['reference_min'] = reference_min
    item_dict['reference_max'] = reference_max
    item_dict['check_quantity'] = check_quantity
    item_dict['internal_account_number'] = internal_account_number

  listbox_dict = {}
  for (checkbook_type, checkbook_dict) in import_dict.items():
    listbox = []
    i = 0
    resource_list = self.portal_catalog(portal_type=['Checkbook Model',
                                                     'Check Model'],
                                        reference = reference_dict[checkbook_type])
    if len(resource_list) != 1:
      raise ValueError, "The import does not support this type : %s" % checkbook_type
    resource = resource_list[0].getObject()
    resource_relative_url = resource.getRelativeUrl()
    resource_amount_dict = {}
    is_checkbook = 0
    if resource.getPortalType() == 'Checkbook Model':
      is_checkbook = 1
    if is_checkbook:
      for amount in resource.objectValues(
          portal_type="Checkbook Model Check Amount Variation"):
        resource_amount_dict["%i" % amount.getQuantity()] = "check_amount/%s" % \
                                                       amount.getRelativeUrl()
    for  (account, account_dict) in checkbook_dict.items():
      for (gid, item_dict) in account_dict.items():
        listbox_line = {}
        listbox_line['listbox_key'] = '%05i' % i
        listbox_line['reference_range_min'] = item_dict['reference_min']
        listbox_line['reference_range_max'] = item_dict['reference_max']
        listbox_line['destination_payment_reference'] = item_dict['internal_account_number']
        listbox_line['quantity'] = 1
        if is_checkbook:
          listbox_line['check_amount'] = resource_amount_dict[item_dict['check_quantity']]
        listbox.append(listbox_line)
    listbox_dict[resource_relative_url] = listbox
  # First make sure there is no errors
  message = None
  error_value = 0
  for (resource_relative_url, listbox) in listbox_dict.items():
    REQUEST['resource'] = resource_relative_url
    (error_value, field_error_dict) = self.CheckDelivery_generateCheckDetailInputDialog(
                                       verbose=1,
                                       listbox=listbox, 
                                       batch_mode=1,
                                       resource=resource_relative_url,
                                       REQUEST=REQUEST)
    if error_value:
      message = field_error_dict.values()[0].error_text
      redirect_url = '%s/view?%s' % ( self.absolute_url()
                                , 'portal_status_message=%s' % message)
      REQUEST['RESPONSE'].redirect( redirect_url )

  # Then create everything
  if not error_value:
    for (resource_relative_url, listbox) in listbox_dict.items():
      REQUEST['resource'] = resource_relative_url
      self.CheckDetail_saveFastInputLine(listbox=listbox, check=0, 
                                         resource=resource_relative_url,
                                         REQUEST=REQUEST)

    message = Message(domain='ui', message='File Imported successfully')
  return message




