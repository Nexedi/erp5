# -*- coding: utf-8 -*-
import os
import zc.buildout
import erp5.recipe.zope2instance

class Recipe(erp5.recipe.zope2instance.Recipe):
  def __init__(self, buildout, name, options):
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
    self.buildout, self.options, self.name = buildout, options, name
    self.zope2_location = options.get('zope2-location', '')

    standalone_location = options.get('location')
    if not standalone_location:
      raise zc.buildout.UserError('Location have to be specified')
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
    erp5.recipe.zope2instance.Recipe.install(self)
    # we return nothing, as this is totally standalone installation
    return []

  def build_zope_conf(self):
    # preparation for further fixing (chroot everything inside instance, etc)
    erp5.recipe.zope2instance.Recipe.build_zope_conf(self)
