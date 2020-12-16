"""External Validator for IBAN on bank account
"""
import string
if not editor:
  return True

editor = editor.replace(' ', '').upper()
country_code = editor[:2]
checksum = editor[2:4]
bban = editor[4:]

iban_len_dict = {
 'AD': 24,
 'AT': 20,
 'BA': 20,
 'BE': 16,
 'BG': 22,
 'CH': 21,
 'CY': 28,
 'CZ': 24,
 'DE': 22,
 'DK': 18,
 'EE': 20,
 'ES': 24,
 'FI': 18,
 'FO': 18,
 'FR': 27,
 'GB': 22,
 'GI': 23,
 'GL': 18,
 'GR': 27,
 'HR': 21,
 'HU': 28,
 'IE': 22,
 'IL': 23,
 'IS': 26,
 'IT': 27,
 'LI': 21,
 'LT': 20,
 'LU': 20,
 'LV': 21,
 'MA': 24,
 'MC': 27,
 'ME': 22,
 'MK': 19,
 'MT': 31,
 'NL': 18,
 'NO': 15,
 'PL': 28,
 'PT': 25,
 'RO': 24,
 'RS': 22,
 'SE': 24,
 'SI': 19,
 'SK': 24,
 'SM': 27,
 'TN': 24,
 'TR': 26
}

if len(editor) != iban_len_dict.get(country_code, -1):
  return False

letter_code_dict = dict( zip(string.ascii_uppercase, range(10,36)) )

iban_code = ''.join([str(letter_code_dict.get(x, x))
                for x in bban + country_code + checksum])

try:
  iban_int = int(iban_code)
except ValueError:
  return False

return iban_int % 97 == 1
