##parameters=setup_list

# Example code:

# Import a standard function, and get the HTML request and response objects.
from random import randrange

random_list0 = []
random_list1 = []

for (key, value) in setup_list:
 if value == 0.0:
   if randrange(0,2) == 0:
     random_list0 = random_list0 + [(key , value)]
   else:
     random_list0 = [(key , value)] + random_list0
 else:
     random_list1 =  random_list1 + [(key , value)]

return random_list0 + random_list1