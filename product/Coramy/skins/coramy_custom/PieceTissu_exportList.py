## Script (Python) "PieceTissu_exportList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
piece_list = context.zGetLocatedPieceTissuList()
cr = '\r'
tab = '\t'
movement_log = 'Piece'+tab+tab+'Quantité initiale'+tab+'Quantité restante'+cr

for piece_item in piece_list :
  piece= piece_item.getObject()
  movement_log += piece.getRelativeUrl()+tab+piece.getId()+tab+str(piece.getQuantity())+tab+str(piece.getRemainingQuantity())+tab+piece.getLocation()+tab+piece.getComment().replace('\r',' ') + cr

request.RESPONSE.setHeader('Content-Type','application/text')

return movement_log
