from __future__ import division
from past.utils import old_div
initial_durability = kw.get('initial_durability')
if start_remaining_annuities is None or stop_remaining_annuities is None \
     or start_remaining_durability is None or stop_remaining_durability is None \
     or initial_durability is None:
  context.log('Error for actual use ratio calculation : one of theses properties is None : start_remaining_annuities : %s, stop_remaining_annuities : %s, start_remaining_durability : %s, stop_remaining_durability : %s, or initial_durability : %s' % (
     repr(start_remaining_annuities), repr(stop_remaining_annuities), repr(start_remaining_durability), repr(stop_remaining_durability), repr(initial_durability)),'')
  return None

consumpted_durability = start_remaining_durability - stop_remaining_durability
annuities_number = start_remaining_annuities - stop_remaining_annuities

try:
  per_annuity_consumption = (old_div(consumpted_durability, (annuities_number + 0.)))
  ratio = old_div(per_annuity_consumption, start_remaining_durability)
  return ratio
  #return ratio * start_remaining_durability / initial_durability
except ZeroDivisionError:
  return None
