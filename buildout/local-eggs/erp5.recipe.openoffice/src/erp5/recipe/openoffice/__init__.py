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

import z3c.recipe.openoffice.recipe as original
import os
import platform

class Recipe(original.Recipe):
  """
  Wrap z3c.recipe.openoffice to allow selecting the architecture
  """
  def __init__(self, buildout, name, options):
    machine = platform.uname()[-2]
    if machine in ('i386', 'i586', 'i686'):
      target = 'x86_32'
    elif machine == 'x86_64':
      target = 'x86_64'
    else:
      raise ValueError('Unknown machine')

    options['download-url'] = options['download-%s' % target]
    original.Recipe.__init__(self, buildout, name, options)
    self.options['tmp-storage'] = buildout['buildout'].get('download-cache',
                os.path.join(buildout['buildout']['directory'], 'download'))
