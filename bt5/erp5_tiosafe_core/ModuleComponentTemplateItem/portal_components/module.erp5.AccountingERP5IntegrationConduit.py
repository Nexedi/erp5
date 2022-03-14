##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from base64 import b16encode

from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit

class AccountingERP5IntegrationConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize ERP5 Accountings
  """
  def __init__(self):
    self.xml_object_tag = 'transaction'

  def getGidFromObject(self, object): # pylint: disable=redefined-builtin
    """
      Return the Accounting GID of the object.
    """
    date = str(object.getStartDate())
    date = date.replace('-', '')
    date = date.replace('/', '')
    date = date.replace(':', '')
    return 'Accounting %s%s' % (object.getReference(), date)

  def getObjectType(self, xml):
    """
      Return the portal type of the object.
    """
    # Retrieve the namespace
    namespace = ''
    index = 0
    if xml.nsmap:
      index = 1
    # Build the namespace
    if index:
      namespace = "%s}" % xml.getchildren()[0].tag.split('}')[0]
    # Check if it's the good property that will be save
    category_tag = "%scategory" % namespace
    # Retrieve all categories tag
    categories = xml.findall(category_tag)
    journal = False
    # Browse the list of categories
    for node in categories:
      if 'Journal' in node.text:
        journal = node.text.split('/')[1]
    # Check by the name which portal type must be returns
    if journal in ('JC', 'JD'):
      return 'Accounting Transaction'
    elif journal in ('PI', 'PC'):
      return 'Purchase Invoice Transaction'
    elif journal in ('SC', 'SI'):
      return 'Sale Invoice Transaction'
    elif journal in ('BP', 'BR', 'CP', 'CR', 'PA',
        'PP', 'SA', 'SR', 'VP', 'VR'):
      return 'Payment Transaction'
    else:
      raise Exception("getObjectType: ERROR journal code unknown")

  def constructContent(self, object, object_id, portal_type): # pylint: disable=redefined-builtin
    """
      This allows to specify how to construct a new content.
      This is really usefull if you want to write your own Conduit.
    """
    # 'created_by_builder' property allows to doesn't call the init Script
    object.newContent(
        portal_type=portal_type,
        id=object_id,
        created_by_builder=1,
    )
    subobject = object._getOb(object_id)
    return subobject, 1, 1

  def _createContent(self, xml=None, object=None, object_id=None, # pylint: disable=redefined-builtin
      sub_object=None, reset_local_roles=0, reset_workflow=0, simulate=0,
      **kw):
    """
      This is the method calling to create an object
    """
    if object_id is None:
      object_id = self.getAttribute(xml, 'id')
    if True: # object_id is not None:
      if sub_object is None and object_id:
        sub_object = object._getOb(object_id, None)
      if sub_object is None: # If so, it does not exist
        portal_type = ''
        if xml.xpath('local-name()') == self.xml_object_tag:
          portal_type = self.getObjectType(xml)
        elif xml.xpath('name()') in self.XUPDATE_INSERT_OR_ADD: # Deprecated ?
          portal_type = self.getXupdateContentType(xml) # Deprecated ?
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            portal_type,
        )
        # Mapping between tag and element
        node_dict = {'arrow': self.visitArrow, 'movement': self.visitMovement}
        # Retrieve the namespace
        index = 0
        if xml.nsmap:
          index = 1
        # Browse the list to work on categories
        for node in xml.getchildren():
          # Only works on right tags, and no on the comments, ...
          if not isinstance(node.tag, str):
            continue
          # Build the split list of the tag
          split_tag = node.tag.split('}')
          if len(split_tag) > 1:
            index = len(split_tag) - 1
          else:
            index = 0
          # Build the tag (without is Namespace)
          tag = node.tag.split('}')[index]
          # Check if the subnodes of the transaction
          if tag in node_dict:
            node_dict[tag](document=sub_object, xml=node, **kw)
          elif tag == 'category':
            # TODO: Define in the integration site the mapping of this element
            # Define new type in the Integration Site, Category Integration
            # Mapping is useless here, it's another type which is necessary
            if node.text == 'Tax Code/T6':
              # HARDCODE: Link to Tax
              pass
      # Create the object in ERP5
      self.newObject(
          object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
      )
      return sub_object

  def visitArrow(self, document=None, xml=None, **kw):
    """
      Manage the addition of source and destination in an Accounting.
    """
    arrow_dict = {}
    # Retrieve the subscriber element
    domain = kw.get('domain')
    # Retrieve the namespace
    namespace = ''
    index = 0
    if xml.nsmap:
      index = 1
    # Build the namespace
    if index:
      namespace = "%s}" % xml.getchildren()[0].tag.split('}')[0]
    # Check if it's the good property that will be save
    category_tag = "%scategory" % namespace
    # Check if exist category
    if xml.find(category_tag) is not None:
      category = xml.find(category_tag)
      if category.text.lower() == 'ownership':
        # Dict of arrow property and sync
        arrow_dict = {
            'source': {
              'sync': self._getCorrespondingOfSynchronization(
                domain,
                'Organisation',
              ),
              'setter': document.setSourceSectionValue,
            },
            'destination': {
              'sync': self._getCorrespondingOfSynchronization(
                domain,
                'Organisation',
              ),
              'setter': document.setDestinationSectionValue,
            },
        }
      elif category.text.lower() == 'accounting':
        # Dict of arrow property and sync
        arrow_dict = {
            'source': {
              'sync': self._getCorrespondingOfSynchronization(
                domain,
                'Account',
              ),
              'setter': document.setSourceValue,
            },
            'destination': {
              'sync': self._getCorrespondingOfSynchronization(
                domain,
                'Account',
              ),
              'setter': document.setDestinationValue
            },
        }
      else:
        raise Exception("visitArrow: Unexpected Category")
    else:
      raise Exception(
          "visitArrow: It's a nonsense to put an arrow without category"
      )
    # Browse the XML subnode
    for subnode in xml.getchildren():
      # Only works on right tags, and no on the comments, ...
      if not isinstance(subnode.tag, str):
        continue
      tag = subnode.tag.split('}')[index]
      # Check the usefull of the different elements
      if tag in arrow_dict:
        # Check to retrieve the good Organisation or Account
        if subnode.text == 'Organisation MyFakeGidOrg':
          # Force the link to My Org
          link_object = document.organisation_module.objectValues(
              portal_type='Organisation',
              title ='my_org',
          )[0]
        else:
          if subnode.text:
            # Retrieve the object to bind
            subscriber = arrow_dict[tag]['sync']
            # Encode to the output type
            link_gid = subnode.text
            link_object = subscriber.getDocumentFromGid(b16encode(link_gid))
          else:
            link_object = None

        # Check if it's object or text element
        if link_object is not None:
          arrow_dict[tag]['setter'](link_object)
        else:
          error_message = "An element DOES NOT EXISTS."
          # Build and add the error message
          if document.getDescription() != error_message:
            # Build and add the error message
            description = '%s\n%s' % (document.getDescription(), error_message)
            document.setDescription(description)

  def visitMovement(self, document=None, xml=None, **kw):
    """
      Manage the addition of the Accounting Transaction Line.
    """
    # Create the new Line
    if document.getPortalType() == 'Purchase Invoice Transaction':
      accounting_line = document.newContent(
          portal_type='Purchase Invoice Transaction Line',
      )
    elif document.getPortalType() == 'Sale Invoice Transaction':
      accounting_line = document.newContent(
          portal_type='Sale Invoice Transaction Line',
      )
    elif document.getPortalType() == 'Payment Transaction' or\
        document.getPortalType() == 'Accounting Transaction':
      accounting_line = document.newContent(
          portal_type='Accounting Transaction Line',
      )
    # Retrieve the namespace
    index = 0
    if xml.nsmap:
      index = 1
    # Browse the XML subnode
    for subnode in xml.getchildren():
      # Only works on right tags, and no on the comments, ...
      if not isinstance(subnode.tag, str):
        continue
      tag = subnode.tag.split('}')[index]
      # Check the usefull of the different elements
      if tag == 'arrow':
        # Add the Source and the Destination of the movement
        self.visitArrow(document=accounting_line, xml=subnode, **kw)
      elif tag == 'resource':
        # XXX: Actually resource is FORCE as Currency Euro
        # Retrieve the currency object and add the property sheet on the line
        link_object = document.currency_module.objectValues(
            portal_type='Currency',
            reference='EUR',
        )[0]
        accounting_line.setResourceValue(link_object.getRelativeUrl())
      elif tag == "quantity":
        accounting_line.setQuantity(subnode.text)

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception("updateNode: Impossible to delete Accounting")

  def deleteNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception("deleteNode: Impossible to delete Accounting")

  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """
      This is the editDocument method inherit of ERP5Conduit. This method
      is used to save the information of a Accounting.
    """
    # TODO: Check the mapping
    # Here as example mapping of title and reference is useless, it's already
    # the good tag name
    # Map the XML tags to the PropertySheet
    mapping = {
        'title': 'title',
        'start_date': 'start_date',
        'stop_date': 'stop_date',
        'reference': 'reference',
    }
    # Translate kw with the PropertySheet
    property_ = {}
    for k, v in kw.items():
      k = mapping.get(k, k)
      property_[k] = v
    object._edit(**property_)
