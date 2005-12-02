##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# ZPublisher should drop requests without a good http referer

from ZPublisher.BaseRequest import BaseRequest
import AccessControl

BaseRequest.erp5_old_traverse = BaseRequest.traverse

def erp5_new_traverse(request, path, response=None, validated_hook=None):

  if response is None: response=request.response
  object = BaseRequest.erp5_old_traverse(request, path, response=response, validated_hook=validated_hook)
  http_url = request.get('ACTUAL_URL', '').strip()
  http_referer = request.get('HTTP_REFERER', '').strip()

  security_manager = AccessControl.getSecurityManager()
  user = security_manager.getUser()
  user_roles = user.getRolesInContext(object)

  # Manager can do anything
  if 'Manager' in user_roles:
    return object

  # are we within a portal ?
  try:
    context = getattr(object, 'im_self', None)
    if context is not None:
      try:
        portal_object = context.getPortalObject()
      except AttributeError:
        portal_object = object.getPortalObject()
    else :
      portal_object = object.getPortalObject()
  except AttributeError:
    pass
  else:
    if not getattr(portal_object, 'require_referer', 0):
      return object
    portal_url = portal_object.absolute_url()
    if http_referer != '':
      # if HTTP_REFERER is set, user can acces the object if referer is ok
      if http_referer.startswith(portal_url):
        return object
      else:
        LOG('HTTP_REFERER_CHECK : BAD REFERER !', 0, 'request : "%s", referer : "%s"' % (http_url, referer))
        response.unauthorized()
    else:
      # no HTTP_REFERER, we only allow to reach portal_url
      for i in ('/', '/index_html', '/login_form', '/view'):
        if http_url.endswith(i):
          http_url = http_url[:-len(i)]
          break
      if len(http_url) == 0 or not portal_url.startswith(http_url):
        LOG('HTTP_REFERER_CHECK : NO REFERER !', 0, 'request : "%s"' % http_url)
        response.unauthorized()

  return object

BaseRequest.traverse = erp5_new_traverse
