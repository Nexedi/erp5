##parameters=list=[],initial_quantity=[]

# This scripts allows to update a list so that it
# converts variation on a quantity to the quantity itself
# ie, if list=[[DateTime('09/10/2003'),+4],[DateTime('09/19/2003'),-8]], 
# and initial_quantity = [3]
# result: [[DateTime('2003/09/10'), 7], [DateTime('2003/09/19'), -1]]
# The list given have to be of the forme:
#  list = [[Datetime(),value (,value)*],([Datetime(),value (,value)*])*]
# The initial_quantity have to be like this :
#  initial_quantity = [value (,value)*]


list.sort()

quantity_list = []
#if type(initial_quantity) is type(1):
#  initial_quantity = [initial_quantity]

if len(list) >= 1 and (len(list[0])-1)==len(initial_quantity):
  quantity_list.append([list[0][0]])
  for i in range(1,len(list[0])):
    if list[0][i]==None:
      list[0][i]=0
    quantity_list[0].append(initial_quantity[i-1] + list[0][i])
  for value in range(1,len(list)):
    quantity_list.append([list[value][0]])
    for i in range(1,len(list[0])):
      if list[value][i]==None:
        list[value][i]=0
      quantity_list[value].append(quantity_list[value-1][i] + list[value][i])

return quantity_list
