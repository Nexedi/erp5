## Script (Python) "PieceTissu_findNegativeQty"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
cr = '\n'
tab = '\t'
movement_log = 'Problèmes'+cr

piece_list = context.portal_catalog(portal_type=('Piece Tissu',))

for piece_item in piece_list :
  piece = piece_item.getObject()
  if piece is not None :
    qty = piece.getRemainingQuantity()
    if qty < 0 :
      movement_log += piece.getRelativeUrl()+tab+str(qty)+cr

request.RESPONSE.setHeader('Content-Type','application/text')

return movement_log
