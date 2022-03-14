"""
Script used by PlanningBox validator to round the bound dates to the
closest full minute.
"""
from __future__ import division

from past.utils import old_div
if full_date.second() > 30:
  # plus one Minute
  return DateTime(full_date.strftime("%Y/%m/%d %H:%M")) + old_div((1.0/24),60)
else:
  return DateTime(full_date.strftime("%Y/%m/%d %H:%M"))
