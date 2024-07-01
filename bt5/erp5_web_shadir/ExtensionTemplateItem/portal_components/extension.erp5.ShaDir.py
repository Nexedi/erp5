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

import six
import hashlib
from base64 import b64decode
from binascii import a2b_hex
from collections import defaultdict
from json import dumps, loads
from zExceptions import BadRequest
from DateTime import DateTime
from Products.ERP5Type.UnrestrictedMethod import super_user
from Products.ERP5Type.Utils import unicode2str, str2bytes


def WebSection_getDocumentValue(self, key, portal=None, language=None,\
                                            validation_state=None, **kw):
  """
    API SHADIR

     - POST /<key>
        + parameters required:
           * sha512: the hash (sha512) of the file content

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
    document_list = [loads(document.getData())
                       for document in portal.portal_catalog(
                         follow_up_uid=data_set.getUid(),
                         validation_state='published')]

    temp_file = self.newContent(temp_object=True, portal_type='File', id='%s.txt' % key)
    temp_file.setData(str2bytes(dumps(document_list)))
    temp_file.setContentType('application/json')
    return temp_file.getObject()
  return None

def WebSection_setObject(self, id, ob, **kw):
  """
    Make any change related to the file uploaded.
  """
  portal = self.getPortalObject()
  ob = ob.getOriginalDocument()
  data = self.REQUEST.get('BODY')

  try:
    metadata, signature = loads(data)
    metadata = loads(metadata)
    # a few basic checks
    b64decode(str2bytes(signature))
    if len(a2b_hex(metadata['sha512'])) != 64:
      raise Exception('sha512: invalid length')
  except Exception as e:
    raise BadRequest(str(e))

  expiration_date = metadata.get('expiration_date')

  data_set = portal.portal_catalog.getResultValue(portal_type='Data Set',
                                                  reference=id)
  if data_set is None:
    data_set = portal.data_set_module.newContent(portal_type='Data Set',
                                                 reference=id)
    with super_user():
      # security check should be done already.
      data_set.publish()


  reference = hashlib.sha512(data).hexdigest()
  ob.setFollowUp(data_set.getRelativeUrl())
  ob.setContentType('application/json')
  ob.setReference(reference)
  if expiration_date is not None:
    ob.setExpirationDate(expiration_date)
  with super_user():
    # security check should be done already.
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

  # return a document for which getId() returns the name for _setObject to be
  # called with id=name ( for WebSection_setObject ), but for which
  # getRelativeUrl returns the relative url of the real document, for
  # VirtualFolderMixin transactional variable cache between _setObject and
  # _getOb
  return document.asContext(getId=lambda: name)

# The following scripts are helpers to search & clean up shadir entries.
# XXX: Due to lack of View skin for shadir, external methods are currently
#      created manually in custom skin after installation, if needed.

def _delete(portal, data_set_id_list, document_id_list):
  r = "%s\n%s %r\n%s %r" % (DateTime(),
    len(data_set_id_list), data_set_id_list,
    len(document_id_list), document_id_list)
  if document_id_list:
    portal.document_module.manage_delObjects(document_id_list)
  if data_set_id_list:
    portal.data_set_module.manage_delObjects(data_set_id_list)
  return r

def _deletableDataSetList(data_set_dict):
  return [data_set.getId()
    for data_set, document_set in data_set_dict.iteritems()
    if document_set.issuperset(data_set.getFollowUpRelatedList())]

def ERP5Site_deleteOrphanShadir(self):
  assert self.getPortalType() == "ERP5 Site", self
  data_set_dict = defaultdict(set)
  document_id_list = []
  query = self.erp5_sql_connection().query
  for relative_url, in query("select catalog.relative_url"
      " from catalog join shadir using (uid)"
        " left join catalog as t on (lower(hex(sha512))=t.reference)"
      " where t.uid is null", 0)[1]:
    document = self.unrestrictedTraverse(relative_url)
    data_set = document.getFollowUpValue(portal_type='Data Set')
    if data_set is not None:
      data_set_dict[data_set].add(relative_url)
    document_id_list.append(document.getId())

  data_set_id_list = _deletableDataSetList(data_set_dict)

  x = zip(*query("select catalog.id from catalog"
      " join category on (base_category_uid=%s and category_uid=catalog.uid)"
      " left join catalog as t on (catalog.uid=t.uid)"
    " where catalog.parent_uid=%s and t.uid is null" % (
      self.portal_categories.follow_up.getUid(),
      self.data_set_module.getUid(),
    ), 0)[1])
  if x:
    data_set_id_list += x[0]

  return _delete(self, data_set_id_list, document_id_list)

def _deleteDocumentList(portal, document_list):
  data_set_dict = defaultdict(set)
  document_id_list = []
  sha512_set = set()
  for document in document_list:
    sha512_set.add(loads(loads(document.getData())[0])[u"sha512"])
    data_set = document.getFollowUpValue(portal_type='Data Set')
    if data_set is not None:
      data_set_dict[data_set].add(document.getRelativeUrl())
    document_id_list.append(document.getId())
  sha512_set.difference_update(sha512
    for relative_url, sha512 in portal.erp5_sql_connection().query(
      "select relative_url, lower(hex(sha512))"
      " from catalog join shadir using (uid) where sha512 in (%s)"
      % ','.join(map("x'%s'".__mod__, sha512_set)), 0)[1]
    if not (relative_url.startswith("document_module/") and
            relative_url[16:] in document_id_list))
  if sha512_set:
    for document in portal.document_module.searchFolder(reference=sha512_set):
      document_id_list.append(document.getId())
  return _delete(portal, _deletableDataSetList(data_set_dict), document_id_list)

def ShaDir_delete(self):
  portal_type = self.getPortalType()
  if portal_type == 'Data Set':
    document_list = self.getFollowUpRelatedValueList(portal_type='File')
  else:
    assert portal_type == 'File', self
    document_list = self,
  return _deleteDocumentList(self.getPortalObject(), document_list)

def ShaDir_search(self, filename, summary, delete=False):
  assert self.getPortalType() == "ERP5 Site", self
  document_list = []
  x = defaultdict(list)
  for document in self.portal_catalog.unrestrictedSearchResults(
      filename=filename, summary=summary):
    document = document.getObject()
    document_list.append(document)
    metadata = loads(loads(document.getData())[0])
    del metadata[u"sha512"]
    x[';'.join('%s=%r' % (k, unicode2str(v))
               for k, v in sorted(metadata.iteritems()))].append(
      document.getId())
  r = '\n'.join('%s %s' % (k, sorted(v)) for k, v in sorted(six.iteritems(x)))
  if delete:
    r += '\n' + _deleteDocumentList(self, document_list)
  return r
