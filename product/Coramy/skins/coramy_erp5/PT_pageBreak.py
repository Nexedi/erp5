## Script (Python) "PT_pageBreak"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=page_number
##title=
##
page_number[0] = page_number[0] + 1
if page_number[0] == 1 :
  return "toto"
else :
  return "PageA4"
