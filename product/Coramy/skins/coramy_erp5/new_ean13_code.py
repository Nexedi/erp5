## Script (Python) "new_ean13_code"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=country='', CNUF='', CIP=0
##title=
##
# this script returns a complete EAN13 Code including key
# the parameters are
# country (string 1 car): country code
# CNUF (string 5 to 8 car): Code National Unifié Fabricant
# CIP (int): Code Interface Produit

# ean_code = first_part (country+CNUF) + second_part (formatted CIF) + key

ean_code = ''
fisrt_part =''
second_part = ''
key = ''

if len(country)==1 and len(CNUF)>=5 and len(CNUF)<=8 :
  first_part = country + CNUF
  second_part = '0'*(12-len(first_part)-len(str(CIP)))+str(CIP)
  ean_code = first_part + second_part

# compute the key
  num_key = 0
  for i in range(6) :
    num_key += int(ean_code[i*2])
    num_key += int(ean_code[i*2-1])*3
  
  if divmod(num_key,10)[1] == 0 :
    key = '0'
  else :
    key = str((divmod(num_key,10)[0]+1)*10-num_key)

ean_code += key

return ean_code
