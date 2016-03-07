skin_folder = getattr(context.portal_skins, skin_folder_id)

# Maybe this is a bit ugly, and lxml should be used
template = context.portal_skins.erp5_development.template_theme_web_main
template_source = template.document_src()
template_body_top, template_body_bottom = template_source.split("<!-- SPLIT -->")
new_code = context.ERP5Site_updateCodeWithMainContent(html_text, main_div_class_name)
new_code_0 = new_code.replace("<body>", template_body_top)
new_code_1 = new_code_0.replace("</body>", template_body_bottom)
new_code_2 = new_code_1.replace("'__REPLACE_CSS__'", css_tales)
final_code = new_code_2.replace("'__REPLACE_JS__'", js_tales)


skin_folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(main_template_id, "Default Template")
getattr(skin_folder, main_template_id).write(final_code)

return "OK"
