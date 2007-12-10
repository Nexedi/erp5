from Products import iHotfix

from Products.PageTemplates.PageTemplate import PageTemplate
from TAL.TALInterpreter import TALInterpreter, FasterStringIO

# revert iHotfix patch that forces PageTemplate to output a string instead of
# a unicode object
TALInterpreter.StringIO = FasterStringIO
PageTemplate.StringIO = FasterStringIO
