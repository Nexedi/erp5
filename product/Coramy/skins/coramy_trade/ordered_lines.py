## Script (Python) "ordered_lines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lignes_cde
##title=
##
index1 = {}
keys2 = []
nb_lignes = len(lignes_cde)

for i in range(nb_lignes):
  index1[int(lignes_cde[i].getId())]=i

keys1 = index1.keys()
keys1.sort()
for i in range(nb_lignes):
  keys2.append(index1[keys1[i]])

return keys2
