##############################################################################
#
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


from Products.ERP5Type.Tool.ClassTool import ClassTool

COPYRIGHT = "Copyright (c) 2002-%s Nexedi SA and Contributors. All Rights Reserved." % DateTime().year()

def newConduit(self, class_id, REQUEST=None):
        """
          Create a document class used as Conduit
        """
        text = """\
##############################################################################
#
# %s
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

XUPDATE_INSERT_LIST = ('xupdate:insert-after', 'xupdate:insert-before')

class %s(TioSafeBaseConduit):
  '''
    This class provides some tools used by different TioSafe Conduits.
  '''

  def addNode(self, xml=None, object=None, sub_object=None, reset=None,
              simulate=None, **kw):
    '''
    A node is added

    xml : the xml wich contains what we want to add

    object : from where we want to add something

    previous_xml : the previous xml of the object, if any

    force : apply updates even if there's a conflict

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,subscriber_value]
    '''
    raise NotImplementedError

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    ''' This is a method called by the addNode that create object for the given xml'''
    raise NotImplementedError

  def _deleteContent(self, object=None, object_id=None):
    ''' This method allows to remove a product in the integration site '''
    raise NotImplementedError

  def updateNode(self, xml=None, object=None, previous_xml=None, force=False,
      simulate=False, reset=False, xpath_expression=None, **kw):
    '''
      This method browse the xml which allows to update data and update the
      correpsonging object.
    '''
    raise NotImplementedError

  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    '''
      This method is called in updateNode and allows to work on the update of
      elements.
    '''
    raise NotImplementedError

  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    ''' This method is called in updateNode and allows to remove elements. '''
    raise NotImplementedError

  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    ''' This method is called in updateNode and allows to add elements. '''
    raise NotImplementedError
""" % (COPYRIGHT, class_id)
        self.writeLocalDocument(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&manage_tabs_message=Conduit+Created' % (self.absolute_url(), class_id))


ClassTool.newDocument = newConduit
