import string
from random import choice
from six.moves import range

test_suite = state_change['object']
portal = test_suite.getPortalObject()

def int2letter(i):
  """Convert an integer to letters, to use as a grouping reference code.
  A, B, C ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, AAA ...
  """
  if i < 26:
    return (chr(i + ord('a')))
  d, m = divmod(i, 26)
  return int2letter(d - 1) + int2letter(m)

if test_suite.getReference() is None:
  new_id = portal.portal_ids.generateNewId(id_generator="uid", id_group="test_suite_reference")
  test_suite.setReference(int2letter(new_id))

def generateRandomString(size):
  tab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  my_string = ''
  for _ in range(size):
    my_string = my_string + choice(tab)
  return my_string

if test_suite.getPortalType() == "Scalability Test Suite":
  random_path = test_suite.getReference() + "_" + generateRandomString(64)
  test_suite.setRandomizedPath(random_path)

test_suite.TestDocument_optimize()
