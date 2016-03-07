'''
This script remove accents and spaces and other things from the text to generate a new login
'''

inc = 1

# XXX here it should be possible to use a regular expression
login = text.lower()
login = login.replace(' ', '_')
login = login.replace('é', 'e')
login = login.replace('è', 'e')
login = login.replace('à', 'a')
login = login.replace('ç', 'c')

new_login = login

# search if the login already exists
result = context.portal_catalog(reference=login)

while len(result) > 0:

  if new_login.rfind('-'):
    # if a number has already been added to the end of the login, increase it
    if new_login[new_login.rfind('-')+1:].isdigit():
      inc = int(new_login[new_login.rfind('-')+1:]) + 1

  new_login = '%s-%s' % (login, inc)
  result = context.portal_catalog(reference=new_login)

return new_login
