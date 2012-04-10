
from Products.ERP5Form.ListBox import ListBoxHTMLRenderer

def getListBoxRenderer(self, field, REQUEST, render_prefix=None):
  """ XXXX"""
  return ListBoxHTMLRenderer(self, field, REQUEST, render_prefix)
