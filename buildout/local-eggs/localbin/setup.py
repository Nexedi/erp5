from setuptools import setup, find_packages

name = "invokepython"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Lukasz Nowak",
    author_email = "luke@nexedi.com",
    description = "ZC Buildout recipe to invoke full python interpreter",
    license = "ZPL 2.1",
    keywords = "python interpreter",
    packages = find_packages(),
    scripts = [name+".py",],
    include_package_data = True,
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Operating System :: POSIX :: Linux",
      ],
    zip_safe=False,
    entry_points = """
    [console_scripts]
    invokepython = invokepython:invokepython
    """,
    )
