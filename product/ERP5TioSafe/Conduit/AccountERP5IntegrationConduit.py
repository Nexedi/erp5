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

from Products.ERP5TioSafe.Conduit.TioSafeBaseConduit import TioSafeBaseConduit
from lxml import etree

class AccountERP5IntegrationConduit(TioSafeBaseConduit):
  """
    Conduit use to synchonize ERP5 Accounts
  """
  def __init__(self):
    self.xml_object_tag = 'node'

  def getGidFromObject(self, object):
    """
      Return the Account GID of the object.
    """
    return 'Account %s' % object.getReference()

  def getObjectType(self, xml):
    """
      Return the portal type of the object.
    """
    return 'Account'

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    """
      This is the method calling to create an object
    """
    if object_id is None:
      object_id = self.getAttribute(xml, 'id')
    if object_id is not None:
      if sub_object is None:
        try:
          sub_object = object._getOb(object_id)
        except (AttributeError, KeyError, TypeError):
          sub_object = None
      if sub_object is None: # If so, it doesn't exist
        portal_type = ''
        if xml.xpath('local-name()') == self.xml_object_tag:
          portal_type = self.getObjectType(xml)
        elif xml.xpath('name()') in self.XUPDATE_INSERT_OR_ADD: # Deprecated ???
          portal_type = self.getXupdateContentType(xml) # Deprecated ???
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            portal_type,
        )
        # Browse the list of arrows and movements
        for node in xml.getchildren():
          # Only works on right tags, and no on the comments, ...
          if type(node.tag) is not str:
            continue
          # Build the split list of a tag to test the namespace
          split_tag = node.tag.split('}')
          if len(split_tag) > 1:
            index = len(split_tag) - 1
          else:
            index = 0
          # Build the tag (without is Namespace)
          tag = node.tag.split('}')[index]
          # Work on categories
          if tag == 'category':
            # TODO: Work on each categories root/1/2/3/...
            # Split on the '/' element
            category = node.text.split('/')
            if category[0] == 'Reference':
              sub_object.setReference(category[1])
            else:
              pass
      # Build the content of new Person
      self.newObject(object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
      )
    return sub_object

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0,
      simulate=0,  **kw):
    raise Exception("updateNode: Impossible to update Account")

  def deleteNode(self, xml=None, object=None, previous_xml=None, force=0,
      simulate=0,  **kw):
    raise Exception("deleteNode: Impossible to delete Account")

  def editDocument(self, object=None, **kw):
    """
      This is the editDocument method inherit of ERP5Conduit. This method
      is used to save the information of a Account.
    """
    # TODO: Check the mapping
    # Map the XML tags to the PropertySheet
    mapping = {'title': 'title',
               'description': 'description'}
    # Translate kw with the PropertySheet
    property = {}
    for k, v in kw.items():
      k = mapping.get(k, k)
      property[k] = v
    object._edit(**property)

