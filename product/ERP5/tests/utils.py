##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

import os
import tarfile
import xml.parsers.expat
import xml.dom.minidom
from six.moves.urllib.request import url2pathname
from ZODB.DemoStorage import DemoStorage
from ZODB import DB
from Products.ERP5Type.XMLExportImport import importXML
import six

if int(os.environ.get('erp5_report_new_simulation_failures') or 0):
  newSimulationExpectedFailure = lambda test: test
else:
  from unittest import expectedFailure as newSimulationExpectedFailure

# Keep a global reference to a ZODB storage so that we can import business
# template xml files. XXX this connection will remain open.
db = DB(DemoStorage())
connection = db.open()


class BusinessTemplateInfoBase:

  def __init__(self, target):
    self.target = target
    self.setUp()

  def setUp(self):
    self.title = ''
    self.modules = {}
    self.allowed_content_types = {}
    self.actions = {}

    self.setUpTitle()
    self.setUpModules()
    self.setUpAllowedContentTypes()
    self.setUpActions()

  def findFileInfosByName(self, startswith='', endswith=''):
    raise NotImplementedError

  def getFileInfo(self, name):
    raise NotImplementedError

  def getFileInfoName(self, fileinfo):
    raise NotImplementedError

  def readFileInfo(self, fileinfo):
    raise NotImplementedError

  def getPrefix(self):
    raise NotImplementedError

  def setUpTitle(self):
    for i in self.findFileInfosByName(endswith='/bt/title'):
      self.title = self.readFileInfo(i)

  def setUpModules(self):
    name = '%s/ModuleTemplateItem/' % self.getPrefix()
    for i in self.findFileInfosByName(startswith=name, endswith='.xml'):
      source = self.readFileInfo(i)
      doc = xml.dom.minidom.parseString(source)
      module_id = doc.getElementsByTagName('id')[0].childNodes[0].data
      portal_type = doc.getElementsByTagName('portal_type')[0].childNodes[0].data
      self.modules[module_id] = portal_type

  def setUpAllowedContentTypes(self):
    name = '%s/PortalTypeAllowedContentTypeTemplateItem/allowed_content_types.xml' % self.getPrefix()
    try:
      fileinfo = self.getFileInfo(name)
    except NotFoundError:
      return
    source = self.readFileInfo(fileinfo)
    doc = xml.dom.minidom.parseString(source)
    for portal_type_node in doc.getElementsByTagName('portal_type'):
      portal_type = portal_type_node.getAttribute('id')
      self.allowed_content_types[portal_type] = []
      for item in portal_type_node.getElementsByTagName('item'):
        self.allowed_content_types[portal_type].append(item.childNodes[0].data)

  def setUpActions(self):

    def parse(file_path):
      action_information = importXML(connection, file_path)
      action_information.__repr__()
      for key, value in six.iteritems(action_information.__dict__):
        if value not in (None, "") and key in ('action', 'condition') :
          setattr(action_information, key, value.text)
      actions = action_information.__dict__.copy()
      return actions

    name = '%s/ActionTemplateItem/portal_types/' % self.getPrefix()
    for i in self.findFileInfosByName(startswith=name, endswith='.xml'):
      portal_type = url2pathname(self.getFileInfoName(i).split('/')[-2])
      if not portal_type in self.actions:
        self.actions[portal_type] = []
      data = parse(i)
      self.actions[portal_type].append(data)


class NotFoundError(Exception):
  """FileInfo does not exists."""


class BusinessTemplateInfoTar(BusinessTemplateInfoBase):

  def __init__(self, target):
    self.target = tarfile.open(target, 'r:gz')
    self.setUp()

  def getPrefix(self):
    return self.title

  def findFileInfosByName(self, startswith='', endswith=''):
    for tarinfo in self.target.getmembers():
      if (tarinfo.name.startswith(startswith) and
          tarinfo.name.endswith(endswith) and
          tarinfo.type==tarfile.REGTYPE):
        yield tarinfo

  def getFileInfo(self, name):
    try:
      return self.target.getmember(name)
    except KeyError:
      raise NotFoundError

  def getFileInfoName(self, fileinfo):
    return fileinfo.name

  def readFileInfo(self, fileinfo):
    return self.target.extractfile(fileinfo).read()


class BusinessTemplateInfoDir(BusinessTemplateInfoBase):

  def getPrefix(self):
    return self.target

  def findFileInfosByName(self, startswith='', endswith=''):
    allfiles = []
    for root, dir_list, file_list in os.walk(self.target):
      # We can drop this block as we no longer use Subversion.
      if '.svn' in root.split(os.path.sep):
        continue
      for file_ in file_list:
        path = os.path.join(self.target, root, file_)
        if os.path.isfile(path):
          allfiles.append(path)
    for i in allfiles:
      if i.startswith(startswith) and i.endswith(endswith):
        yield i

  def getFileInfo(self, name):
    if not os.path.isfile(name):
      raise NotFoundError
    return name

  def getFileInfoName(self, fileinfo):
    return fileinfo

  def readFileInfo(self, fileinfo):
    return open(fileinfo).read()
