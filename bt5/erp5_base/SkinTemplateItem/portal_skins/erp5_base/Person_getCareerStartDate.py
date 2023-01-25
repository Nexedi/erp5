all_career_step_list = context.contentValues(portal_type='Career',
                                             checked_permission='View')

career_step_list = []
# only keep "active" career steps (and related to this organisation if given)
for career_step in all_career_step_list :
  if (subordination_relative_url is None or \
      career_step.getSubordination() == subordination_relative_url) and \
     career_step.getStartDate() and \
     career_step.getValidationState() not in ('cancelled', 'deleted'):
    career_step_list.append(career_step)

# sort them by start date
career_step_list.sort(key=lambda x: x.getStartDate())
for career_step in career_step_list :
  # TODO: take the first date of the last active career range.
  # for now, we only return the first one.
  return career_step.getStartDate()

raise ValueError('No Career Step Defined.')
