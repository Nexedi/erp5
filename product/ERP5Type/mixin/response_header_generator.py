# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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
from itertools import chain
from AccessControl import ClassSecurityInfo
import ExtensionClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Globals import PersistentMapping
from zLOG import LOG, ERROR
from six.moves import xrange

def _makeForbiddenCharList(*args):
  result = [True] * 256
  for char in chain(*args):
    result[char] = False
  return tuple(result)
# https://tools.ietf.org/html/rfc7230#section-3.2
IS_FORBIDDEN_HEADER_NAME_CHAR_LIST = _makeForbiddenCharList(
  (ord(x) for x in "!#$%&'*+-.^_`|~"),
  xrange(0x30, 0x3a), # DIGIT
  xrange(0x61, 0x7b), # ALPHA, only lower-case
)
# Note: RFC defines field_value as not starting with SP nor HTAB,
# but this is because these are stripped during parsing. Allow
# them during generation.
IS_FORBIDDEN_HEADER_VALUE_CHAR_LIST = _makeForbiddenCharList(
  [0x09], # HTAB
  xrange(0x20, 0x7f), # SP + VCHAR
  xrange(0x80, 0x100), # obs-text
)
del _makeForbiddenCharList

class ResponseHeaderGenerator(ExtensionClass.Base):
    """
    Mix-in class allowing instances of its host class to define response
    headers of any request traversing it.

    For example, allows setting site-wide headers, and then overriding some
    when a WebSite document is traversed in the same request.

    Note that this happens on traversal (aka "document ID is in the URL"), and
    not on any other access.
    """
    security = ClassSecurityInfo() # We create a new security info object

    security.declareProtected(Permissions.ManagePortal, 'getResponseHeaderRuleDict')
    def getResponseHeaderRuleDict(self):
      """
      Return a mapping describing currently-defined response header rules.
      Modifying returned value does not have any effect on stored rules (use
      setResponseHeaderRule & deleteResponseHaderRule).

      Key (str)
        Header name.
        Valid character set (as per rfc7230):
          "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." /
          "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
          DIGIT being range: 0x30-0x39
          ALPHA being limited to range: 0x61-0x7A (lower-case only)
      Value (dict)
        "method_id" (string)
          Identifier of a callable accessible on self.
          If empty, fallback_value and fallback_value_replace will always be
          used.
          Parameters (passed by name):
            request (BaseRequest)         Current request object.
            header_name (str)             (see above)
            fallback_value (str)          (see below)
            fallback_value_replace (bool) (see below)
            current_value (str, None)
              The value of this header in current response.
              None if it is not set yet.
          Return value (tuple)
            [0]: Header value (str)       (see fallback_value below)
            [1]: Replace (bool)           (see fallback_value_replace below)
          Such callable should refrain from accessing the response directly.
        "fallback_value" (str)
          Header value to use if given method is unusable (raises or
          inaccessible).
          Valid characted set (as per rfc7230): HTAB, 0x20-0x7E, 0x80-0xFF
        "fallback_value_replace" (bool)
          When true, fallback_value replaces any pre-existing value.
          If fallback_value is empty, this removes the header from the response.
          When false, fallback_value is appended to any pre-existing value,
          separated with ", ".
          If fallback_value is empty, this response header is left unchanged.
      """
      return {
        header_name: {
          'method_id': method_id,
          'fallback_value': fallback_value,
          'fallback_value_replace': fallback_value_replace,
        }
        for (
          header_name, (method_id, fallback_value, fallback_value_replace)
        ) in six.iteritems(getattr(self, '_response_header_rule_dict', {}))
      }

    def _getResponseHeaderRuleDictForModification(self):
      """
      Retrieve persistent rule dict storage.
      Use only when a modification is requested, to avoid creating useless
      subobjects.
      """
      try:
        return self._response_header_rule_dict
      except AttributeError:
        self._response_header_rule_dict = rule_dict = PersistentMapping()
        return rule_dict

    security.declareProtected(Permissions.ManagePortal, 'setResponseHeaderRule')
    def setResponseHeaderRule(
      self,
      header_name,
      method_id,
      fallback_value,
      fallback_value_replace,
    ):
      """
      Create or modify a header rule.

      See getResponseHeaderRuleDict for a parameter description.
      header_name is lower-cased before validation and storage.
      """
      header_name = header_name.lower()
      if not header_name:
        raise ValueError('Header name must not be empty')
      for char in header_name:
        if IS_FORBIDDEN_HEADER_NAME_CHAR_LIST[ord(char)]:
          raise ValueError(
            '%r is not a valid header name character' % (char, ),
          )
      for char in fallback_value:
        if IS_FORBIDDEN_HEADER_VALUE_CHAR_LIST[ord(char)]:
          raise ValueError(
            '%r is not a valid header value character' % (char, ),
          )
      self._getResponseHeaderRuleDictForModification()[header_name] = (
        method_id,
        fallback_value,
        bool(fallback_value_replace),
      )

    security.declareProtected(Permissions.ManagePortal, 'deleteResponseHeaderRule')
    def deleteResponseHeaderRule(self, header_name):
      """
      Delete an existing header rule.
      """
      del self._getResponseHeaderRuleDictForModification()[header_name]

    def __before_publishing_traverse__(self, self2, request):
      try:
        response = request.RESPONSE
        setHeader = response.setHeader
        appendHeader = response.appendHeader
        removeHeader = response.headers.pop
      except AttributeError:
        # Response does not support setting headers, nothing to do.
        pass
      else:
        for (
          header_name, (method_id, value, value_replace)
        ) in six.iteritems(getattr(self, '_response_header_rule_dict', {})):
          if method_id:
            try:
              method_value = getattr(self, method_id)
            except AttributeError:
              LOG(
                __name__,
                ERROR,
                'Cannot access %r.%r to generate response header %r, using fallback value' % (
                  self,
                  method_id,
                  header_name,
                ),
              )
            else:
              fallback_value = value
              fallback_value_replace = value_replace
              try:
                value, value_replace = method_value(
                  request=request,
                  header_name=header_name,
                  fallback_value=value,
                  fallback_value_replace=value_replace,
                  current_value=response.getHeader(header_name),
                )
                for char in value:
                  if IS_FORBIDDEN_HEADER_VALUE_CHAR_LIST[ord(char)]:
                    value = fallback_value
                    value_replace = fallback_value_replace
                    raise ValueError(
                      '%r is not a valid header value character' % (char, ),
                    )
              except Exception:
                LOG(
                  __name__,
                  ERROR,
                  '%r.%r raised when generating response header %r, using fallback value' % (
                    self,
                    method_id,
                    header_name,
                  ),
                  error=True,
                )
          if value:
            (setHeader if value_replace else appendHeader)(header_name, value)
          elif value_replace:
            try:
              removeHeader(header_name)
            except KeyError:
              pass
          # else, no value and append: nothing to do.
      return super(
        ResponseHeaderGenerator,
        self,
      ).__before_publishing_traverse__(self2, request)

InitializeClass(ResponseHeaderGenerator)
