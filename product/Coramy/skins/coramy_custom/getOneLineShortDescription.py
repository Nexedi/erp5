## Script (Python) "getOneLineShortDescription"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=description='',len_max=100
##title=
##
# cut the description to fit under len_max caracteres
from string import join

result = description.split('\n')[0]

if len(result) > len_max:
  result = join(result[:len_max].split(' ')[:-2]) + '...'
else:
  result = description

return result
