## Script (Python) "echantillon_page_count"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=total_nb, on_page
##title=
##
items_nb = float(total_nb)
items_in_page = float(on_page)
if items_nb/items_in_page==int(items_nb/items_in_page):
 page_nb = items_nb/items_in_page
else :
 page_nb = int(items_nb/items_in_page)+1

return page_nb
