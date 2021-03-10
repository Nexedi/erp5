configuration_save_url = kw.get('configuration_save_url', None)
preferred_event_sender_email = kw.get('preferred_event_sender_email', '')
preferred_date_order = kw.get('preferred_date_order', None)
preferred_language_list = kw.get('lang', [])

configuration_save = context.restrictedTraverse(configuration_save_url)

# if preferred email is not specified used previously saved company email.
company_email = context.getGlobalConfigurationAttr('company_email')
if preferred_event_sender_email in ('', None,):
  preferred_event_sender_email = company_email

# price currency contains all currency info like iso code& precision ';'
# separated
currency_info = kw['price_currency']
currency_reference, currency_base_unit_quantity, currency_title  = \
    currency_info.split(';')
configuration_save.addConfigurationItem(
    "Currency Configurator Item",
    reference = currency_reference,
    base_unit_quantity = currency_base_unit_quantity,
    title = currency_title,)
context.setGlobalConfigurationAttr(default_currency=currency_reference)

# adjust price_currency for organisation configuration item
organisation_configurator_item = context.getGlobalConfigurationAttr(
    'organisation_configurator_item')
organisation_configurator_item_obj = context.restrictedTraverse(
    organisation_configurator_item, None)
organisation_configurator_item_obj.setPriceCurrency(currency_reference)

# CRM
# Create services used in crm preference.
# XXX I think here is not a good place.(yusei)
service_list = (
  # sale opportunity
  ('product', dict(title='Product', use='crm/sale_opportunity', )),
  ('service', dict(title='Service', use='crm/sale_opportunity', )),
  # campaign
  ('marketing_campaign', dict(title='Marketing Campaign', use='crm/campaign', )),
  ('marketing_survey', dict(title='Market Survey', use='crm/campaign', )),
  ('marketing_purchases', dict(title='Purchases Campaign', use='crm/campaign', )),
  ('marketing_sales', dict(title='Sales Campaign', use='crm/campaign', )),
  ('marketing_other', dict(title='Other Marketing Service', use='crm/campaign', )),
  # support request
  ('support_administrative', dict(title='Administrative Support', use='crm/support_request', )),
  ('support_financial', dict(title='Financial Support', use='crm/support_request', )),
  ('support_it', dict(title='IT Support', use='crm/support_request', )),
  ('support_other', dict(title='Other Support Service', use='crm/support_request', )),
  # meeting
  ('organisation_conference', dict(title='Conference', use='crm/meeting', )),
  ('organisation_partnership', dict(title='Partnership Meeting', use='crm/meeting', )),
  ('organisation_purchases', dict(title='Purchases Meeting', use='crm/meeting', )),
  ('organisation_project', dict(title='Project Meeting', use='crm/meeting', )),
  ('organisation_sales', dict(title='Sales Meeting', use='crm/meeting', )),
  ('organisation_other', dict(title='Other Meeting', use='crm/meeting', )),
  # event
  ('event_complaint', dict(title='Complaint', use='crm/event', )),
  ('event_announcement', dict(title='Announcement', use='crm/event', )),
  ('event_inquiry', dict(title='Inquiry', use='crm/event', )),
  ('event_advertisement', dict(title='Advertisement', use='crm/event', )),
  ('event_spam', dict(title='Spam', use='crm/event', )),
  ('event_information', dict(title='Information', use='crm/event', )),
  ('event_other', dict(title='Other event', use='crm/event', )),
  )
configuration_save.addConfigurationItem("Service Configurator Item",
                                        configuration_list=service_list)

# configure preferences
prefs = dict(
  # UI
  preferred_category_child_item_list_method_id =
                   'getCategoryChildTranslatedLogicalPathItemList',
  preferred_text_format = 'text/html',
  preferred_text_editor = 'fck_editor',
  preferred_date_order = preferred_date_order,
  preferred_listbox_view_mode_line_count = 20,
  preferred_listbox_list_mode_line_count = 20,
  preferred_string_field_width = 30,
  preferred_textarea_width = 80,
  preferred_textarea_height = 5,
  preferred_report_style = 'ODT',
  preferred_report_format = 'pdf',
  preferred_money_quantity_field_width = 10, # TODO: adapt this
                                             # based on the selected
                                             # currency, XOF needs
                                             # more than 10 for
                                             # example
  preferred_html_style_access_tab = 1,
  preferred_quantity_field_width = 8,
  # accounting
  preferred_accounting_transaction_currency = 'currency_module/%s' % \
      currency_reference,
)

configuration_save.addConfigurationItem(
    'Preference Configurator Item',
    object_id = 'default_configurator_preference',
    description = "The default parameters for the site are set on this "
    "preference",
    title = "Default Configurator Site Preference",
    **prefs)

# configure system preferences
# some preparation
system_prefs = dict(
  # CRM
  preferred_campaign_use_list = ['use/crm/campaign'],
  preferred_event_use_list = ['use/crm/event'],
  preferred_meeting_use_list = ['use/crm/meeting'],
  preferred_sale_opportunity_use_list = ['use/crm/sale_opportunity'],
  preferred_support_request_use_list = ['use/crm/support_request'],
  preferred_event_sender_email = preferred_event_sender_email,
  preferred_event_assessment_form_id_list = [],
  # DMS
  # XXX-Luke: (proposal) Allow to define, maybe use some magic of
  #           representation
  preferred_document_file_name_regular_expression = \
      '(?P<node_reference>[a-zA-Z0-9_-]+)-(?P<local_reference>[a-zA-Z0-9_.]+)'
      '-(?P<version>[0-9a-zA-Z.]+)-(?P<language>[a-z]{2})[^-]*?',
  preferred_document_reference_regular_expression = '(?P<reference>[a-zA-Z0-9'
      '-_.]+-[a-zA-Z0-9-_.]+)(|-(?P<version>[0-9a-zA-Z.]+))(|-(?P<language>[a'
      '-z]{2})[^-]*)?',
  preferred_document_classification = 'collaborative/team',
  preferred_synchronous_metadata_discovery = True,
  preferred_redirect_to_document = True,
  # PDM
  preferred_product_individual_variation_base_category_list = ['variation'],
  preferred_component_individual_variation_base_category_list = ['variation'],
  preferred_service_individual_variation_base_category_list = ['variation'],
  # trade
  preferred_supplier_role_list = ['role/supplier'],
  preferred_client_role_list = ['role/client'],
  preferred_sale_use_list = ['use/trade/sale'],
  preferred_purchase_use_list = ['use/trade/purchase'],
  preferred_packing_use_list = ['use/trade/container'],
  preferred_tax_use_list=['use/trade/tax'],
  preferred_price_ratio_use_list=['use/trade/tax'])

configuration_save.addConfigurationItem(
    'System Preference Configurator Item',
    object_id = 'default_configurator_system_preference',
    description="The default system parameters for the site are set on this "\
    "preference",
    title="Default Configurator System Site Preference",
    **system_prefs)

# preferred_languages
for bt5_id in preferred_language_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          bt5_id=bt5_id)
