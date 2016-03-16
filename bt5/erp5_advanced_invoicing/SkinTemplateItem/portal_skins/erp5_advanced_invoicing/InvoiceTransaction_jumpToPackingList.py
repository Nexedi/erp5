# string:${object_url}/Base_jumpToRelatedObject?base_category=causality&related:int=0&portal_type=Sale+Packing+List

invoice = context.getCausalityValue(portal_type=invoice_type)
invoice.Base_jumpToRelatedObject(base_category=base_category, related=related, portal_type=portal_type)
