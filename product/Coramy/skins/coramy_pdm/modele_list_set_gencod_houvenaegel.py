## Script (Python) "modele_list_set_gencod_houvenaegel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selection = context.portal_selections.getSelectionFor('modele_selection',REQUEST=context.REQUEST)
modele_list = selection(context=context)
request = context.REQUEST

for modele_item in modele_list:
  modele=modele_item.getObject()
  modele.setEan13Modele(modele.portal_categories.group.Coramy.Houvenaegel)
