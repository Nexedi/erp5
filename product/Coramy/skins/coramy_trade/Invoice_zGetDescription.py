## Script (Python) "Invoice_zGetDescription"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from string import join

description = context.getComment('')
return description

# Try to cut the comment without cutting the words 
# pbl: capital letter are larger, and the test on the length of sentence isn't good ...
def recursive_string_cut(b,s):
  l = 80
  if len(s) < l:
    return b+s
  else:
    c = s[:l].split(' ')
    if len(c) < 2:
      # I don't think that a word with more than 80 caracters can exist ... and it can crash the memory
      return s[:l]
    else:
      return recursive_string_cut(b+join(c[:-2],' ')+'\n', join(c[-2:],' ')+s[l:] )
    

# get all the lines
description_lines = description.split('\n')

# cut the too long lines
result_description_lines = map( ( lambda x: recursive_string_cut('',x) ),description_lines)

# recreate a string
result = join(result_description_lines,'\n')

return result
