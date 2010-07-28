from setuptools import setup, find_packages

name = "invokepython"
version = '0.1'

setup(
    name = name,
    version = version,
    author = "Lukasz Nowak",
    author_email = "luke@nexedi.com",
    description = "Generates python wrapper around python interpreter",
    long_description = "Generates python wrapper, which acts like normal "\
        "python interpreter, but containing full list of additional python "\
        "paths",
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
