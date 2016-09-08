from Products.ERP5Type.Globals import get_request
from Acquisition import aq_base
from Products.ERP5Type.Globals import PersistentMapping
from Products.CMFCore.utils import getToolByName
import transaction


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
  self._delOb(object_id)
  new_obj = new_class(object_id)
  new_obj.__dict__.update(old_obj.__dict__)
  if new_class.__module__ == 'erp5.portal_type':
    new_obj.portal_type = new_class.__name__
  # Workaround for new object which inherit from Folder or XMLobject
  # For the CMF objects, the sub-objects acts as attributes, but for the objects
  # inside they should be inside the HBTree to be called subobject.
  # This patch adds the objects as sub-objects for those erp5 objects
  if new_obj._getOb.__module__ == 'Products.ERP5Type.Core.Folder':
    for obj in old_obj.objectValues():
      # We don't want to keep the sub-objects as attributes for any objects
      # specifically for objects which we are shifting to dynamic portal_type
      # classes, cause if we edit or delete object, it would only delete the
      # object and not remove the attribute, which leads to error if we try
      # adding object with same id.
      delattr(new_obj, obj.id)
      new_obj._setOb(obj.id, obj)
  self._setOb(object_id, new_obj)
  if self._delOb.__module__ == 'OFS.ObjectManager':
    # Workaround OFS updating '_objects' in _[ds]etObject instead of _[ds]etOb
    for i in self._objects:
      if i['id'] == object_id:
        i['meta_type'] = getattr(new_obj, 'meta_type', None)
        break
  new_obj = self._getOb(object_id, new_obj)
  if new_obj.isIndexable:
    new_obj.reindexObject()
  elif new_obj.portal_type == 'Catalog':
    # In case of 'Catalog' portal_type, we don't want unindexing or reindexing
    # as we don't expect it to be indexable.
    pass
  else:
    old_obj.unindexObject()
  return new_obj

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
    destination_project_list = self.getValueList('source_project')
    source_project_list = self.getValueList('destination_project')
    destination_function_list = self.getValueList('source_function')
    source_function_list = self.getValueList('destination_function')
    stop_date = self.getStartDate()
    start_date = self.getStopDate()
    source_reference = self.getDestinationReference()
    destination_reference = self.getSourceReference()

    self.edit(destination_value_list=destination_list,
              source_value_list=source_list,
              destination_section_value_list=destination_section_list,
              source_section_value_list=source_section_list,
              destination_payment_value_list=destination_payment_list,
              source_payment_value_list=source_payment_list,
              destination_project_value_list=destination_project_list,
              source_project_value_list=source_project_list,
              destination_function_value_list=destination_function_list,
              source_function_value_list=source_function_list,
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
    transaction.savepoint(optimistic=True)

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


def updateCareerValidationState(self):
  """Career workflow changed its state variable name in r17169
  """
  module = self.getPortalObject().person_module
  for person in self.getPortalObject().person_module.contentValues(
                              filter=dict(portal_type='Person')):
    for career in person.contentValues(filter=dict(portal_type='Career')):
      if getattr(aq_base(career), 'workflow_history', None) is None:
        continue
      for line in career.workflow_history['career_workflow']:
        if 'state' in line:
          line['validation_state'] = line.pop('state')
      career.workflow_history._p_changed = 1
      career.reindexObject()
