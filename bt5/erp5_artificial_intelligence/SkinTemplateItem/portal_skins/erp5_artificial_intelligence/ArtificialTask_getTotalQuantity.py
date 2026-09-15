"""Answer the total of the tokens of one Artificial Task.

One Artificial Task Report points at one Artificial Task with the base
category `follow_up`. One Artificial Task can hold more than one report.
The script reads every related report. The script adds the total of each
report.

The script calls `ArtificialTaskReport_getTotalQuantity` on each report.
That script holds the one definition of the token total. This script
adds no second definition.

The script answers one float. The script answers 0.0 when no report
points at this Artificial Task.

PARAMETER LIST: empty. This script takes no parameter.
"""
REPORT_PORTAL_TYPE = 'Artificial Task Report'

total = 0.0
for report in context.getFollowUpRelatedValueList(
    portal_type=REPORT_PORTAL_TYPE):
  total = total + float(report.ArtificialTaskReport_getTotalQuantity())

return total
