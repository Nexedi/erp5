from setuptools import setup, find_packages

name = "createmandrivaspec"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Nicolas Dumazet",
    author_email = "nicolas.dumazet@nexedi.com",
    description = "ZC Buildout recipe to generate a Mandriva spec file",
    license = "ZPL 2.1",
    keywords = "mandriva buildout",
    packages = find_packages(),
    scripts = [name+".py",],
    include_package_data = True,
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Operating System :: POSIX :: Linux",
      ],
    install_requires = [
      'collective.recipe.template',
      ],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
