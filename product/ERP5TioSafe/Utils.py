# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from zLOG import LOG, ERROR

class EchoDictTarget:
  """
  This is an echo class used by lxml to parse xml data

  See http://codespeak.net/lxml/parsing.html#the-target-parser-interface

  This class takes a dict as init parameter defining how to parse the xml.
  
  Dict must looks like :
  { xml_tag : (wanted_dict_key, is_root_element),...}

  The result of the parsing will thus return a list of dictionnaries. Each time it finds an xml_tag which is a root element will create a new dict.

  This allow to transform an xml string into a property dict wich can be used to easily create a new erp5 object

  Parsing must be called this way :
  parser = etree.XMLParser(target = EchoDictTarget(parser_dict))
  result_list = etree.XML(str(xml), parser,)

  """


  def __init__(self, parser_dict):
    self.parser_dict = parser_dict
    self.result_list = []
    self._current_object = None
    self._current_key = None

  def start(self, tag, attrib):
    try:
      value, root = self.parser_dict[tag]
      if root:
        self._current_object = {}
      if self._current_object is not None and \
             not self._current_object.has_key(value):
        self._current_object[value] = ""
        self._current_key = value
      else:
        self._current_key = None
    except KeyError:
      self._current_key = None
    except TypeError:
      LOG("EchoTargetDict.start", ERROR,
          "got a key for %s, but no root tag exists ! Check your property mapping definition" %(tag,))
      self._current_key = None
      
  def end(self, tag):
    try:
      value , root = self.parser_dict[tag]
      if root:
        self.result_list.append(self._current_object.copy())
    except KeyError:
      pass

  def data(self, data):
    if self._current_key and len(data.strip()):
      # for the element browsed several time
      if self._current_object.has_key(self._current_key):
        data = self._current_object[self._current_key] + data
      self._current_object[self._current_key] = data

  def comment(self, text):
    pass

  def close(self):
    return self.result_list


  
