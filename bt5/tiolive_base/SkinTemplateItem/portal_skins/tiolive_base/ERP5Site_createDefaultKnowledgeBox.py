#
# Advertisement and something for beginners should be added by default.
#
knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='portal_gadgets/erp5_advertisement',
  activate_kw = activate_kw)
knowledge_box.visible()

# Documentation Gadget
knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='portal_gadgets/erp5_documentation',
  activate_kw=activate_kw)
knowledge_box.visible()

# Put gadgets side by side by default.
# XXX Not so frendly. 
knowledge_pad.edit(user_layout="1##2##")
