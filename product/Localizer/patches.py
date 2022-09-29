# -*- coding: utf-8 -*-
# Copyright (C) 2000-2006  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This is a hotfix, it dynamically applies several patches to Zope.
"""

# Import from the Standard Library
import logging
import os
import six

# Import from itools
from .itools.i18n import AcceptLanguageType

# Import from Zope
from ZPublisher.HTTPRequest import HTTPRequest
from zope.globalrequest import clearRequest, setRequest
from zope.globalrequest import getRequest as get_request

# Flag
patch = False
Z_DEBUG_MODE = os.environ.get('Z_DEBUG_MODE') == '1'


logger = logging.getLogger('Localizer')


# PATCH 1: Global Request
#
# The original purpose was to get the request object from places where the
# acquisition was disabled (within the __of__ method for example). It was
# inspired by the Tim McLaughlin's GlobalGetRequest proposal, see
# http://dev.zope.org/Wikis/DevSite/Proposals/GlobalGetRequest
#
# Currently it keeps a Context instance, which wraps the request object,
# but also other things, like the user's session, as it is required by
# the ikaaro CMS.
#
# The request objects are stored in a dictionary in the Publish module,
# whose keys are the thread id.
#
# Also, we keep the get_request method in the Globals module for backwards
# compatibility (with TranslationService for example).

def get_new_publish(zope_publish):
    def publish(request, *args, **kwargs):
        try:
            setRequest(request)
            return zope_publish(request, *args, **kwargs)
        finally:
            clearRequest()
    return publish


if patch is False:
    patch = True

# PATCH 2: Accept
#
# Adds the variable AcceptLanguage to the REQUEST.  It provides a higher
# level interface than HTTP_ACCEPT_LANGUAGE.

# Apply the patch
def new_processInputs(self):
    HTTPRequest.old_processInputs(self)

    request = self

    # Set the AcceptLanguage variable
    # Initialize with the browser configuration
    accept_language = request['HTTP_ACCEPT_LANGUAGE']
    # Patches for user agents that don't support correctly the protocol
    user_agent = request['HTTP_USER_AGENT']
    if user_agent.startswith('Mozilla/4') and user_agent.find('MSIE') == -1:
        # Netscape 4.x
        q = 1.0
        langs = []
        for lang in [ x.strip() for x in accept_language.split(',') ]:
            langs.append('%s;q=%f' % (lang, q))
            q = q/2
        accept_language = ','.join(langs)

    accept_language = AcceptLanguageType.decode(accept_language)
    self.other['AcceptLanguage'] = accept_language


if patch:
    HTTPRequest.old_processInputs = HTTPRequest.processInputs
    HTTPRequest.processInputs = new_processInputs

