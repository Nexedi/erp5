from Products.ERP5Form.ListBox import ListBoxHTMLRenderer
from Products.CMFCore.Expression import getExprContext


def getListBoxRenderer(self, field, REQUEST, render_prefix=None):
  """ XXXX"""
  return ListBoxHTMLRenderer(self, field, REQUEST, render_prefix)

def execExpression(self, expression):
  """
    Allow exec <Products.CMFCore.Expression.Expression object ..> instances from 
    within  restricted environment.
    XXX: consider its security impact
  """
  econtext = getExprContext(self)
  return expression(econtext)
  
