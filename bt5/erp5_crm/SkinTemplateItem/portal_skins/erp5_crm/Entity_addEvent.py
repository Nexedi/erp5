from erp5.component.module.Log import log
log('Obsoleted, please use Base_addEvent (with Base_viewAddEventDialog) instead')
return context.Base_addEvent(title, direction, portal_type, resource, **kw)
