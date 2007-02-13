##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# monkeypatch to fix colon (:) in password
# remove once zope is ipdated to >=2.8.7
import sys
from ZPublisher.HTTPRequest import HTTPRequest, base64
from Acquisition import aq_base

def ERP5_authUserPW(self):
        global base64
        auth=self._auth
        if auth:
            if auth[:6].lower() == 'basic ':
                if base64 is None: import base64
                [name,password] = \
                    base64.decodestring(auth.split()[-1]).split(':', 1)
                return name, password

HTTPRequest._authUserPW = ERP5_authUserPW
