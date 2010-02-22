from setuptools import setup, find_packages

name = "erp5.recipe.openoffice"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Nicolas Dumazet",
    author_email = "nicolas.dumazet@nexedi.com",
    description = "ZC Buildout recipe to install openoffice",
    license = "ZPL 2.1",
    keywords = "openoffice buildout",
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['erp5', 'erp5.recipe'],
    install_requires = [
        'z3c.recipe.openoffice',
    ],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
