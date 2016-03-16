# Retrieve the last counter date for a given date

from DateTime import DateTime
if start_date is None:
  start_date = DateTime()

counter_date_list = context.portal_catalog(portal_type='Counter Date', 
                site_uid=site_uid, 
                start_date={'query':start_date,'range':'ngt'},
                sort_on=[('start_date','descending')], limit=1)
counter_date = None
if len(counter_date_list)==1:
  counter_date = counter_date_list[0]
return counter_date
