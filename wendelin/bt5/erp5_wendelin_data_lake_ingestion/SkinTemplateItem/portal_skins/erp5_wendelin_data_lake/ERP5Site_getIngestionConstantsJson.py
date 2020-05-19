import json
portal = context.getPortalObject()
dict = {'invalid_suffix':portal.ERP5Site_getIngestionReferenceDictionary()['invalid_suffix'],
        'split_end_suffix':portal.ERP5Site_getIngestionReferenceDictionary()['split_end_suffix'],
        'single_end_suffix':portal.ERP5Site_getIngestionReferenceDictionary()['single_end_suffix'],
        'split_first_suffix':portal.ERP5Site_getIngestionReferenceDictionary()['split_first_suffix'],
        'none_extension':portal.ERP5Site_getIngestionReferenceDictionary()['none_extension'],
        'reference_separator':portal.ERP5Site_getIngestionReferenceDictionary()['reference_separator'],
        'complex_files_extensions':portal.ERP5Site_getIngestionReferenceDictionary()['complex_files_extensions'],
        'reference_length':portal.ERP5Site_getIngestionReferenceDictionary()['reference_length'],
        'invalid_chars':portal.ERP5Site_getIngestionReferenceDictionary()['invalid_chars'],
        }
return json.dumps(dict)
