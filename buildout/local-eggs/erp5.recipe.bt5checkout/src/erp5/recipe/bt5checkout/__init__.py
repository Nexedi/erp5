# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import infrae.subversion

class Recipe(infrae.subversion.Recipe):
  def __init__(self, buildout, name, options):
    base, revision, urls = options['base'], options['revision'], \
        options['urls']
    new_url_list = []
    for url in options['urls'].split('\n'):
      if url:
        url = '%s/%s/%s %s' % (base, url, revision, url)
      new_url_list.append(url)
    options['urls'] = '\n'.join(new_url_list)
    infrae.subversion.Recipe.__init__(self, buildout, name, options)
