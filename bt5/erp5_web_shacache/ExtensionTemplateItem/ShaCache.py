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


import hashlib


def WebSection_getDocumentValue(self, key, portal=None, language=None,\
                                            validation_state=None, **kw):
  """
    API SHACACHE

     - GET /<key>
       The key is the sha512sum.

       Return raw content.
       Raise HTTP error (404) if key does not exist
  """
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


def WebSection_setObject(self, id, ob, **kw):
  """
    Add any change of the file uploaded.
  """

  sha512sum = hashlib.sha512()
  self.REQUEST._file.seek(0)
  while True:
    d = self.REQUEST._file.read(sha512sum.block_size)
    if not d:
      break
    sha512sum.update(d)

  reference = sha512sum.hexdigest()
  if reference != id:
    raise ValueError('The content does not match with sha512sum provided.')

  # Set object properties
  ob.setContentType('application/octet-stream')
  ob.setFilename(id)
  ob.setReference(reference)
  return ob

def WebSection_putFactory(self, name, typ, body):
  """
   API SHACACHE
     - PUT /<key>
        + parameters required:
          * data:  it is the file content
       The key is the file name.
  """
  portal = self.getPortalObject()
  group = ('networkcache',)
  new_id = str(portal.portal_ids.generateNewId(id_group=group))
  registry = portal.portal_contribution_registry
  portal_type = registry.findPortalTypeName(filename=name,
                                            content_type=typ)
  if portal_type is None:
    return None

  # The code bellow is inspired from ERP5Type.Core.Folder.newContent
  pt = self._getTypesTool()
  myType = pt.getTypeInfo(self)
  if myType is not None and not myType.allowType( portal_type ) and \
     'portal_contributions' not in self.getPhysicalPath():
    raise ValueError('Disallowed subobject type: %s' % portal_type)
  container = portal.getDefaultModule(portal_type)
  pt.constructContent(type_name=portal_type,
                      container=container,
                      id=new_id)

  document = container._getOb(new_id)

  # We can only change the state of the object after all the activities and
  # interaction workflow, to avoid any security problem.
  document.activate(after_path_and_method_id=(document.getPath(), \
            ('convertToBaseFormat', 'Document_tryToConvertToBaseFormat', \
             'immediateReindexObject', 'recursiveImmediateReindexObject')))\
            .WebSite_publishDocumentByActivity()

  return document
