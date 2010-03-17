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
import erp5.recipe.mysqldatabase

class WithMinusTemplate(Template):
  idpattern = '[_a-z][-_a-z0-9]*'

class Recipe(plone.recipe.zope2instance.Recipe):
  def __init__(self, buildout, name, options):
    instancehome = options.get('instancehome')
    if not instancehome:
      raise zc.buildout.UserError('instancehome have to be specified')
    options['control-script'] = options.get('control-script',
        os.path.join(instancehome, 'bin', 'zopectl'))
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
    options['bin-directory'] = os.path.join(instancehome, 'bin')
    options['scripts'] = '' # suppress script generation.
    options['file-storage'] = options.get('file-storage',
        os.path.join(instancehome, 'var', 'Data.fs'))
    self.buildout, self.options, self.name = buildout, options, name
    self.zope2_location = options.get('zope2-location', '')

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
    instancehome = options['instancehome']

    requirements, ws = self.egg.working_set()
    ws_locations = [d.location for d in ws]

    if options.get('mysql_create_database', 'false').lower() == 'true':
       # Use mysqldatabase recipe for Create the mysql database.
       erp5.recipe.mysqldatabase.Recipe(self.buildout, self.name, self.options).install()


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
      zc.buildout.easy_install._safe_arg(instancehome),
      '-u', options['user'],
      ) == 0

    # patch begin: create several directories
    for directory in ('Constraint', 'Document', 'PropertySheet', 'tests'):
      path = os.path.join(instancehome, directory)
      if not os.path.exists(path):
        os.mkdir(path)
    # patch end: create several directories

    # Save the working set:
    open(os.path.join(instancehome, 'etc', '.eggs'), 'w').write(
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
      self.update_zodb()
    # we return nothing, as this is totally standalone installation
    return []

  def update_zodb(self):
    options = self.options
    zopectl_path = os.path.join(options['bin-directory'],
                  options['control-script'])
    script_name = os.path.join(os.path.dirname(__file__),
                 'create_erp5_instance.py')
    argv = [zopectl_path, 'run', script_name]

    if options.get('portal_id'):
      argv.extend(['--portal_id', options['portal_id']])
    if options.get('erp5_sql_connection_string'):
      argv.extend(['--erp5_sql_connection_string',
            options['erp5_sql_connection_string']])

    if options.get('cmf_activity_sql_connection_string'):
      argv.extend(['--cmf_activity_sql_connection_string',
         options['cmf_activity_sql_connection_string']])
    if options.get('erp5_catalog_storage'):
      argv.extend(['--erp5_catalog_storage',
            options['erp5_catalog_storage']])
    if options.get('user'):
      # XXX read rom zope2instance section ?
      argv.extend(['--initial-user',
            options['user']])

    argv.extend(['--bt5-path',
          os.path.join(options['bt5-path'])])
    argv.extend([bt for bt in options.get('bt5', '').split('\n') if bt])

    assert os.spawnl(
       os.P_WAIT, zopectl_path, *argv ) == 0

  def build_zope_conf(self):
    options = self.options
    instancehome = options['instancehome']
    template_input_data = ''.join(
        file(self.options['zope_conf_template'].strip()).readlines()
    )
    template = WithMinusTemplate(template_input_data)
    # XXX: support local products with simple option instead of hardcoding
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
    zope_conf_path = os.path.join(instancehome, 'etc', 'zope.conf')
    file(zope_conf_path, 'w').write(result)

  def update(self):
#    if self.options.get('force-zodb-update','false').strip().lower() == 'true':
#      return self.install()
    options = self.options
    instancehome = options['instancehome']

    requirements, ws = self.egg.working_set()
    ws_locations = [d.location for d in ws]

    if os.path.exists(instancehome):
      # See if we can stop. We need to see if the working set path
      # has changed.
      saved_path = os.path.join(instancehome, 'etc', '.eggs')
      if os.path.isfile(saved_path):
        if (open(saved_path).read() !=
          '\n'.join(ws_locations)
          ):
          # Something has changed. Blow away the instance.
          return self.install()
        elif options.get('site-zcml'):
          self.build_package_includes()

      # Nothing has changed.
      self.install_scripts()
      return instancehome
    else:
      return self.install()

  def patch_binaries(self, ws_locations):
    if not self.zope2_location:
      return

    instancehome = self.options['instancehome']
    path =":".join(ws_locations)
    for script_name in ('runzope', 'zopectl'):
      script_path = os.path.join(instancehome, 'bin', script_name)
      script = open(script_path).read()
      if '$SOFTWARE_HOME:$PYTHONPATH' in script:
        script = script.replace(
          '$SOFTWARE_HOME:$PYTHONPATH',
          path+':$SOFTWARE_HOME:$PYTHONPATH'
          )
      elif "$SOFTWARE_HOME" in script:
        # Zope 2.8
        script = script.replace(
          '"$SOFTWARE_HOME"',
          '"'+path+':$SOFTWARE_HOME:$PYTHONPATH"'
          )
      f = open(script_path, 'w')
      f.write(script)
      f.close()
    # Patch Windows scripts
    for script_name in ('runzope.bat', ):
      script_path = os.path.join(instancehome, 'bin', script_name)
      if os.path.exists(script_path):
        script = open(script_path).read()
        # This could need some regex-fu
        lines = [l for l in script.splitlines()
             if not l.startswith('@set PYTHON=')]
        lines.insert(2, '@set PYTHON=%s' % self.options['executable'])
        script = '\n'.join(lines)

        # Use servicewrapper.py instead of calling run.py directly
        # so that sys.path gets properly set. We used to append
        # all the eggs to PYTHONPATH in runzope.bat, but after
        # everything was turned into eggs we exceeded the
        # environment maximum size for cmd.exe.
        script = script.replace(
          "ZOPE_RUN=%SOFTWARE_HOME%\\Zope2\\Startup\\run.py",
          "ZOPE_RUN=%INSTANCE_HOME%\\bin\\servicewrapper.py"
          )
        f = open(script_path, 'w')
        f.write(script)
        f.close()
    # Patch Windows service scripts
    path =";".join(ws_locations)
    script_name = 'zopeservice.py'
    script_path = os.path.join(instancehome, 'bin', script_name)
    if os.path.exists(script_path):
      script = open(script_path).read()
      script = script.replace(
          "ZOPE_RUN = r'%s\\Zope2\\Startup\\run.py' % SOFTWARE_HOME",
          "ZOPE_RUN = r'%s\\bin\\servicewrapper.py' % INSTANCE_HOME"
          )
      f = open(script_path, 'w')
      f.write(script)
      f.close()
    script_name = 'servicewrapper.py'
    script_path = os.path.join(instancehome, 'bin', script_name)
    script = """import sys

sys.path[0:0] = [
%s]

if __name__ == '__main__':
  from Zope2.Startup import run
  run.run()
""" % ''.join(['  \'%s\',\n' % l.replace('\\', '\\\\') for l in ws_locations])
    f = open(script_path, 'w')
    f.write(script)
    f.close()
    # Add a test.bat that works on Windows
    new_script_path = os.path.join(instancehome, 'bin', 'test.bat')
    script_path = os.path.join(instancehome, 'bin', 'runzope.bat')
    if os.path.exists(script_path):
      script = open(script_path).read()
      # Adjust script to use the right command
      script = script.replace("@set ZOPE_RUN=%SOFTWARE_HOME%\\Zope2\\Startup\\run.py",
                  """@set ZOPE_RUN=%ZOPE_HOME%\\test.py
@set ERRLEV=0""")
      script = script.replace("\"%ZOPE_RUN%\" -C \"%CONFIG_FILE%\" %1 %2 %3 %4 %5 %6 %7",
                  """\"%ZOPE_RUN%\" --config-file \"%CONFIG_FILE%\" %1 %2 %3 %4 %5 %6 %7 %8 %9
@IF %ERRORLEVEL% NEQ 0 SET ERRLEV=1
@ECHO \"%ERRLEV%\">%INSTANCE_HOME%\\testsexitcode.err""")
      f = open(new_script_path, 'w')
      f.write(script)
      f.close()

  def install_scripts(self):
    options = self.options
    instancehome = options['instancehome']

    # The instance control script
    zope_conf = os.path.join(instancehome, 'etc', 'zope.conf')
    zope_conf_path = options.get('zope-conf', zope_conf)

    extra_paths = []

    # Only append the instance home and Zope lib/python in a non-egg
    # environment
    lib_python = os.path.join(self.zope2_location, 'lib', 'python')
    if os.path.exists(lib_python):
      extra_paths.append(os.path.join(instancehome))
      extra_paths.append(lib_python)

    extra_paths.extend(options.get('extra-paths', '').split())

    requirements, ws = self.egg.working_set(['plone.recipe.zope2instance'])

    if options.get('no-shell') == 'true':
      zc.buildout.easy_install.scripts(
        [(self.options.get('control-script', self.name),
          'plone.recipe.zope2instance.ctl', 'noshell')],
        ws, options['executable'], options['bin-directory'],
        extra_paths = extra_paths,
        arguments = ('\n    ["-C", %r]'
               '\n    + sys.argv[1:]'
               % zope_conf_path
               ),
        relative_paths=self._relative_paths,
        )
    else:
      zc.buildout.easy_install.scripts(
        [(self.options.get('control-script', self.name),
          'plone.recipe.zope2instance.ctl', 'main')],
        ws, options['executable'], options['bin-directory'],
        extra_paths = extra_paths,
        arguments = ('\n    ["-C", %r]'
               '\n    + sys.argv[1:]'
               % zope_conf_path
               ),
        relative_paths=self._relative_paths,
        )

    # The backup script, pointing to repozo.py
    repozo = options.get('repozo', None)
    if repozo is None:
      repozo = os.path.join(self.zope2_location, 'utilities', 'ZODBTools', 'repozo.py')

    directory, filename = os.path.split(repozo)
    if repozo and os.path.exists(repozo):
      zc.buildout.easy_install.scripts(
        [('repozo', os.path.splitext(filename)[0], 'main')],
        {}, options['executable'], options['bin-directory'],
        extra_paths = [os.path.join(self.zope2_location, 'lib', 'python'),
                 directory],
        relative_paths=self._relative_paths,
        )

  def build_package_includes(self):
    """Create ZCML slugs in etc/package-includes
    """
    instancehome = self.options['instancehome']
    sitezcml_path = os.path.join(instancehome, 'etc', 'site.zcml')
    zcml = self.options.get('zcml')
    site_zcml = self.options.get('site-zcml')
    additional_zcml = self.options.get("zcml-additional")

    if site_zcml:
      open(sitezcml_path, 'w').write(site_zcml)
      return

    if zcml:
      zcml=zcml.split()

    if additional_zcml or zcml:
      includes_path = os.path.join(instancehome, 'etc', 'package-includes')

      if not os.path.exists(includes_path):
        # Zope 2.9 does not have a package-includes so we
        # create one.
        os.mkdir(includes_path)
      else:
        if '*' in zcml:
          zcml.remove('*')
        else:
          shutil.rmtree(includes_path)
          os.mkdir(includes_path)

    if additional_zcml:
      path=os.path.join(includes_path, "999-additional-overrides.zcml")
      open(path, "w").write(additional_zcml.strip())

    if zcml:
      if not os.path.exists(sitezcml_path):
        # Zope 2.9 does not have a site.zcml so we copy the
        # one out from Five.
        skel_path = os.path.join(self.zope2_location, 'lib', 'python',
                     'Products', 'Five', 'skel',
                     'site.zcml')
        shutil.copyfile(skel_path, sitezcml_path)

      n = 0
      package_match = re.compile('\w+([.]\w+)*$').match
      for package in zcml:
        n += 1
        orig = package
        if ':' in package:
          package, filename = package.split(':')
        else:
          filename = None

        if '-' in package:
          package, suff = package.split('-')
          if suff not in ('configure', 'meta', 'overrides'):
            raise ValueError('Invalid zcml', orig)
        else:
          suff = 'configure'

        if filename is None:
          filename = suff + '.zcml'

        if not package_match(package):
          raise ValueError('Invalid zcml', orig)

        path = os.path.join(
          includes_path,
          "%3.3d-%s-%s.zcml" % (n, package, suff),
          )
        open(path, 'w').write(
          '<include package="%s" file="%s" />\n'
          % (package, filename)
          )


