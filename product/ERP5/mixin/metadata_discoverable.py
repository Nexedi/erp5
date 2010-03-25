# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import md5
import string
import xmlrpclib, base64, re, zipfile, cStringIO
from xmlrpclib import Fault
from xmlrpclib import Transport
from xmlrpclib import SafeTransport
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from Products.ERP5Type.Base import WorkflowMethod
from zLOG import LOG
from Products.ERP5Type.Cache import CachingMethod

# Mixin import
from Products.ERP5.mixin.convertable import ConvertableMixin
from Products.ERP5.mixin.html_convertable import HTMLConvertableMixin




class MetadataDiscoverableMixin(HTMLConvertableMixin):
  """
  This class provides a generic implementation of IMetadataDiscoverable.

  """

  # Declarative security
  security = ClassSecurityInfo()


  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  


  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the content information from the HTML conversion.
    The default implementation tries to build a dictionnary
    from the HTML conversion of the document and extract
    the document title.
    """
    result = {}
    html = self.asEntireHTML()
    if not html: return result
    title_list = re.findall(self.title_parser, str(html))
    if title_list:
      result['title'] = title_list[0]
    return result

  