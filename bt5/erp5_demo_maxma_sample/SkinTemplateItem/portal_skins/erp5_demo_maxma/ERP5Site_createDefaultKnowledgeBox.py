knowledge_pad.setTitle("Home")
knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='specialise/portal_gadgets/erp5_gadget_best_seller_products',
  mode='total_price',
  section_category='group/my_group',
  activate_kw = activate_kw)
knowledge_box.visible()
knowledge_box.setProperty('method','getCurrentInventoryList')

knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='specialise/portal_gadgets/erp5_gadget_contact_person',
  activate_kw = activate_kw)
knowledge_box.visible()

# Documentation Gadget
knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='specialise/portal_gadgets/erp5_gadget_events',
  activate_kw=activate_kw)
knowledge_box.visible()

# Documentation Gadget
knowledge_box = knowledge_pad.newContent(
  portal_type='Knowledge Box',
  specialise='specialise/portal_gadgets/erp5_gadget_new_sale_opportunity',
  activate_kw=activate_kw)
knowledge_box.visible()

knowledge_pad.edit(user_layout="1##3|2##4")
