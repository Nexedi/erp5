from Globals import get_request
from Products.CMFCore.utils import getToolByName

def fixProductNames(self, REQUEST=None):
  msg = ''
  portal_types = getToolByName(self, 'portal_types')
  for contentType in portal_types.listTypeInfo():
    if hasattr(contentType, 'product'):
      if contentType.product in ('ERP5', 'Coramy', 'Nexedi'):
        msg += 'Change the Product Name of %s from %s to ERP5Type\n' % (contentType.getId(), contentType.product)
        contentType.product = 'ERP5Type'
  return msg

def changeObjectClass(self, object_id, new_class):
  """Creates a copy of object_id inside self, changing its class to
  new_class"""
  old_obj = self._getOb(object_id)
  self._delObject(object_id)
  new_obj = new_class(object_id)
  new_obj.__dict__.update(old_obj.__dict__)
  self._setObject(object_id, new_obj)
 

def updateBalanceTransactionClass(self):
  """Update Balance Transactions new indexing that occured around r16371
  """
  from Products.ERP5Type.Document.BalanceTransaction import BalanceTransaction
  from Products.ERP5Type.Document.BalanceTransactionLine\
                  import BalanceTransactionLine

  def reverseSourceAndDestination(self):
    destination_list = self.getValueList('source')
    source_list = self.getValueList('destination')
    destination_section_list = self.getValueList('source_section')
    source_section_list = self.getValueList('destination_section')
    destination_payment_list = self.getValueList('source_payment')
    source_payment_list = self.getValueList('destination_payment')
    stop_date = self.getStartDate()
    start_date = self.getStopDate()
    source_reference = self.getDestinationReference()
    destination_reference = self.getSourceReference()

    self.edit(destination_value_list=destination_list,
              source_value_list=source_list,
              destination_section_value_list=destination_section_list,
              source_section_value_list=source_section_list,
              destination_payment_value_list=destination_payment_list,
              stop_date=stop_date,
              start_date=start_date,
              source_reference=source_reference,
              destination_reference=destination_reference)

    if self.getPortalTypeName() != 'Balance Transaction':
      self.setQuantity( - self.getQuantity())

      stap = self.getDestinationTotalAssetPrice()
      dtap = self.getSourceTotalAssetPrice()
      if stap:
        self.setSourceTotalAssetPrice(stap)
      if dtap:
        self.setDestinationTotalAssetPrice(dtap)

  module = self.getPortalObject().accounting_module
  for obj in module.contentValues(filter=
                       dict(portal_type='Balance Transaction')):
    obj = obj.getObject()
    #print 'updating', obj, 'with class', BalanceTransaction
    changeObjectClass(module, obj.getId(), BalanceTransaction)
    get_transaction().commit(1)

    newobj = getattr(module, obj.getId())
    reverseSourceAndDestination(newobj)
    for subobj in newobj.getMovementList(
                portal_type=( 'Accounting Transaction Line',
                              'Balance Transaction Line', )):
      changeObjectClass(newobj, subobj.getId(), BalanceTransactionLine)
      reverseSourceAndDestination(subobj)
      #print '   subupdating', subobj, 'with class', BalanceTransactionLine
    
    # XXX 'something' activates some unindexObject calls, so activate our
    # reindexing after ...
    newobj.activate(after_method_id='unindexObject').recursiveReindexObject()

