import tempfile
import os
import shutil
import sys
import types

def importModule(module_name):
  __import__(module_name)
  return sys.modules[module_name]


def ERP5Site_generateCodeDocumentation(self,
    backend,
    module_name_list=("erp5.component.test.erp5_version.testSupportRequest", "erp5.component.test.erp5_version.testERP5Administration",),
    REQUEST=None,
    RESPONSE=None):
  """Generate documentation for a component module.

  `module_name` must be the "importable" dotted name of the component, ie not
  test.erp5.testSupportRequest but erp5.component.test.${version}.testSupportRequest
  """
  if backend == 'pdoc':
    import pdoc # 0.32

    pdoc.import_path = sys.path # when reloading this seems needed.
    def docfilter(x):
      """pdoc documents by default inherited classes and attributes.

      This is too verbose when documenting a test component (which is my use case now).
      """
      if isinstance(x, pdoc.Function) or isinstance(x, pdoc.Variable):
        if not x.cls:
          return True
        return x.name in x.cls.cls.__dict__
      return True

    def doc_module(module_name):
      return pdoc.html(module_name, docfilter=docfilter, allsubmodules=True) \
        + '''<style>#sidebar { overflow: scroll !important; }</style>''' # workaround style problem with long names.

    # first generate an index page, by creating a fake module aggregating all the modules
    # we are documenting.
    fake_module_name = 'index' # https://pypi.org/project/index/ ... looks we won't have this installed.
    sys.modules[fake_module_name] = module = types.ModuleType(fake_module_name)
    module_all = []
    for module_name in module_name_list:
      setattr(module, module_name, importModule(module_name))
      module_all.append(module_name)
    module.__all__ = module_all

    tmpdir = tempfile.mkdtemp()
    try:
      doc_dir = os.path.join(tmpdir, 'html')
      os.mkdir(doc_dir)
      open(os.path.join(doc_dir, 'index.html'), 'w').write(doc_module(fake_module_name))
      for module_name in module_name_list:
        # create parent directory structure
        parts = module_name.split('.')
        for i in range(len(parts)):
          dir_ = os.path.join(doc_dir, *parts[:i+1])
          if not os.path.exists(dir_):
            os.mkdir(dir_)
        open(os.path.join(doc_dir, *parts + ['index.html']), 'w').write(
          doc_module(module_name))

      data = open(shutil.make_archive(os.path.join(tmpdir, 'out.zip'), 'zip', doc_dir), 'rb').read()
      if RESPONSE is not None:
        RESPONSE.setHeader('content-disposition', 'attachment;filename=doc.zip')
      return data
    finally:
      shutil.rmtree(tmpdir)

    return doc_module(fake_module_name)

  if backend == 'epydoc':
    from epydoc.docbuilder import build_doc_index
    from epydoc.docwriter.html import HTMLWriter
    tmpdir = tempfile.mkdtemp()
    try:
      doc_dir = os.path.join(tmpdir, 'html')
      os.mkdir(doc_dir)
      for module_name in module_name_list:
        module = importModule(module_name)
        if hasattr(module, '__loader__'):
          # XXX epydoc wants __file__, we'll give him files...
          with tempfile.NamedTemporaryFile(suffix='.py', dir=tmpdir, delete=False) as f:
            f.write(module.__loader__.get_source(module_name))
          module.__file__ = f.name

      html_writer = HTMLWriter(build_doc_index(module_name_list))
      html_writer.write(doc_dir)

      data = open(shutil.make_archive(os.path.join(tmpdir, 'out.zip'), 'zip', doc_dir), 'rb').read()
      if RESPONSE is not None:
        RESPONSE.setHeader('content-disposition', 'attachment;filename=doc.zip')
      return data
    finally:
      shutil.rmtree(tmpdir)

  if backend == 'sphinx':
    tmpdir = tempfile.mkdtemp()
    try:
      with open(os.path.join(tmpdir, 'conf.py'), 'w') as conf:
        conf.write("""
project = u'ERP5 Generated Documentation'
html_theme = 'default'
master_doc = 'index'
extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.autosummary',
  'sphinx.ext.doctest',
  'sphinx.ext.viewcode',
  'sphinxcontrib.plantuml']

plantuml = '/srv/slapgrid/slappart8/bin/plantuml'
htmlhelp_basename = 'ERP5Doc'
html_show_sourcelink = True
pygments_style = 'sphinx'
autodoc_default_flags = ['members', 'undoc-members']
""")

      with open(os.path.join(tmpdir, 'index.rst'), 'w') as index:
        index.write("""
ERP5 Auto-Generated Documentation
=================================

.. toctree::
    :maxdepth: 4
    :caption: Contents:

""")
        for module_name in module_name_list:
          module = importModule(module_name)
          # XXX workaround https://nexedi.erp5.net/bug_module/20181018-12F285A
          # XXX if modules have a __file__, sphinx will use this, even if the module have a loader providing get_source
          # https://github.com/sphinx-doc/sphinx/blob/c89edd82eb76b175be919774ce7d4047bfe446ed/sphinx/util/__init__.py#L301
          # as a workaround, just remove the file on the module.
          # XXX not sure this is safe.
          module.__file__ = None

          title = '{} module'.format(module_name)
          index.write(title + '\n')
          index.write('=' * len(title) + '\n')
          index.write("""
.. automodule:: {}

""".format(module_name))

        index.write("""
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""")

      from sphinx.cmd.build import main # Sphinx-1.8.1
      # https://github.com/sphinx-doc/sphinx/blob/master/sphinx/cmd/build.py#L299
      main(argv=[tmpdir, os.path.join(tmpdir, 'html')])
      data = open(
        shutil.make_archive(
          os.path.join(tmpdir, 'doc.zip'),
          'zip',
          os.path.join(tmpdir, 'html')
          ), 'rb').read()
      if RESPONSE is not None:
        RESPONSE.setHeader('content-disposition', 'attachement;filename=doc.zip')
      return data
    finally:
      shutil.rmtree(tmpdir)

  if backend == 'pydoc':
    import pydoc
    # XXX only supports 1 module (pydoc is anyway a bit ugly compared to others)
    return pydoc.html.docmodule(importModule(module_name_list[0]))

  raise TypeError("Unsupported backend {}".format(backend))