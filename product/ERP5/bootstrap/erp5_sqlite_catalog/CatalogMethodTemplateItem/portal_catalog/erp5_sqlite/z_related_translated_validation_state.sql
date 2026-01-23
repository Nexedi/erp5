<dtml-var table_0>.original_message = catalog.validation_state
 AND <dtml-var table_0>.message_context = "validation_state"
 AND <dtml-var table_0>.portal_type = catalog.portal_type
 AND <dtml-var table_0>.language = <dtml-sqlvar "Localizer.get_selected_language()" type="string">