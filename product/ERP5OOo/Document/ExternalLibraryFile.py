
##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5OOo.Document.ExternalDocument import ExternalDocument, SpiderException

from xml import sax

def stripName(s):
  return s[4:].replace('-','_').encode()

class BookInfo(object):
  id=title=description=''

class Handler(sax.handler.ContentHandler):
  stack=[]
  attrs=None
  c=''
  d=None
  results=[]

  def startElement(self,name,attrs):
    name=stripName(name)
    self.stack.append(name)
    self.attrs=attrs
    if hasattr(self,'start_'+name):
      getattr(self,'start_'+name)()

  def endElement(self,name):
    name=stripName(name)
    if hasattr(self,'end_'+name):
      getattr(self,'end_'+name)()
    self.stack.pop()
    self.attrs=None
    self.c=''

  def characters(self,c):
    self.c+=c.strip().encode('utf-8')

  def start_Record(self):
    self.d=BookInfo()
    self.results.append(self.d)

  def end_ID(self):
    self.d.id=self.c

  def end_Title(self):
    self.d.title+=self.c

  def end_Author(self):
    self.d.description+=self.c+'; '

  def end_Label_Information(self):
    self.d.description+=self.c+'; '

def parseLibraryFile(s):
  h=Handler()
  sax.parseString(s,h)
  return h.results


class ExternalLibraryFile(ExternalDocument):
  """
  get AU library data
  """
  # CMF Type Definition
  meta_type = 'ERP5 External Library File'
  portal_type = 'External Library File'
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.DMSFile
                    , PropertySheet.Document
                    , PropertySheet.Url
                    , PropertySheet.ExternalDocument
                    )

  def _processData(self,s,inf):
    # remove current subobjects
    self.manage_delObjects([i.getId() for i in self.searchFolder(portal_type='Book')])
    # parse xml file and iterate over results
    lista=parseLibraryFile(s)
    for i,o in enumerate(lista):
      n=self.newContent(portal_type='Book')
      self.log(n.getRelativeUrl())
      n.setTitle(o.title)
      n.setDescription(o.description)
      # copy attributes
      for atr in self.portal_types[self.getPortalType()].getInstanceBaseCategoryList():
        n.setProperty(atr,self.getProperty(atr))
      # partial commits (otherwise packet may exceed mysql max size)
      # XXX this should probably be deferred as portal_activities
      if i % 50 ==0:
        get_transaction().commit()
    self.log(len(lista))
    return 'k'*len(lista) # a hack to have number of objects in status message


# vim: filetype=python syntax=python shiftwidth=2 
