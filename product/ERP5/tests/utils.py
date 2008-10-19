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

import os.path
from Products.ERP5Type import tarfile
import xml.parsers.expat
import xml.dom.minidom
from urllib import url2pathname


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
    class Handler:
      cur_key = None
      old_tag = None
      cur_tag = None
      key_val = None
      value_val = None

      def __init__(self):
        self.data = {}

      def start(self, name, attrs):
        if not name in ('item', 'key', 'value', 'string', 'int', 'float'):
          return
        self.old_tag = self.cur_tag
        self.cur_tag = name
        if name=='key':
          self.cur_key = name

      def end(self, name):
        self.cur_tag = None
        if name=='item':
          self.data[self.key_val] = self.value_val
          self.cur_key = None
          self.key_val = None
          self.value_val = None

      def char(self, data):
        if self.cur_tag in ('string', 'int', 'float'):
          f = getattr(self, 'to%s' % self.cur_tag)
          if self.old_tag=='key':
            self.key_val = f(data)
          elif self.old_tag=='value':
            self.value_val = f(data)

      def tostring(self, value):
        return str(value)

      def toint(self, value):
        return int(value)

      def tofloat(self, value):
        return float(value)

    def parse(source):
      handler = Handler()
      p = xml.parsers.expat.ParserCreate()
      p.StartElementHandler = handler.start
      p.EndElementHandler = handler.end
      p.CharacterDataHandler = handler.char
      p.Parse(source)
      return handler.data

    name = '%s/ActionTemplateItem/portal_types/' % self.getPrefix()
    for i in self.findFileInfosByName(startswith=name, endswith='.xml'):
      portal_type = url2pathname(self.getFileInfoName(i).split('/')[-2])
      if not portal_type in self.actions:
        self.actions[portal_type] = []
      data = parse(self.readFileInfo(i))
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
    def visit(arg, dirname, names):
      if '.svn' in dirname:
        return
      for i in names:
        path = os.path.join(self.target, dirname, i)
        if os.path.isfile(path):
          allfiles.append(path)
    os.path.walk(self.target, visit, None)
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
    return file(fileinfo).read()
