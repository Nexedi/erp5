## Script (Python) "verif_modele"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# in the case where there's nothing to print
print " "

for o in context.objectValues("CORAMY Modele"):
  print o.id
  nb_forme = 0
  for forme in o.getCategoryMembershipList(('eid','specialise'),portal_type='Forme'):
    nb_forme+=1
    forme_path = '/coramy/' + forme
    ob_search = context.restrictedTraverse(path=forme_path,default=None)
    if ob_search is None:
      print "  cette forme n'existe pas: " + forme
    else:
      ob_search_list = context.portal_catalog.searchResults(path=forme_path)
      if len(ob_search_list) == 0:
        print "  cette forme existe mais n'est pas dans le catalog: " + forme

    if nb_forme == 2:
      print "  Il y a deux Formes pour : " + o.id
  if nb_forme == 0:
    print "  Il n'y a pas de Formes pour : " + o.id  

  nb_vetement = 0
  for vetement in o.getCategoryMembershipList(('eid','specialise'),portal_type='Vetement'):
    nb_vetement+=1
    vetement_path = '/coramy/' + vetement
    ob_search = context.restrictedTraverse(path=vetement_path,default=None)
    if ob_search is None:
      print "  ce vetement n'existe pas: " + vetement
    else:
      ob_search_list = context.portal_catalog.searchResults(path=vetement_path)
      if len(ob_search_list) == 0:
        print "  ce vetement existe mais n'est pas dans le catalog: " + vetement
    if nb_vetement == 2:
      print "  Il y a deux Vetements pour : " + o.id

  if nb_vetement == 0:
    print "  Il n'y a pas de Vetements pour : " + o.id  


return printed
