## Script (Python) "Base_convertDateListToChartList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=list=[]
##title=
##
# This scripts allows to update a list so that it
# can be displayed correctly in a graph
# The list given have to be of the forme:
#  list = [[Datetime(),value (,value)*],([Datetime(),value (,value)*])*]

list.sort()

# Check if there is any none value, and replace it by 0

formated_list = []
if len(list) >= 1:
  for i in range(len(list)):
    for index_value in range(1,len(list[0])):
      if list[i][index_value]==None:
        list[i][index_value]=0
  formated_list.append(list[0])
  for i in range(1,len(list)):
    nb_days = int(list[i][0]-list[i-1][0])
    for day in range(1,nb_days):
      formated_list.append([list[i-1][0]+day])
      for nb_value in range(1,len(list[i-1])):
        formated_list[len(formated_list)-1].append(list[i-1][nb_value])
    formated_list.append(list[i])

return formated_list
