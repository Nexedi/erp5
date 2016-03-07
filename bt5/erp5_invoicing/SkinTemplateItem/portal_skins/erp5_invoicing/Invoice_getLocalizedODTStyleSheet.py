current_language = context.Localizer.get_selected_language()
localized_style_sheet_name = "%s_l10n_%s" % (parameter, current_language)
localized_style_sheet = getattr(context, localized_style_sheet_name, None)
if localized_style_sheet is not None:
  return localized_style_sheet
else:
  return getattr(context, parameter)
