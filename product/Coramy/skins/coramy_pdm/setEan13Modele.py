## Script (Python) "setEan13Modele"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=societe
##title=
##
# retourne un code ean pour un modele
# "societe" pointe vers la categorie correspondant à la societe souhaitee (base category group)
# cette category possède des attributs CNUF, CIP et country

request = context.REQUEST
modele = context

country = societe.country
CNUF = societe.CNUF
CIP = societe.CIP

modele.edit(code_ean13 = modele.new_ean13_code(country,CNUF,CIP))
societe.edit(CIP = CIP+1)
