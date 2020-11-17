# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions


class TextContentHistoryMixin:
  """Mixin that provides access to history of edit of the text content property.

  To be used with erp5_code_mirror
  """
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'getTextContentHistoryRevisionDictList')
  def getTextContentHistoryRevisionDictList(self, limit=100):
    """Returns the history of edition as a list of dictionnaries.
    """
    history_dict_list = self._p_jar.db().history(self._p_oid, size=limit)
    if history_dict_list is None:
      # Storage doesn't support history
      return ()

    from struct import unpack
    from OFS.History import historicalRevision

    previous_text_content = None
    result = []
    for history_dict in history_dict_list:
      text_content = historicalRevision(self, history_dict['tid'])._baseGetTextContent()
      if text_content and text_content != previous_text_content:
        history_dict['time'] = history_dict['time']
        history_dict['user_name'] = history_dict['user_name'].strip()
        history_dict['key'] = '.'.join(map(str, unpack(">HHHH", history_dict['tid'])))
        del history_dict['tid']
        del history_dict['size']

        result.append(history_dict)
        previous_text_content = text_content

    return result

  security.declareProtected(Permissions.ModifyPortalContent,
                            'getTextContentHistory')
  def getTextContentHistory(self, key):
    """Returns the text content of a previous version of the document.
    """
    from struct import pack
    from OFS.History import historicalRevision

    serial = pack(*('>HHHH',) + tuple(map(int, key.split('.'))))
    rev = historicalRevision(self, serial)

    return rev._baseGetTextContent()

InitializeClass(TextContentHistoryMixin)
