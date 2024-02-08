##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from zodbpickle.pickle import PicklingError
from Acquisition import aq_base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as \
  PropertyConstantGetter


class TemporaryDocumentMixin(object):
  """
  Setters and attributes that are attached to temporary documents.
  """
  isIndexable = PropertyConstantGetter('isIndexable', value=False)
  isTempDocument = PropertyConstantGetter('isTempDocument', value=True)
  __roles__ = None

  def __getstate__(self):
    if getattr(self, '_p_jar', None) is not None:
      # disallow persistent storage
      raise PicklingError("Temporary objects can't be pickled")
    return super(TemporaryDocumentMixin, self).__getstate__()

  def reindexObject(self, *args, **kw):
    pass

  def recursiveReindexObject(self, *args, **kw):
    pass

  def activate(self, *args, **kw):
    return self

  def setUid(self, value):
    self.uid = value # Required for Listbox so that no casting happens when we use TempBase to create new objects

  _setUid = setUid

  def getUid(self):
    try:
      return getattr(aq_base(self), 'uid')
    except AttributeError:
      value = self.getId()
      self.setUid(value)
      return value

  def setTitle(self, value):
    """
    Required so that getProperty('title') will work on tempBase objects
    The dynamic acquisition work very well for a lot of properties, but
    not for title. For example, if we do setProperty('organisation_url'), then
    even if organisation_url is not in a propertySheet, the method getOrganisationUrl
    will be generated. But this does not work for title, because I(seb)'m almost sure
    there is somewhere a method '_setTitle' or 'setTitle' with no method getTitle on Base.
    That why setProperty('title') and getProperty('title') does not work.
    """
    self.title = value

  def getTitle(self):
    """Returns the title of this document
    """
    return getattr(aq_base(self), 'title', None)

  def edit(self, *args, **kw):
    if getattr(self, "_original", None) is None:
      return super(TemporaryDocumentMixin, self).edit(*args, **kw)
    # Object created with Base.asContext, so do not touch borrowed
    # workflow history, in particular if it is persistent.
    # This also avoids security issues.
    return self._edit(restricted=1, *args, **kw)

# Make some methods public.
for method_id in ('reindexObject', 'recursiveReindexObject',
                  'activate', 'setUid', 'setTitle', 'getTitle',
                  'edit', 'setProperty', 'getUid', 'setCriterion',
                  'setCriterionPropertyList'):
  setattr(TemporaryDocumentMixin, '%s__roles__' % method_id, None)
