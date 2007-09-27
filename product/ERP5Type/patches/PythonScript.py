##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Products.PythonScripts.PythonScript import PythonScript
from OFS.misc_ import p_
from App.ImageFile import ImageFile


def haveProxyRole(self):
  """if a script has proxy role, return True"""
  if self._proxy_roles:
    return True
  return False


def om_icons(self):
  """Return a list of icon URLs to be displayed by an ObjectManager"""
  icons = ({'path': 'misc_/PythonScripts/pyscript.gif',
            'alt': self.meta_type, 'title': self.meta_type},)
  if self.haveProxyRole():
    icons = ({'path': 'p_/PythonScript_ProxyRole_icon',
              'alt': 'Proxy Roled Python Script',
              'title': 'This script has proxy role.'},)
  return icons

pyscript_proxyrole = ImageFile('pyscript_proxyrole.gif', globals())

#
# Add proxy role icon in ZMI
#
PythonScript.haveProxyRole = haveProxyRole
PythonScript.om_icons = om_icons
p_.PythonScript_ProxyRole_icon = pyscript_proxyrole
