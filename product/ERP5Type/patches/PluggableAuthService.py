##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors
# Copyright (c) 2013 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from hashlib import md5
from Products.PluggableAuthService.PluggableAuthService \
  import PluggableAuthService, _noroles, nobody
from Products.ERP5Type.Cache import caching_instance_method

if 1:
    assert md5(PluggableAuthService.validate.func_code.co_code).hexdigest() in (
      # PluggableAuthService 1.9.0
      '5e2e6adabd03124bfd21278d3b6fb1c7', # Python 2.6
      '5ef8421949366195dbb2d15d979a14c9', # Python 2.7
      )

    # When no user is found, try to create anonymous user even if we're not the
    # top user folder, so that anonymous user can be customized in appropriate
    # context (in particular: assign anonymous user to groups).
    # Because it's common to define admin users at root, original behaviour
    # is kept if any basic auth string is passed.
    def validate( self, request, auth='', roles=_noroles ):

        """ See IUserFolder.
        """
        plugins = self._getOb( 'plugins' )
        is_top = self._isTop()

        if not is_top and self._isNotCompetent( request, plugins ):
            # this user folder should not try to authenticate this request
            return None

        user_ids = self._extractUserIds(request, plugins)
        ( accessed
        , container
        , name
        , value
        ) = self._getObjectContext( request[ 'PUBLISHED' ], request )

        for user_id, login in user_ids:

            user = self._findUser(plugins, user_id, login, request=request)

            if aq_base( user ) is emergency_user:

                if is_top:
                    return user
                else:
                    return None

            if self._authorizeUser( user
                                  , accessed
                                  , container
                                  , name
                                  , value
                                  , roles
                                  ):
                return user

        if auth and not is_top: # patch 1
            return None

        #
        #   No other user folder above us can satisfy, and we have no user;
        #   return a constructed anonymous only if anonymous is authorized.
        #
        anonymous = self._createAnonymousUser( plugins )
        if self._authorizeUser( anonymous
                              , accessed
                              , container
                              , name
                              , value
                              , roles
                              ):
            return anonymous

        return None

    PluggableAuthService.validate.im_func.func_code = validate.func_code

    @caching_instance_method('createAnonymousUser',
                             cache_factory='erp5_content_short')
    def createAnonymousUser(self):
        try:
            role_list, group_list = self.ERP5Site_getAnonymousUserSecurity()
            if role_list or group_list:
                from Products.ERP5Security.ERP5UserFactory import ERP5User
                user = ERP5User(nobody.getId(), nobody.getUserName())
                user._addRoles(nobody.getRoles())
                user._addRoles(role_list)
                user._addGroups(group_list)
                return user
        except Exception:
            pass

    # AnonymousUserFactory plugins have never been usable in ERP5 so
    # instead of bothering user to create one on existing site, ignore
    # these plugins and call directly our code to create anonymous users.
    def _createAnonymousUser(self, plugins):
        user = createAnonymousUser(self)
        return (nobody if user is None else user).__of__(self)

    PluggableAuthService._createAnonymousUser = _createAnonymousUser