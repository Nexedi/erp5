## Script (Python) "PieceTissu_fastInputFieldRender"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
fast_input_list = context.PieceTissu_fastInputList()[0]
formatted_text = []

for i in range (11) :
  formatted_text.append( 'Piece n° '+str(i+1))
  for text in fast_input_list :
    formatted_text.append(text+':')
  formatted_text.append('')

return formatted_text
