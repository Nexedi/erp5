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

import os, sys
from string import Template
import zc.buildout
import plone.recipe.zope2instance
import erp5.recipe.createsite

class WithMinusTemplate(Template):
  idpattern = '[_a-z][-_a-z0-9]*'

class Recipe(plone.recipe.zope2instance.Recipe, erp5.recipe.createsite.Recipe):
  def __init__(self, buildout, name, options):
    standalone_location = options.get('instancehome')
    if not standalone_location:
      raise zc.buildout.UserError('instancehome have to be specified')
    options['location'] = standalone_location
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
    # Override erp5.recipe.zope2instance so as to create several
    # directories used by ERP5.
    options = self.options
    location = options['instancehome']

    requirements, ws = self.egg.working_set()
    ws_locations = [d.location for d in ws]

    # What follows is a bit of a hack because the instance-setup mechanism
    # is a bit monolithic. We'll run mkzopeinstance and then we'll
    # patch the result. A better approach might be to provide independent
    # instance-creation logic, but this raises lots of issues that
    # need to be stored out first.
    if not self.zope2_location:
      mkzopeinstance = os.path.join(
        options['bin-directory'], 'mkzopeinstance')
      if not mkzopeinstance:
        # EEE
        return

    else:
      mkzopeinstance = os.path.join(
        self.zope2_location, 'bin', 'mkzopeinstance.py')
      if not os.path.exists(mkzopeinstance):
        mkzopeinstance = os.path.join(
          self.zope2_location, 'utilities', 'mkzopeinstance.py')
      if sys.platform[:3].lower() == "win":
        mkzopeinstance = '"%s"' % mkzopeinstance

    if not mkzopeinstance:
      # EEE
      return

    assert os.spawnl(
      os.P_WAIT, os.path.normpath(options['executable']),
      zc.buildout.easy_install._safe_arg(options['executable']),
      mkzopeinstance, '-d',
      zc.buildout.easy_install._safe_arg(location),
      '-u', options['user'],
      ) == 0

    # patch begin: create several directories
    for directory in ('Constraint', 'Document', 'PropertySheet', 'tests'):
      path = os.path.join(location, directory)
      if not os.path.exists(path):
        os.mkdir(path)
    # patch end: create several directories

    # Save the working set:
    open(os.path.join(location, 'etc', '.eggs'), 'w').write(
      '\n'.join(ws_locations))

    # Make a new zope.conf based on options in buildout.cfg
    self.build_zope_conf()

    # Patch extra paths into binaries
    self.patch_binaries(ws_locations)

    # Install extra scripts
    self.install_scripts()

    # Add zcml files to package-includes
    self.build_package_includes()

    if self.options.get('force-zodb-update','false').strip().lower() == 'true':
      force_zodb_update = True
    else:
      force_zodb_update = False

    if not os.path.exists(options['zodb-path'].strip()) or \
        force_zodb_update:
      # initialise ERP5 part only in case if ZODB not exist yet or it is forced
      erp5.recipe.createsite.Recipe.install(self)
    # we return nothing, as this is totally standalone installation
    return []

  def build_zope_conf(self):
    options = self.options
    location = options['instancehome']
    template_input_data = ''.join(
        file(self.options['zope_conf_template'].strip()).readlines()
    )
    template = WithMinusTemplate(template_input_data)
    # make prepend products with 'products'
    options_dict = self.options.copy()
    if 'products' in options_dict:
      prefixed_products = []
      for product in options_dict['products'].split('\n'):
        product = product.strip()
        if product:
          prefixed_products.append('products %s' % product)
      options_dict['products'] = '\n'.join(prefixed_products)
    result = template.substitute(options_dict)
    zope_conf_path = os.path.join(location, 'etc', 'zope.conf')
    file(zope_conf_path, 'w').write(result)

  def update(self):
    return plone.recipe.zope2instance.Recipe.update(self)
