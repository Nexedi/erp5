import nbformat
import ssl
import re
from base64 import b64encode, b64decode
from nbconvert import HTMLExporter
from nbconvert.preprocessors import Preprocessor, ExecutePreprocessor
from xmlrpclib import ServerProxy
from urllib import urlencode
from urllib2 import urlopen

#import os
#os.environ['JUPYTER_CONFIG_DIR'] = "/srv/slapgrid/slappart5/srv/runner/instance/slappart10/ipython"
#os.environ['IPYTHONDIR'] = "/srv/slapgrid/slappart5/srv/runner/instance/slappart10/ipython"

class PyMarkdownPreprocessor(Preprocessor):
  """
  :mod:`nbconvert` Preprocessor for the python-markdown nbextension.
  This :class:`~nbconvert.preprocessors.Preprocessor` replaces kernel code in
  markdown cells with the results stored in the cell metadata.
  """

  def replace_variables(self, source, variables):
    """
    Replace {{variablename}} with stored value
    """
    try:
      replaced = re.sub(
        "{{(.*?)}}", lambda m: variables.get(m.group(1), ''), source)
    except TypeError:
      replaced = source
    return replaced

  def preprocess_cell(self, cell, resources, index):
    """
    Preprocess cell
    Parameters
    ----------
    cell : NotebookNode cell
      Notebook cell being processed
    resources : dictionary
      Additional resources used in the conversion process.  Allows
      preprocessors to pass variables into the Jinja engine.
    cell_index : int
      Index of the cell being processed (see base.py)
    """
    if cell.cell_type == "markdown":
      if hasattr(cell['metadata'], 'variables'):
        variables = cell['metadata']['variables']
        if len(variables) > 0:
          cell.source = self.replace_variables(
            cell.source, variables)
    return cell, resources

def to_html(self, **kw):
  notebook = nbformat.reads(self.getTextContent(), as_version=4)

  resources = {}
  notebook = \
    ExecutePreprocessor(timeout=300, kernel_name="erp5").preprocess(notebook, resources)[0]
  notebook = PyMarkdownPreprocessor().preprocess(notebook, resources)[0]

  html_exporter = HTMLExporter()
  html_exporter.template_file = 'full'
  
  body, resources = html_exporter.from_notebook_node(notebook)
  
  return body
  
def cloudoooConvertFile(self, data, source_mimetype, destination_mimetype, zip=False, refresh=False, conversion_kw=None):
  #url = 'https://softinst78992.host.vifib.net/erp5/ERP5Site_htmlToPdf'
  #data_dict = {'data' : b64encode(data)}
  #data_dict.update(**conversion_kw)
  #return urlopen(url=url, data=urlencode(data_dict)).read()
  proxy = ServerProxy(self.getPortalObject().portal_preferences.getPreferredDocumentConversionServerUrl(), allow_none=True)
  return b64decode(proxy.convertFile(b64encode(data), source_mimetype, destination_mimetype, zip, refresh, conversion_kw or {}))
