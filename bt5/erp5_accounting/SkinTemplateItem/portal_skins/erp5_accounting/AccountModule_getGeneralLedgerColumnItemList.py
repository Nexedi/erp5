return (
  ('Movement_getNodeGapId', 'Account Code'),
  ('node_translated_title', 'Account Name'),
  ('Movement_getNodeFinancialSectionTitle', 'Financial Section'),
  ('section_title', 'Section'),
  ('mirror_section_title', 'Third Party'),
  ('date', 'Operation Date'),
  ('modification_date', 'Modification Date'),
  ('Movement_getSpecificReference', 'Transaction Reference'),
  ('Movement_getExplanationTranslatedPortalType', 'Type'),
  ('Movement_getExplanationTitle', 'Title'),
  ('Movement_getExplanationReference', 'Document Reference'),
) + context.accounting_module.AccountModule_getAnalyticColumnList() + (
  ('debit_price', 'Debit'),
  ('credit_price', 'Credit'),
  ('total_price', 'Balance'),
  ('Movement_getSectionPriceCurrency', 'Accounting Currency'),
  
  ('debit', 'Transaction Currency Debit'),
  ('credit', 'Transaction Currency Credit'),
  ('total_quantity', 'Transaction Currency Balance'),
  ('resource_reference', 'Transaction Currency'),
  
  ('Movement_getPaymentTitle', 'Section Bank Account',),
  ('payment_mode_translated_title', 'Payment Mode',),
  
  ('grouping_reference', 'Grouping Reference'),
  ('grouping_date', 'Grouping Date'),
  ('getTranslatedSimulationStateTitle', 'State'),
)
