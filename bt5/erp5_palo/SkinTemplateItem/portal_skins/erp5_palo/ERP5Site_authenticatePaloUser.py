from DateTime import DateTime
from Products.ERP5Security.ERP5UserManager import getUserByLogin

person_list = getUserByLogin(context, login)
if not person_list:
  return False, []

person = person_list[0]
if person.getPassword(format='palo_md5') != password:
  return False, []

now = DateTime()
group_set = set()
for assignment in person.contentValues(portal_type='Assignment'):
  if assignment.getValidationState() == 'open' and (
    assignment.getStartDate() is None or
    assignment.getStartDate() <= now <= assignment.getStopDate()):

    # XXX below is sample implementation, as it must match the groups defined in PALO
    if assignment.isMemberOf("function/palo"):
      group_set.add(assignment.getGroupReference())

    if assignment.isMemberOf("function/palo_admin"):
      group_set.add("admin")

return True, list(group_set)
