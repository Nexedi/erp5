# XXX for now, we always use the default Base_getODSStyleSheet
# we use to have Base_getODSListStyleSheet with a line at the bottom of
# the page, for better print display and also Base_getODSStyleSheetLandscape
# when landscape mode is used.
# Now we rather agreed that ods_style is a style for export, not report and
# the rendering appearance was not so important.
return context.Base_getODSStyleSheet
