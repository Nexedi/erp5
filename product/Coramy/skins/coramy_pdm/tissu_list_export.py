## Script (Python) "tissu_list_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selection = context.portal_selections.getSelectionFor('tissu_selection',REQUEST=context.REQUEST)
tissu_list = selection(context=context)
request = context.REQUEST
tab = '\t'
cr = '\n'

export ="Référence"+tab+"Fournisseur"+tab+"Réf. Fournisseur"+tab+"Collection"+tab+"Description"+cr
for tissu_item in tissu_list:
  tissu=tissu_item.getObject()
  if tissu <> None :
    ligne_tissu = ''
    ligne_tissu += str(tissu.getId())+tab
    ligne_tissu += str(tissu.getDefaultSourceTitle())+tab
    ligne_tissu += str(tissu.getSourceReference())+tab
    ligne_tissu += str(tissu.getCollection())+tab
    ligne_tissu += str(tissu.getDescription())+tab

    export += ligne_tissu+cr

request.RESPONSE.setHeader('Content-Type','application/text')

return export
