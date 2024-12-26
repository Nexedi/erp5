# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.Domain import Domain
from erp5.component.mixin.DocumentExtensibleTraversableMixin import DocumentExtensibleTraversableMixin
from ZPublisher import BeforeTraverse

from Products.ERP5Type.Cache import getReadOnlyTransactionCache

class DiscussionForum(Domain, DocumentExtensibleTraversableMixin):
  """
      A Discussion Forum is TODO.

      DiscussionForum uses the following scripts for customisation:

      - getDocumentValueList

      - getDefaultDocumentValue

      - getDiscussionForumValue

  """
  # CMF Type Definition
  meta_type = 'Discussion Forum'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.SortIndex
                    , PropertySheet.Predicate
                    )

  security.declarePrivate( 'manage_beforeDelete' )
  def manage_beforeDelete(self, item, container):
    self.log("----------before delete-------------")
    if item is self:
      handle = self.meta_type + '/' + self.getId()
      BeforeTraverse.unregisterBeforeTraverse(item, handle)
    super(DiscussionForum, self).manage_beforeDelete(item, container)

  security.declarePrivate( 'manage_afterAdd' )
  def manage_afterAdd(self, item, container):
    self.log("----------after add-------------")
    if item is self:
      handle = self.meta_type + '/' + self.getId()
      BeforeTraverse.registerBeforeTraverse(item, self._getTraversalHookClass()(), handle)
    super(DiscussionForum, self).manage_afterAdd(item, container)

  security.declarePrivate( 'manage_afterClone' )
  def manage_afterClone(self, item):
    self.log("----------after clone-------------")
    self._cleanupBeforeTraverseHooks()
    super(DiscussionForum, self).manage_afterClone(item)

  def _cleanupBeforeTraverseHooks(self):
    # unregister all before traversal hooks that do not belong to us.
    my_handle = self.meta_type + '/' + self.getId()
    handle_to_unregister_list = []
    for (_, handle), hook in self.__before_traverse__.items():
      if isinstance(hook, self._getTraversalHookClass()) and handle != my_handle:
        handle_to_unregister_list.append(handle)
    for handle in handle_to_unregister_list:
      BeforeTraverse.unregisterBeforeTraverse(self, handle)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDiscussionForumValue')
  def getDiscussionForumValue(self):
    """
        Returns the current web section (ie. self) though containment acquisition.

        To understand the misteries of acquisition and how the rule
        containment vs. acquisition works, please look at
        XXXX (Zope web site)
    """
    self.log("----------get df value-------------")
    return self

  '''
  # Default view display
  security.declareProtected(Permissions.View, '__call__')
  def __call__(self):
    """
        If a Web Section has a default document, we render
        the default document instead of rendering the Web Section
        itself.

        The implementation is based on the presence of specific
        variables in the REQUEST (besides editable_mode and
        ignore_layout).

        current_web_section -- defines the Web Section which is
        used to display the current document.

        current_web_document -- defines the Document (ex. Web Page)
        which is being displayed within current_web_section.

        is_web_section_default_document -- a boolean which is
        set each time we display a default document as a section.

        We use REQUEST parameters so that they are reset for every
        Web transaction and can be accessed from widgets.
    """
    # Register current web site physical path for later URL generation
    if self.REQUEST.get(self.web_section_key, MARKER) is MARKER:
      self.REQUEST[self.web_section_key] = self.getPhysicalPath()
    self.REQUEST.set('current_web_section', self)
    if self._checkIfRenderDefaultDocument():
      document = None
      if self.isDefaultPageDisplayed():
        # The following could be moved to a typed based method for more flexibility
        document = self.getDefaultDocumentValue()
        if document is None:
          # no document found for current user, still such document may exists
          # in some cases user (like Anonymous) can not view document according to portal catalog
          # but we may ask him to login if such a document exists
          isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
          if isAuthorizationForced is not None and isAuthorizationForced():
            if unrestricted_apply(self.getDefaultDocumentValue) is not None:
              # force user to login as specified in Web Section
              raise Unauthorized
        if document is not None and document.getReference() is not None:
          # we use web_site_module/site_id/section_id/page_reference
          # as the url of the default document.
          self.REQUEST.set('current_web_document', document)
          self.REQUEST.set('is_web_section_default_document', 1)
          document = aq_base(document.asContext(
              id=document.getReference(),
              original_container=document.getParentValue(),
              original_id=document.getId(),
              editable_absolute_url=document.absolute_url())).__of__(self)
      else:
        isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
        if isAuthorizationForced is not None and isAuthorizationForced():
          if self.getPortalObject().portal_membership.isAnonymousUser():
            # force anonymous to login
            raise Unauthorized
      # Try to use a custom renderer if any
      custom_render_method_id = self.getCustomRenderMethodId()
      if custom_render_method_id is not None:
        if document is None:
          document = self
        view = _ViewEmulator().__of__(self)
        # call caching policy manager.
        _setCacheHeaders(view, {})
        # If we have a conditional get, set status 304 and return
        # no content
        if _checkConditionalGET(view, extra_context={}):
          return ''
        result = getattr(document, custom_render_method_id)()
        return result
      elif document is not None:
        return document()
    return Domain.__call__(self)
  '''

  # WebSection API
  security.declareProtected(Permissions.View, 'getDefaultDocumentValue')
  def getDefaultDocumentValue(self):
    """
        Return the default document of the current
        forum.

        This method must be implemented through a
        portal type dependent script:
          DiscussionForum_getDefaultDocumentValue
    """
    self.log("----------getdocvalue-------------")
    cache = getReadOnlyTransactionCache()
    if cache is not None:
      key = ('getDefaultDocumentValue', self)
      try:
        return cache[key]
      except KeyError:
        pass

    result = self._getTypeBasedMethod('getDefaultDocumentValue',
                   fallback_script_id='DiscussionForum_getDefaultDocumentValue')()

    if cache is not None:
      cache[key] = result

    if result is not None:
      result = result.__of__(self)

    return result

  security.declareProtected(Permissions.View, 'getDocumentValueList')
  def getDocumentValueList(self, **kw):
    self.log("----------get doc value list-------------")
    """
        Return the list of documents which belong to the
        current forum. The API is designed to
        support additional parameters so that it is possible
        to group documents by reference, version, language, etc.
        or to implement filtering of documents.

        This method must be implemented through a
        portal type dependent script:
          DiscussionForum_getDocumentValueList
     """
    cache = getReadOnlyTransactionCache()
    if cache is not None:
      key = ('getDocumentValueList', self) + tuple(kw.items())
      try:
        return cache[key]
      except KeyError:
        pass

    result = self._getTypeBasedMethod('getDocumentValueList',
                     fallback_script_id='DiscussionForum_getDocumentValueList')(**kw)

    if cache is not None:
      cache[key] = result

    if result is not None and not kw.get('src__', 0):
      result = [doc.__of__(self) for doc in result]

    return result
