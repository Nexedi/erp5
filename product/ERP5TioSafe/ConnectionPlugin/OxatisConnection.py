##############################################################################
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

from RESTConnection import RESTConnection
from RESTConnection import MethodWrapper
from Products.ERP5Type.Tool.WebServiceTool import ConnectionError
from lxml import etree
from zLOG import LOG, PROBLEM
from AccessControl import Unauthorized

RECORD_NOT_FOUND = "1001"
INVALID_DATA = "1002"
NO_ERROR = "200"
WARNINGS = "300"
ERRORS = "500"
UNAUTHORIZED = "503"

class OxatisHeaderTarget:
  """ This class is used to check if there is any
  error code returned into the xml from Oxatis
  """

  def __init__(self):
    self.error_code = NO_ERROR
    self.error_message = ''
    self.sub_error_code = NO_ERROR
    self.in_error_header = False

  def start(self, tag, attrib):
    if tag in ("DataResultService", "ResultService"):
      self.in_error_header = True
    if self.in_error_header:
      self.current_tag = tag
    else:
      self.current_tag = None

  def end(self, tag):
    if tag in ("DataResultService", "ResultService"):
      self.in_error_header = False
    self.current_tag = None

  def data(self, data):
    if self.in_error_header and self.current_tag:
      if self.current_tag == "StatusCode":
        self.error_code = data
      elif self.current_tag == "ErrorDetails":
        self.error_message = data
      elif self.current_tag == "StatusSubCode":
        self.sub_error_code = data

  def comment(self, text):
    pass

  def close(self):
    return (self.error_code, self.error_message, self.sub_error_code)


class OxatisMethodWrapper(MethodWrapper):

  def __call__(self, *args, **kw):
    url, xml = MethodWrapper.__call__(self, *args, **kw)
    # Parse data to check if there any error code
    parser = etree.XMLParser(target = OxatisHeaderTarget())
    error_code, error_message, sub_error_code = etree.XML(xml, parser,)
    if error_code == NO_ERROR:
      return url, xml
    elif error_code == WARNINGS:
      LOG("OxatisConnection.__call__ encounter a warning", PROBLEM, "error message is %s" %(error_message))
      return url, xml
    elif error_code == UNAUTHORIZED:
      raise Unauthorized(url)
    elif error_code == ERRORS:
      # Check if there is subcode
      if sub_error_code == RECORD_NOT_FOUND:
        raise KeyError
      elif sub_error_code == INVALID_DATA:
        raise TypeError, "Invalid data sent to WebService, url = %s, args =%s, kw = %s" %(url, args, kw)
      else:
        raise ValueError(error_message)
    else:
      raise ConnectionError("Invalid error code %s" %(error_code))


class OxatisConnection(RESTConnection):

  def __getattr__(self, name):
    if not name.startswith("_"):
      return OxatisMethodWrapper(name, self)
