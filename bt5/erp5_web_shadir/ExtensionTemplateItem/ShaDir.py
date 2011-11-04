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
import json
import validictory
from Products.ERP5Type.Document import newTempFile


def WebSection_getDocumentValue(self, key, portal=None, language=None,\
                                            validation_state=None, **kw):
  """
    API SHADIR

     - POST /<key>
        + parameters required:
           * file: the name of the file
           * urlmd5: mdsum of orginal url
           * sha512: the hash (sha512) of the file content

        + parameters not required:
           * valid-until: the date which the file must be expired
           * architecture: computer architecture

       Used to add information on shadir server.


     - GET /<key>
       Return list of information for a given key
       Raise HTTP error (404) if key does not exist
  """
  if self.REQUEST.get('REQUEST_METHOD') in ('PUT',):
    return

  if portal is None:
    portal = self.getPortalObject()

  data_set = portal.portal_catalog.getResultValue(portal_type='Data Set',
                                                  reference=key)

  # Return the SIGNATURE file, if the document exists.
  if data_set is not None:
    document_list = [json.loads(document.getData()) \
                       for document in portal.portal_catalog(
                         follow_up_uid=data_set.getUid(),
                         validation_state='published')]

    temp_file = newTempFile(self, '%s.txt' % key)
    temp_file.setData(json.dumps(document_list))
    temp_file.setContentType('application/json')
    return temp_file.getObject()

  return None

def WebSection_setObject(self, id, ob, **kw):
  """
    Make any change related to the file uploaded.
  """
  portal = self.getPortalObject()
  data = self.REQUEST.get('BODY')
  schema = self.WebSite_getJSONSchema()
  structure = json.loads(data)
  # 0 elementh in structure is json in json
  # 1 elementh is just signature
  structure = [json.loads(structure[0]), structure[1]]

  validictory.validate(structure, schema)

  file_name = structure[0].get('file', None)
  expiration_date = structure[0].get('expiration_date', None)

  data_set = portal.portal_catalog.getResultValue(portal_type='Data Set',
                                                  reference=id)
  if data_set is None:
    data_set = portal.data_set_module.newContent(portal_type='Data Set',
                                                 reference=id)
    data_set.publish()


  reference = hashlib.sha512(data).hexdigest()
  ob.setFilename(file_name)
  ob.setFollowUp(data_set.getRelativeUrl())
  ob.setContentType('application/json')
  ob.setReference(reference)
  if expiration_date is not None:
    ob.setExpirationDate(expiration_date)
  ob.publish()
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
  if name is None:
    name = 'shacache'
  document = portal.portal_contributions.newContent(data=body,
                                                    filename=name,
                                                    discover_metadata=False)
  return document

