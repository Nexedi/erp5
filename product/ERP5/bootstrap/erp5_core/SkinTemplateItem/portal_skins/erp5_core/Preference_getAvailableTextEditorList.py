text_editor_list = [("Plain Text", "text_area"), ("FCK Editor", "fck_editor")]

if getattr(context.portal_skins, "erp5_ace_editor", None) is not None:
  text_editor_list.append(("Ace Editor", "ace"))

if getattr(context.portal_skins, "erp5_code_mirror", None) is not None:
  text_editor_list.append(("Code Mirror", "codemirror"))

if getattr(context.portal_skins, "erp5_monaco_editor", None) is not None:
  text_editor_list.append(("Monaco Editor", "monaco"))

return text_editor_list
