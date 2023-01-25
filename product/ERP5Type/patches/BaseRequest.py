# -*- coding: utf-8 -*-

from functools import partial
from ZPublisher.BaseRequest import BaseRequest

def setCacheControlPrivateForAuthenticatedUser(request, user, validated_hook_):
  # If we are publishing a resource for an authenticated user, forbid shared
  # caches from storing it.
  # Historially, this was (for some reason) implemented in CookieCrumbler,
  # but it does not seem very consistent as it then depends on how the user
  # was authenticated. This is a more neutral location.
  if user.getUserName() != 'Anonymous User':
    request.response.setHeader('Cache-Control', 'private')
  if validated_hook_ is not None:
    return validated_hook_(request, user)

orig_BaseRequest_traverse = BaseRequest.traverse
def BaseRequest_traverse(self, path, response=None, validated_hook=None):
  return orig_BaseRequest_traverse(
    self,
    path=path,
    response=response,
    validated_hook=partial(
      setCacheControlPrivateForAuthenticatedUser,
      validated_hook_=validated_hook,
    ),
  )
BaseRequest.traverse = BaseRequest_traverse
