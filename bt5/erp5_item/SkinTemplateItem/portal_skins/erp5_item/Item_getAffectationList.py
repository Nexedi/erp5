"""Helper script used by many scripts Item_get*(Value|Title) used for UI
It helps to improve consistency between all those scripts

 fallback_on_future: if True return future Tracking List if current Tracking List is empty
"""
portal = context.getPortalObject()

default_at_date = False
if at_date is None:
  default_at_date = True
  at_date = DateTime()

sql_kw = {'item': context.getRelativeUrl(),
          'at_date': at_date}

affectation_list = portal.portal_simulation.getCurrentTrackingList(**sql_kw)

if fallback_on_future and not affectation_list:
  if default_at_date:
    del sql_kw['at_date']
  affectation_list = portal.portal_simulation.getFutureTrackingList(**sql_kw)

return affectation_list
