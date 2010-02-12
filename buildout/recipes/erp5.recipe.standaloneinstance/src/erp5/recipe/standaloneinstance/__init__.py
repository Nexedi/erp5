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

import os
import zc.buildout
import erp5.recipe.zope2instance
import erp5.recipe.createsite

class Recipe(erp5.recipe.zope2instance.Recipe, erp5.recipe.createsite.Recipe):
  def __init__(self, buildout, name, options):
    standalone_location = options.get('location')
    if not standalone_location:
      raise zc.buildout.UserError('Location have to be specified')
    options['control-script'] = options.get('control-script',
        os.path.join(standalone_location, 'bin', 'zopectl'))
    erp5.recipe.createsite.Recipe.__init__(self, buildout, name, options)
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
    self.buildout, self.options, self.name = buildout, options, name
    self.zope2_location = options.get('zope2-location', '')

    options['bin-directory'] = os.path.join(standalone_location, 'bin')
    options['scripts'] = '' # suppress script generation.
    options['file-storage'] = options.get('file-storage',
        os.path.join(standalone_location, 'var', 'Data.fs'))

    # Relative path support for the generated scripts
    relative_paths = options.get(
        'relative-paths',
        buildout['buildout'].get('relative-paths', 'false')
        )
    if relative_paths == 'true':
        options['buildout-directory'] = buildout['buildout']['directory']
        self._relative_paths = options['buildout-directory']
    else:
        self._relative_paths = ''
        assert relative_paths == 'false'

  def install(self):
    # initalise zope instance
    erp5.recipe.zope2instance.Recipe.install(self)

    # initialise ERP5 part
    erp5.recipe.createsite.Recipe.install(self)
    # we return nothing, as this is totally standalone installation
    return []

  def build_zope_conf(self):
    # preparation for further fixing (chroot everything inside instance, etc)
    erp5.recipe.zope2instance.Recipe.build_zope_conf(self)

  def update(self):
    return erp5.recipe.zope2instance.Recipe.update(self)
