##############################################################################
#
# Copyright (c) 2009 Nexedi SA. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################


from Acquisition import Explicit, aq_base
from AccessControl import ClassSecurityInfo
from base64 import b16encode
from lxml import etree
from zLOG import LOG, ERROR
from DateTime import DateTime
from Products.ERP5Type.Cache import CachingMethod
import six

# Global variables
SEPARATOR = '\n'


class TioSafeBrain(Explicit):
  """
    The main brain class provides the generic method used by sub brain which
    allows to present the different TioSafe XML.
  """
  security = ClassSecurityInfo()
  security.declareObjectPublic()
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, object_type, context, **kw):
    self.path = context.getParentValue().getPath() + '/' + kw.get('id', '')
    self.object_type = object_type
    self.context = context
    # save properties as attributes
    for k,v in six.iteritems(kw):
      # FIXME: '0000-00-00 00:00:00' is an error find in the Prestashop sync
      if v is not None and v != '0000-00-00 00:00:00':
        setattr(self, k.lower(), v)

  def updateProperties(self, brain):
    """
    Update self properties with the one from
    another brain
    """
    for k,v in six.iteritems(brain.__dict__):
      setattr(self, k, v)

  def _asXML(self):
    """
    Must be overriden by subclasses
    """
    raise NotImplementedError

  def asXML(self, debug=False):
    """
    Build the TioSafe XML
    """
    return self._asXML()

  def getDefaultUnknownNodeGID(self):
    """
    Resource the gid of the node used when no node can be found
    """
    integration_site = self.getIntegrationSite()
    default_node = integration_site.getDestinationValue()
    return integration_site.person_module.getSourceSectionValue().getGidFromObject(default_node, encoded=False)

  def getDefaultUnknownResourceGID(self):
    """
    Resource the gid of the node used when no node can be found
    """
    integration_site = self.getIntegrationSite()
    default_node = integration_site.getResourceValue()
    return integration_site.product_module.getSourceSectionValue().getGidFromObject(default_node, encoded=False)

  def getDefaultOrganisationGID(self):
    """
    Return the gid of the shop
    """
    integration_site = self.getIntegrationSite()
    default_source = integration_site.getSourceAdministrationValue()
    return integration_site.organisation_module.getSourceSectionValue().getGidFromObject(default_source, encoded=False)


  def _getSynchronizationObjectList(self, sync_type, object_type_list):
    """
      Render the 'SyncML Publication' or the 'SyncML Subscription' list which
      correspond to the sync_type and the object_type.
    """
    if not isinstance(object_type_list, list):
      object_type_list = [object_type_list,]

    def cached_getSynchronizationObjectList(sync_type, object_type):
      context = self.context
      module_list = []
      object_module_id = object_type.lower().replace(' ', '_')
      for module in context.getIntegrationSite().contentValues(portal_type="Integration Module"):
        if object_module_id in module.getId():
          module_list.append(module)

      if not len(module_list):
        raise ValueError("Impossible to find a module for %s" % object_type)

      sync_object_list = []
      for module in module_list:
        # init shortcut of module's data
        module_source = module.getSourceSectionValue()
        module_destination = module.getDestinationSectionValue()
        source_portal_type = module_source.getSourceValue().getPortalType()
        destination_portal_type = module_destination.getSourceValue().getPortalType()

        # only work on the ERP5 or TioSafe sync
        assert sync_type in ("tiosafe", "erp5"), sync_type
        if (sync_type == "erp5") ^ (source_portal_type == "Integration Module"):
          # render the source if:
          #  1. sync_type == erp5 and source_portal_type != Integration Module
          #  2. sync_type != erp5 and source_portal_type == Integration Module
          sync_object_list.append(module_source.getPath())
        elif (sync_type == "tiosafe") ^ (destination_portal_type != "Integration Module"):
          # render the destination if:
          #  1. sync_type == tiosafe and destination_portal_type == Integration Module
          #  2. sync_type != tiosafe and destination_portal_type != Integration Module
          sync_object_list.append(module_destination.getPath())
        else:
          raise ValueError("Impossible to find pub/sub related to Integration Module, pub = %s with source = %s, sub = %s with source = %s" %(
              module.getSourceSection(),
              module_source.getSource(),
              module.getDestinationSection(),
              module_destination.getSource(),
              ))
      return sync_object_list

    # Cache sync object list
    cached_getSynchronizationObjectList = CachingMethod(cached_getSynchronizationObjectList,
                                                        id="TioSafeBrain_getSynchronizationObjectList",
                                                        cache_factory='erp5_content_long')
    object_list = []
    for object_type in object_type_list:
      object_list.extend(cached_getSynchronizationObjectList(sync_type, object_type))
    portal = self.context.getPortalObject()
    return [portal.restrictedTraverse(x) for x in object_list]

  def getTioSafeSynchronizationObjectList(self, object_type):
    """ return the synchronization pub/sub which is used
    to retrieve object from plugin
    """
    return self._getSynchronizationObjectList(sync_type="tiosafe", object_type_list=object_type)

  def getERP5SynchronizationObjectList(self, object_type):
    """ return the synchronization pub/sub which is used
    to retrieve object from ERP5
    """
    return self._getSynchronizationObjectList(sync_type="erp5", object_type_list=object_type)

  def getPortalType(self):
    """ return the portal type """
    return self.object_type

  def getGid(self, encoded=None):
    """ Return the GID of the object. """
    if getattr(self, 'gid', None) is None:
      # GID is build from definition on integration module
      integration_module = self.context.getParentValue()
      prefix = integration_module.getGidPrefix("")
      property_list = integration_module.getGidPropertyList()
      gid = prefix
      for prop in property_list:
        try:
          prop_value = getattr(self, prop)
        except AttributeError:
          raise AttributeError("The brain doesn't have the property %s" % prop)
        gid += " %s" %(prop_value,)

      self.gid = gid

    if encoded is not None:
      return b16encode(self.gid)
    return self.gid

  def getIntegrationSite(self):
    """ Retrieve the integration site """
    parent = self.context.getParentValue()
    while not parent.getPortalType() == "Integration Site":
      parent = parent.getParentValue()
    return parent

  def getId(self):
    """ Return the id of the element. """
    return self.id

  def getPhysicalPath(self):
    """ Return the Physical Path of the object. """
    return tuple(self.path.split('/'))


  def getPath(self):
    """ Return the Path of the object. """
    return str(self.path)

  def _setTagList(self, document=None, xml=None, tag_list=None, separator=None):
    """
      This method set on an XML node some sub-nodes which are the properties
      (define in tag_list) of a document given as parameter.
    """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)
    # list which allows to realise a specific work on date
    date_list = ['birthday', 'start_date', 'stop_date']
    # marker for checking property existency
    MARKER = object()

    for key in tag_list:
      # getattr retrieves the MARKER imply that property doesn't provided
      if getattr(document, key, MARKER) is not MARKER:
        text = getattr(document, key)
        # if a separator is provides, browse the element's list else it's a
        # single element
        if separator:
          text_list = text.split(separator)
          text_list.sort() # XXX- If the fix point fails se me
        else:
          text_list = [text,]
        for text in text_list:
          if text:
            if key in date_list:
              # work on correct date else put an empty value
              try:
                text = str(DateTime(text))
              except DateTime.DateError:
                text = ""
            element = etree.SubElement(xml, key)
            element.text = text

  def _setArrowTag(self, document=None, xml=None, source_tag='source',
      destination_tag='destination', category=''):
    """ This method build the XML of the arrow. """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)
    sync_list = self.getTioSafeSynchronizationObjectList(object_type="Person")

    # create the arrow tag and set if exist source and destination
    arrow = etree.SubElement(xml, 'arrow', type=category)
    arrow_list = [(source_tag, 'source'), (destination_tag, 'destination')]
    for prop, tag in arrow_list:
      if getattr(document, prop, None) is not None:
        movement = etree.SubElement(arrow, tag)
        object_id = getattr(document, prop)
        if object_id != 'default_node':
          for sync in sync_list:
            try:
              brain_node = sync.getObjectFromId(object_id)
              node_gid = brain_node.getGid()
              break
            except (ValueError, AttributeError):
              # This is not a document, might be a category, or the gid previously built
              # pass it anyway in xml
              node_gid = None

          if node_gid is None:
            node_gid = self.getDefaultUnknownNodeGID()
          movement.text = node_gid
        else:
          movement.text = self.getDefaultOrganisationGID()

  def _setArrowTagList(self, document=None, xml=None):
    """ This method set all possible arrows on the XML. """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)
    # marker for checking property existency
    MARKER = object()

    # build the list which contains the properties
    # IF THIS LIST IS UPDATE THINK TO KEEP THE ALPHABETIC ORDER
    arrow_data_list = [
        ['source', 'destination', ''],
        ['source_accounting', 'destination_accounting', 'Accounting'],
        ['source_administration', 'destination_administration', 'Administration'],
        ['source_carrier', 'destination_carrier', 'Carrier'],
        ['source_decision', 'destination_decision', 'Decision'],
        ['source_invoice', 'destination_invoice', 'Invoice'],
        ['source_ownership', 'destination_ownership', 'Ownership'],
        ['source_payment', 'destination_payment', 'Payment'],
    ]
    # browse the arrow's data and build the arrow when it's possible
    for sub_list in arrow_data_list:
      source, destination, category = sub_list
      if getattr(document, source, MARKER) is not MARKER or \
          getattr(document, destination, MARKER) is not MARKER:
        # set the arrow tag
        self._setArrowTag(
            document=document,
            xml=xml,
            source_tag=source,
            destination_tag=destination,
            category=category,
        )


# ----------- Brain for insert in Integration Site ---------- #
# XXX-Aurel : this must be handle by the base brain class
class LastId(TioSafeBrain):
  __allow_access_to_unprotected_subobjects__ = 1

  def getId(self):
    """ Return the last id of the table in the database. """
    # XXX-Aurel : this must be based on the GID definition
    # As GID in TioSafe case is unique, it must be used to get
    # the last ID of an inserted object (usefull for cases where
    # transactionnal operation is not provided like with prestashop)
    #raise ValueError, self.last_id
    return TioSafeBrain.getId(self)

class Node(TioSafeBrain):
  """
    This class allows to build the TioSafe XML of a Node and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def _generateCoordinatesXML(self, node):
    """ Generate the XML for addresses sub-objects & phones"""

    # Phones
    phone_tag_list = ['phone', 'cellphone']
    for tag in phone_tag_list:
      value = getattr(self, "%s" %(tag), '')
      if value:
        element = etree.SubElement(node, tag)
        element.text = value

    # Fax
    value = getattr(self, "fax", '')
    if value:
      element = etree.SubElement(node, 'fax')
      element.text = value

    MARKER = object()
    node_address_method = "get%sAddressList" %(self.getPortalType(),)
    module_id = "%s_module" %(self.getPortalType().lower(),)
    module = getattr(self.context, module_id)
    if getattr(module, node_address_method, MARKER) is not MARKER:
      # order address list
      ordered_address_list = []

      parameter_kw = {"%s_id" %(self.getPortalType().replace(" ", "_").lower(),) : str(self.getId())}

      for element in getattr(module, node_address_method)(**parameter_kw):
        # Save the country after realisation of the mapping
        if getattr(element, 'country', None):
          country = self.getIntegrationSite().getCategoryFromMapping(
            category = 'Country/%s' % element.country, create_mapping=True,
            create_mapping_line=True,
          )
          element.country = '/'.join(country.split('/')[1:])

        full_address = '%s %s %s %s' % (
            getattr(element, 'street', ''),
            getattr(element, 'zip', ''),
            getattr(element, 'city', ''),
            getattr(element, 'country', ''),
        )
        ordered_address_list.append((full_address, element))
      ordered_address_list.sort()

      for full_address, element in ordered_address_list:
        address = etree.SubElement(node, 'address')
        tag_list = ('street', 'zip', 'city', 'country', )
        self._setTagList(element, address, tag_list)

  def _setRoleList(self, node):
    """
    Define the role as a client by default
    """
    # by default assume we synchronize client
    # if not this method must be overriden
    element = etree.SubElement(node, 'category')
    element.text = 'role/client'

  def _setRelation(self, node):
    """
    Add the relation tag which link a person to an organisation
    """
    if self.object_type == "Person":
      if getattr(self, "relation", None) is not None:
        # this must be the gid of organisatin
        # we suppose here that we get the id in self.relation
        # in other cases, this method must be overriden
        tiosafe_sync_list = self.getTioSafeSynchronizationObjectList(object_type='Organisation')
        for tiosafe_sync in tiosafe_sync_list:
          try:
            brain_node = tiosafe_sync.getObjectFromId(self.relation)
            organisation_gid = brain_node.getGid()
            break
          except (ValueError, AttributeError):
            organisation_gid = None

        if organisation_gid is None:
          raise ValueError("Impossible to find organisation for id %s on node %s" %(self.relation, self.path))
      else:
        organisation_gid = ""
      # set the tag
      if organisation_gid:
        element = etree.SubElement(node, 'relation')
        element.text = organisation_gid

  def _asXML(self):
    node_type = self.context.getDestinationObjectType()
    node = etree.Element('node', type=node_type)

    # list of possible tags for a node
    tag_list = (
      'title', 'firstname', 'lastname', 'email', 'birthday',
      )
    self._setTagList(self, node, tag_list)

    try:
      self._generateCoordinatesXML(node)
    except ValueError:
      # Missing mapping
      return None

    # Role must be defined here if there is specific - client/internal/...
    self._setRoleList(node)
    # Define relation, must be the GID
    self._setRelation(node)

    xml = etree.tostring(node, pretty_print=True, encoding='utf-8')
    LOG('Node asXML returns : %s' % (xml, ), 300, "")
    return xml

class Resource(TioSafeBrain):
  """
    This class allows to build the TioSafe XML of a Resource and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, *args, **kw):
    self.category = []
    self.mapping_property_list = []
    TioSafeBrain.__init__(self, *args, **kw)

  def _generateMappingXML(self, resource):
    """
    Specific part for the mapped property
    """
    # sort categories
    def cat_cmp(a, b):
      return cmp(a['category_list'], b['category_list'])
    self.mapping_property_list.sort(cmp=cat_cmp)

    for mapping in self.mapping_property_list:
      element = etree.SubElement(resource, 'mapping')
      category_list = mapping['category_list']
      category_list.sort()
      for category_value in category_list:
        category = etree.SubElement(element, 'category')
        category.text = category_value
      mapping.pop('category_list')
      for k, v in six.iteritems(mapping):
        prop = etree.SubElement(element, k)
        prop.text = v

  def _asXML(self):
    resource_type = self.context.getDestinationObjectType()
    resource = etree.Element('resource', type=resource_type)

    # First defined basic tags
    tag_list = (
      'title', 'reference', 'ean13',
      'description',
    )
    self._setTagList(self, resource, tag_list)

    # Then build & add the list of variations
    category_list = []
    # - Categorie can already have been retrieve
    if isinstance(self.category, str):
      self.category = self.category.split(SEPARATOR)
    category_list = self.category[:]
    # - Categories can also be retrieved using specific query
    module_id = "%s_module" %(self.getPortalType().lower(),)
    module = getattr(self.context, module_id)
    get_category_method = "get%sCategoryList" % self.getPortalType()
    MARKER = object()
    if getattr(module, get_category_method, MARKER) is not MARKER:
      # add category list
      parameter_kw = {"%s_id" %(self.getPortalType().replace(" ", "_").lower(),) : str(self.getId())}
      for element in getattr(module, get_category_method)(**parameter_kw):
        # XXX-Aurel : This code is bad as it assumes it will return a list in any case
        try:
          category = self.getIntegrationSite().getCategoryFromMapping(
            category=element.category, create_mapping=True
            )
        except ValueError:
          return None
        category_list.append(category)

    # - Order the category list
    category_list.sort()
    # - Add the categories to the product's xml
    for category_value in category_list:
      category = etree.SubElement(resource, 'category')
      category.text = category_value

    self._generateMappingXML(resource)

    xml = etree.tostring(resource, pretty_print=True, encoding='utf-8')
    LOG("Resource asXML returns : %s" % (xml, ), 300, "")
    return xml

class Transaction(TioSafeBrain):
  """
    This class allows to build the TioSafe XML of a Sale Order and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, object_type, context, **kw):
    self.source = "default_node"
    self.source_ownership = "default_node"
    self.source_decision = "default_node"
    self.source_administration = "default_node"
    TioSafeBrain.__init__(self, object_type, context, **kw)

  def getVATCategory(self, vat_value):
    """
    This returns the VAT category according to the value set
    """
    def cached_buildVATDict():
      vat_dict = {}
      trade_condition = self.getIntegrationSite().getDefaultSourceTradeValue()

      while len(trade_condition.contentValues(portal_type="Trade Model Line")) == 0:
        # Must find a better way to browse specialised objects
        specialized_trade_condition = trade_condition.getSpecialiseValue()
        if specialized_trade_condition is None or specialized_trade_condition.getPortalType() == "Business Process":
          raise ValueError('Impossible to find a trade condition containing VAT lines, last trade condition was %s, parent was %s' %(specialized_trade_condition, trade_condition))
        else:
          trade_condition = specialized_trade_condition

      for vat_line in trade_condition.contentValues(portal_type="Trade Model Line"):
        # LOG("browsing line %s" %(vat_line.getPath(), 300, "%s" %(vat_line.getBaseApplicationList(),)))
        for app in vat_line.getBaseApplicationList():
          if "base_amount/trade/base/taxable/vat/" in app:
            vat_dict["%.2f" %(vat_line.getPrice()*100.)] = app.split('/')[-1]
      # LOG("vat_dict is %s" %(vat_dict), 300, "")
      return vat_dict

    cached_getSynchronizationObjectList = CachingMethod(cached_buildVATDict,
                                                        id="TioSafeBrain_cached_buildVATDict",
                                                        cache_factory='erp5_content_long')
    vat_dict = cached_buildVATDict()
    return vat_dict["%.2f" %(float(vat_value))]

  def _setPaymentMode(self, txn):
    """
    Define the payment mode of a transaction
    This must be the category payment_mode/XXX
    """
    if getattr(self, 'payment_mode', None) is not None:
      payment_mapping = self.getIntegrationSite().getCategoryFromMapping(
        category='Payment Mode/%s' % getattr(self, 'payment_mode'),
        create_mapping=True,
        create_mapping_line=True,
        )
      element = etree.SubElement(txn, 'payment_mode')
      element.text = payment_mapping.split('/', 1)[-1]

  def _asXML(self):
    transaction_type = self.context.getDestinationObjectType()
    transaction = etree.Element('transaction', type=transaction_type)
    tiosafe_sync_list = self.getTioSafeSynchronizationObjectList(object_type='Product')
    erp5_sync_list = self.getERP5SynchronizationObjectList(object_type='Product')
    integration_site = self.getIntegrationSite()

    # marker for checking property existency
    MARKER = object()

    # list of possible tags for a sale order
    tag_list = (
        'title', 'start_date', 'stop_date', 'reference', 'currency',
    )
    self._setTagList(self, transaction, tag_list)
    self._setTagList(self, transaction, ['category', ], SEPARATOR)
    # set arrow list
    try:
      self._setPaymentMode(transaction)
      self._setArrowTagList(self, transaction)
    except ValueError:
      # A mapping must be missing
      return None

    # order the movement list
    movement_list = []

    # build a list of 2-tuple
    # the first key contains the sort element
    # the second part of the tuple contains a dict which contains all the data
    # of the transaction line
    method_id = self.getPortalType().replace(' ', '')
    portal_type = self.getPortalType().replace(' ', '_').lower()
    line_type_list = ['', 'Delivery', 'Discount', ]

    module_id = "%s_module" %(portal_type)
    module = getattr(integration_site, module_id)

    for line_type in line_type_list:
      getter_line_method = getattr(
          module,
          'get%s%sLineList' % (line_type, method_id),
          MARKER,
      )
      if getter_line_method is not MARKER:
        # browse each transaction lines, build the sort element and set data
        parameter_kw = {'%s_id' % portal_type: str(self.getId()), }
        for line in getter_line_method(**parameter_kw):
          key_list = ['title', 'resource', 'reference', 'quantity', 'price']
          value_list = [getattr(line, x, '') for x in key_list]
          movement_dict = {'context': line,}
          # set to None the '' value of the list
          for k, v in zip(key_list, value_list):
            movement_dict[k] = v or None

          # set the VAT value
          movement_dict['VAT'] = self.getVATCategory(getattr(line, 'vat', None))

          # the following boolean var allows to check if variation will be sync
          variation_sync = True

          # retrieve the resource and the gid in the line
          if not line_type:
            # work on transaction lines
            for tiosafe_sync in tiosafe_sync_list:
              try:
                # FIXME: Is it always product_id give as parameter ?
                brain_node = tiosafe_sync.getObjectFromId(line.product_id)
                resource_gid = brain_node.getGid()
                break
              except (ValueError, AttributeError):
                resource_gid = None

            if resource_gid is None:
              resource_gid = self.getDefaultUnknownResourceGID()

            for erp5_sync in erp5_sync_list:
              try:
                resource = erp5_sync.getDocumentFromGid(b16encode(resource_gid))
                break
              except (ValueError, AttributeError):
                resource = None
                # do not sync variations with the Unknown product
                variation_sync = False
          else:
            # do not sync variations with delivery or discount
            variation_sync = False
            # work on delivery and discount transaction lines
            resource_gid = resource_id = line.resource
            try:
              brain_node = tiosafe_sync.getObjectFromId(resource_id)
              resource_gid = brain_node.getGid()
            except (ValueError, AttributeError):
              # case of default delivery/discount
              if not 'Service' in resource_id:
                resource_gid = ' Unknown'
              LOG(
                  'Transaction, getting resource failed',
                  300,
                  'resource_id = %s, remains %s' % (resource_id, resource_gid),
              )
              pass
            # through the type render the delivery or the discount
            if line_type == 'Discount':
              resource = integration_site.getSourceCarrierValue()
            elif line_type == 'Delivery':
              resource = integration_site.getDestinationCarrierValue()
            else:
              raise ValueError('Try to work on "%s" which is an invalid type.' % line_type)
          # after the work on the line set the resource value which will be
          # render in the xml
          movement_dict['resource'] = resource_gid

          # browse line variations and set them to a list
          getter_line_category_method = getattr(
              module,
              'get%sLineCategoryList' % method_id,
              MARKER,
          )
          category_value_list = [getattr(line, 'category', ''), ]
          # FIXME: variation are sync only on line with a product ?
          # else don't sync variations for delivery, discount and Unknown prodcut
          if variation_sync and \
              getter_line_category_method is not MARKER:
            parameter_kw = {
                '%s_id' % portal_type: str(self.getId()),
                '%s_line_id' % portal_type: str(line.getId()),
            }
            for brain in getter_line_category_method(**parameter_kw):
              try:
                category_value_list.append(
                    integration_site.getCategoryFromMapping(
                        brain.category,
                        resource,
                    )
                )
              except ValueError:
                return None

          # sort categories, build the sort key and set categoires in the dict
          if len(category_value_list):
            category_value_list.sort()
            movement_dict['category'] = category_value_list
          # build the element which allows to sort
          movement_list.append(movement_dict)

    # Sort the movement list for fix point
    def cmp_resource(a,b):
      a_str = "%s %s %s" %(a['resource'], a['title'], ' '.join(a['category']))
      b_str = "%s %s %s" %(b['resource'], b['title'], ' '.join(b['category']))
      return cmp(a_str, b_str)

    movement_list.sort(cmp=cmp_resource)

    # the second part build the XML of the transaction
    # browse the ordered movement list and build the movement list as a result
    # the xml through of the line data in the dict
    for movement_dict in movement_list:
      movement = etree.SubElement(transaction, 'movement')
      # set arrow list on the movement
      self._setArrowTagList(movement_dict['context'], movement)
      # if exist the following tags in the line dict, add them in the xml
      tag_list = ('resource', 'title', 'reference', 'quantity', 'price', 'VAT')
      for tag in tag_list:
        if tag in movement_dict:
          element = etree.SubElement(movement, tag)
          element.text = movement_dict[tag]
      # add the categories to the movement
      for category_value in movement_dict['category']:
        if len(category_value):
          category = etree.SubElement(movement, 'category')
          category.text = category_value

    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    LOG("Transactions asXML returns : %s" % (xml, ), 300, "")
    return xml


# All the following classes has to be removed from the brain
# Use & improve abstract classes instead

# class Opportunity(TioSafeBrain):
#   """
#     This class allows to build the TioSafe XML of an Opportunity and to sync.
#   """
#   __allow_access_to_unprotected_subobjects__ = 1

#   def asXML(self):
#     """
#       Generate the TioSafe Opportunity XML through the properties of an object.
#     """
#     resource = etree.Element('resource', reference=self.getGid())

#     # list of possible tags for an product
#     tag_list = (
#         'title', 'reference', 'source', 'account', 'campaign', 'probability',
#         'price',
#     )
#     self._setTags(self, resource, tag_list)
#     self._setTags(self, resource, ['category', ], SEPARATOR)

#     return etree.tostring(resource, pretty_print=True, encoding='utf-8')


# class Campaign(TioSafeBrain):
#   """
#     This class allows to build the TioSafe XML of an Camapign and to sync.
#   """
#   __allow_access_to_unprotected_subobjects__ = 1

#   def asXML(self):
#     """
#       Generate the TioSafe Campaign XML through the properties of an object.
#     """
#     resource = etree.Element('resource', reference=self.getGid())

#     # list of possible tags for an product
#     tag_list = (
#         'title', 'reference', 'start_date', 'stop_date', 'source', 'price',
#         'description',
#     )
#     self._setTags(self, resource, tag_list)
#     self._setTags(self, resource, ['category', ], SEPARATOR)

#     return etree.tostring(resource, pretty_print=True, encoding='utf-8')


# # ########## Brain for TioSafe Transactions ########## #
# class Accounting(TioSafeBrain):
#   """
#     This class allows to build the TioSafe XML of an Accounting and to sync.
#   """
#   __allow_access_to_unprotected_subobjects__ = 1

#   def getGid(self):
#     """ Return the GID of the object. """
#     # FIXME: Why we must remove -, / and : ???
#     return self.gid.replace('-', '').replace('/', '').replace(':', '')

#   def asXML(self):
#     """
#       Generate the TioSafe Accounting XML through the properties of an object.
#     """
#     transaction = etree.Element('transaction', reference=self.getGid())

#     # list of possible tags for an accounting
#     tag_list = (
#         'start_date', 'stop_date', 'reference', 'currency', 'causality',
#     )
#     self._setTags(self, transaction, tag_list)
#     self._setTags(self, transaction, ['category', ], SEPARATOR)

#     # set arrow list
#     self._setArrowTagList(self, transaction)

#     # add the movements list to the XML
#     for element in self.accounting_line(id_accounting=self.getId()):
#       movement = etree.SubElement(transaction, 'movement')
#       # set arrow list
#       self._setArrowTagList(element, movement)
#       # list of possible tags for an accounting movement
#       tag_list = ('title', 'resource', 'quantity', 'price', )
#       self._setTags(element, movement, tag_list)
#       self._setTags(element, movement, ['category', ], SEPARATOR)

#     return etree.tostring(transaction, pretty_print=True, encoding='utf-8')




# # The brain of a Trasaction type: Event
# class Event(TioSafeBrain):
#   """
#     This is the Brain which works on Sale Orders.
#   """

#   __allow_access_to_unprotected_subobjects__ = 1

#   def asXML(self):
#     """
#       Return the GID of the object.
#     """
#     # Declare the main xml node and build the first xml level
#     event = etree.Element('event', reference=self.getGid())
#     tag_list = (
#         'title', 'start_date', 'stop_date', 'reference', 'location',
#         'description', 'product', 'account',
#     )
#     self._setTags(self, event, tag_list)
#     self._setTags(self, event, ['category', ], SEPARATOR)
#     # Set arrows in the first xml level
#     self._setArrowTagList(self, event)

#     return etree.tostring(event, pretty_print=True, encoding='utf-8')


# # ########## WebService Brain ########## #
# class LastIdWebServiceBrain(TioSafeBrain, LastId):
#   __allow_access_to_unprotected_subobjects__ = 1


# # ---------- SF ---------- #
# class PersonSalesforceBrain(TioSafeBrain, Node):
#   __allow_access_to_unprotected_subobjects__ = 1

#   def __init__(self, context, **kw):
#     super(PersonSalesforceBrain, self).__init__(context, **kw)
#     # add properties
#     setattr(self, 'path', '%s/%s' % (context.getPath(), self.getId()))
#     setattr(self, 'gid', 'Person %s %s' % (self.title, self.email))

# class EventSalesforceBrain(TioSafeBrain, Event):
#   __allow_access_to_unprotected_subobjects__ = 1

#   def __init__(self, context, **kw):
#     super(EventSalesforceBrain, self).__init__(context, **kw)
#     # Use person GIDs for source and destination, here context is the
#     # integration site
#     self.source = context.person_module(id=self.source)[0].getGid()
#     self.destination = context.person_module(id=self.destination)[0].getGid()
#     # add properties
#     setattr(self, 'path', '%s/%s' % (context.getPath(), self.id))
#     setattr(self, 'gid', 'Event %s %s %s' % (self.start_date, self.source, self.destination))
