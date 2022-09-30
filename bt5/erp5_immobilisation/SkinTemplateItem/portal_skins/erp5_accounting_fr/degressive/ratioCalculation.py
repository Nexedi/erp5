if initial_remaining_annuities is None or current_annuity is None:
  context.log('Error in degressive ratioCalculation :',
            'initial_remaining_annuities (%s) or current_annuity (%s) is None' % (initial_remaining_annuities, current_annuity))
  return None
degressive_coef = kw.get('initial_degressive_coefficient', None)
if not degressive_coef:
  context.log('Error in degressive ratioCalculation :',
            'initial_degressive_coefficient (%s) is None or 0' % degressive_coef)
  return None


# Calculate the ratio for each annuity
annuity_ratio_list = []
first_linear_ratio = 1./initial_remaining_annuities
degressive_ratio = first_linear_ratio * degressive_coef

for i in range(int(initial_remaining_annuities)):
  linear_ratio = 1. / (initial_remaining_annuities - i)
  applied_ratio = max(linear_ratio, degressive_ratio)
  annuity_ratio_list.append(applied_ratio)

try:
  return annuity_ratio_list[current_annuity]
except IndexError:
  context.log('Error in degressive ratioCalculation :',
              'current_annuity (%s) exceeds initial_remaining_annuities (%s)' % (current_annuity, initial_remaining_annuities))
  return None
