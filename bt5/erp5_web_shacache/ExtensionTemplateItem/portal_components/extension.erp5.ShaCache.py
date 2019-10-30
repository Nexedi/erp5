# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 20011 Nexedi SA and Contributors. All Rights Reserved.
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


import hashlib, httplib
from Products.ERP5Type.UnrestrictedMethod import super_user
from Products.ERP5Type.Utils import IterableAsStreamIterator
from zExceptions import Success


def WebSection_getDocumentValue(self, key, portal=None, language=None,\
                                            validation_state=None, **kw):
  """
    API SHACACHE

     - GET /<key>
       The key is the sha512sum.

       Return raw content.
       Raise HTTP error (404) if key does not exist
  """
  if self.REQUEST.get('REQUEST_METHOD') in ('PUT',):
    return

  if portal is None:
    portal = self.getPortalObject()

  # Return the document, if the document exists.
  if validation_state is None:
    validation_state = ('released', 'released_alive', 'published',
                        'published_alive', 'shared', 'shared_alive',
                        'public', 'validated')

  kw['portal_type'] = portal.getPortalDocumentTypeList()
  kw['validation_state'] = validation_state
  kw['reference'] = key

  document_list = self.getDocumentValueList(limit=1, **kw)
  if len(document_list):
    return document_list[0]

  return None

def File_viewAsWeb(self):
  """
    Make possible to send the file data to the client without consume the
    RAM memory.
  """
  RESPONSE = self.REQUEST.RESPONSE
  RESPONSE.setHeader('Content-Type', self.getContentType())
  size = self.getSize()
  RESPONSE.setHeader('Content-Length', size)
  RESPONSE.setHeader('Cache-Control', 'public,max-age=31556926')
  RESPONSE.setHeader('Accept-Ranges', 'bytes')

  # Shortcut if the file is not a Pdata.
  data=self.data
  if isinstance(data, str):
    # Do this way instead of 'return data'
    # to bypass default caching policy manager.
    raise Success(data)

  # For Pdata type, we must iterate and send chunk by chunk.
  def generator():
    while data:
      # Send data to the client.
      yield data.data
      # Load next object without keeping previous chunks in memory.
      deactivate = data._p_deactivate
      data = data.next
      deactivate()
  return IterableAsStreamIterator(generator(), size)


def WebSite_viewAsWebPost(self, *args, **kwargs):
  portal = self.getPortalObject()
  sha512sum = hashlib.sha512()
  file = self.REQUEST._file
  while True:
    d = file.read(1<<20)
    if not d:
      break
    sha512sum.update(d)
  sha512sum = sha512sum.hexdigest()
  document = portal.portal_contributions.newContent(file=file,
    filename='shacache', discover_metadata=False, reference=sha512sum,
    content_type='application/octet-stream')
  with super_user():
    # security check should be done already.
    document.publish()

  self.REQUEST.RESPONSE.setStatus(httplib.CREATED)
  return sha512sum

