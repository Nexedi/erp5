import os
import collective.recipe.template

class Recipe(collective.recipe.template.Recipe):
  def __init__(self, buildout, name, options):
    """
      Create a Mandriva RPM spec file from a template

      - input: path to spec template
      - output: path where generated spec should be saved
      - version: rpm version number, can be either the version
          or a file path containing the version
      - (section) name: rpm name
      - build_requires: a list of Mandriva packages required to build the rpm
      - svnpath: SVN path to current buildout

      optional:
        - release: rpm release number. Defaults to 1
    """
    package_list = options['package_list'].splitlines()
    package_list = map(lambda x: x.strip(), package_list)
    dependencies = ["BuildRequires: %s" % pkg for pkg in package_list if pkg]

    version = options['version'].strip()
    if os.path.exists(version):
      version = open(version, 'r').read().strip()

    release = options.get('release', str(1))

    options.update(dependencies="\n".join(dependencies),
                   version=version,
                   release=release)

    collective.recipe.template.Recipe.__init__(self, buildout, name, options)

