editor_list = [("Plain Text", "text_area")]

if getattr(context.portal_skins, "erp5_ace_editor", None) is not None:
  editor_list.append(("Ace Editor", "ace"))

if getattr(context.portal_skins, "erp5_code_mirror", None) is not None:
  editor_list.append(("Code Mirror", "codemirror"))

return editor_list
