from Products.ERP5Type.DateUtils import atTheEndOfPeriod
return atTheEndOfPeriod(context.getStopDate(), 'month') - 1
