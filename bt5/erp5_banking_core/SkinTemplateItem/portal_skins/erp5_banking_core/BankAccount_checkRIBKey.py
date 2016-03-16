d = {}
d['A'] = d['J'] = '1'
d['B'] = d['K'] = d['S'] = '2'
d['C'] = d['L'] = d['T'] = '3'
d['D'] = d['M'] = d['U'] = '4'
d['E'] = d['N'] = d['V'] = '5'
d['F'] = d['O'] = d['W'] = '6'
d['G'] = d['P'] = d['X'] = '7'
d['H'] = d['Q'] = d['Y'] = '8'
d['I'] = d['R'] = d['Z'] = '9'

old_rib = account_nb[-2:]

new_account_nb = ""
for nb in list(account_nb)[:-2]:
  if d.has_key(nb):
    new_account_nb += d[nb]
  else:
    new_account_nb += nb

new_account_nb += "00"
new_account_nb = long(new_account_nb)
rib = 97 - new_account_nb % 97

return (str(rib) == str(old_rib))
