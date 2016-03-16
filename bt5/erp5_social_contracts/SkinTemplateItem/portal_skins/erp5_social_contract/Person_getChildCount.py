child_count = 0

for child in context.Person_getFamilyRelatedPersonList() :
  if max_age == -1 or child.Person_getAge(year=1) <= max_age :
    child_count += 1

return child_count
