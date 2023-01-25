configuration_save = context.restrictedTraverse(configuration_save_url)

# business processes
configuration_save.addConfigurationItem("Business Process Configurator Item",
                         title="Default Trade Business Process" ,
                         configuration_spreadsheet_data = getattr(context, "standard_business_process.ods").data,
                         reference="default_erp5_business_process")

configuration_save.addConfigurationItem("Business Process Configurator Item",
                         title="Default Sales Business Process" ,
                         configuration_spreadsheet_data = getattr(context, "standard_sale_business_process.ods").data,
                         reference="default_erp5_sale_business_process")

configuration_save.addConfigurationItem("Business Process Configurator Item",
                         title="Default Purchase Business Process" ,
                         configuration_spreadsheet_data = getattr(context, "standard_purchase_business_process.ods").data,
                         reference="default_erp5_purchase_business_process")

# setup Sale Trade Condition
configuration_save.addConfigurationItem("Sale Trade Condition Configurator Item",
                                         title="General Sale Trade Condition",
                                         reference="STC-General")

# setup Purchase Trade Condition
configuration_save.addConfigurationItem("Purchase Trade Condition Configurator Item",
                                         title="General Purchase Trade Condition",
                                         reference="PTC-General")

rule_simulation_list = context.ConfigurationTemplate_readOOCalcFile("standard_simulation_rule.ods",
                          data=getattr(context,'standard_simulation_rule.ods').data)

for rule_dict in rule_simulation_list:
  configuration_save.addConfigurationItem("Rule Configurator Item",
                                          id = rule_dict['rule_template_id'],
                                          reference = rule_dict['reference'],
                                          trade_phase = rule_dict['trade_phase'])

# Create alarms to launch builders.
configuration_save.addConfigurationItem("Alarm Configurator Item",
                             title="Invoice Builder Alarm",
                             id="invoice_builder_alarm",
                             periodicity_minute_frequency=5,
                             # A clever solution should be provided for the script
                             # bellow
                             active_sense_method_id="Alarm_buildConfiguratorStandardInvoice")

configuration_save.addConfigurationItem("Alarm Configurator Item",
                             title="Packing List Builder Alarm",
                             id="packing_list_builder_alarm",
                             periodicity_minute_frequency=5,
                             # A clever solution should be provided for the script
                             # bellow
                             active_sense_method_id="Alarm_buildConfiguratorStandardPackingList")
