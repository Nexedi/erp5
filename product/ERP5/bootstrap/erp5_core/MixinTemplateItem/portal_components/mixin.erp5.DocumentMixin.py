# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

LOCK_PERMISSION_KEY = 'TRANSACTIONAL_VARIABLE_FORMAT_PERMISSION_LOCK_FLAG'

class DocumentMixin:
  """
  Implementation of IDocument interface
   convert must not be overloaded as it checks conversion
   format permission

   isSupportBaseDataConversion can be overriden, if base_conversion
   is supported (eg. OOoDocuments, TextDocument).


  """
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'convert')
  def convert(self, format, **kw): # pylint: disable=redefined-builtin
    """
      Main content conversion function, returns result which should
      be returned and stored in cache.

      If format is not allowed for download, Unauthorized exception is raised.

      format - the format specied in the form of an extension
      string (ex. jpeg, html, text, txt, etc.)
      **kw can be various things - e.g. resolution
    """
    transaction_variable = getTransactionalVariable()
    if LOCK_PERMISSION_KEY in transaction_variable:
      # in convert we want always to check conversion format permission
      # to bypass such check one should use _convert directly
      del transaction_variable[LOCK_PERMISSION_KEY]
    self._checkConversionFormatPermission(format, lock_checking=True, **kw)

    pre_converted_only = kw.pop('pre_converted_only', False)
    if pre_converted_only:
      # we will use ONLY cache to return converted content
      # if respective document is not in cache we will return a good default content
      try:
        kw['format'] = format
        result = self.getConversion(**kw)
      except KeyError:
        # respective document is not cached yet and we should return a failure safe content instead
        result = self.getFailsafeConversion(**kw)
    else:
      # generate conversion on the fly or get it from cache (if already stored)
      result = self._convert(format, **kw)
    if LOCK_PERMISSION_KEY in transaction_variable:
      del transaction_variable[LOCK_PERMISSION_KEY]
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getFailsafeConversion')
  def getFailsafeConversion(self, **kw):
    """
      Return a failure resistent conversion of a document
    """
    method = self._getTypeBasedMethod('getFailsafeConversion',
                   fallback_script_id='Document_getFailsafeConversion')
    return method(**kw)

  def _convert(self, format, **kw): # pylint: disable=redefined-builtin
    """Private method which make the transformation.
    Must be overriden !!!
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                                             'checkConversionFormatPermission')
  def checkConversionFormatPermission(self, format, **kw): # pylint: disable=redefined-builtin
    """Public version of _checkConversionFormatPermission
    Without raising return just True or False.
    """
    try:
      self._checkConversionFormatPermission(format, **kw)
    except Unauthorized:
      return False
    else:
      return True

  def _checkConversionFormatPermission(self, format, lock_checking=False, **kw): # pylint: disable=redefined-builtin
    """Private method to check permission when access specified format.
    This method raises
    """
    transaction_variable = getTransactionalVariable()
    if transaction_variable.get(LOCK_PERMISSION_KEY, False):
      # Permission already checked in convert with final format,
      # do not check permission for intermediate formats
      return True
    # XXX cache result in TV
    method = self._getTypeBasedMethod('checkConversionFormatPermission',
                 fallback_script_id='Document_checkConversionFormatPermission')
    if '**' not in method.params():
      # Backward compatibility code:
      # Existing Type Based Method doesn't support new **kw argument
      # in their signature.
      is_allowed = method(format=format)
    else:
      is_allowed = method(format=format, **kw)
    if not is_allowed:
      raise Unauthorized('Document: user does not have enough permission'\
                         ' to access document in %s format' %\
                                                        (format or 'original'))
    transaction_variable[LOCK_PERMISSION_KEY] = lock_checking

  security.declareProtected(Permissions.AccessContentsInformation,
                                                 'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
    """Tell if document implement IBaseConvertable Interface.
    By default it doens't
    """
    return False

InitializeClass(DocumentMixin)
