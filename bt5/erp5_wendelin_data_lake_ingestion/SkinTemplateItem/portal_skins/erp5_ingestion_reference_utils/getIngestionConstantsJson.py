import json
portal = context.getPortalObject()
dict = {'invalid_suffix':portal.getIngestionReferenceDictionary()['invalid_suffix'],
        'split_end_suffix':portal.getIngestionReferenceDictionary()['split_end_suffix'],
        'single_end_suffix':portal.getIngestionReferenceDictionary()['single_end_suffix'],
        'split_first_suffix':portal.getIngestionReferenceDictionary()['split_first_suffix'],
        'none_extension':portal.getIngestionReferenceDictionary()['none_extension'],
        'reference_separator':portal.getIngestionReferenceDictionary()['reference_separator'],
        'complex_files_extensions':portal.getIngestionReferenceDictionary()['complex_files_extensions'],
        'reference_length':portal.getIngestionReferenceDictionary()['reference_length'],
        'invalid_chars':portal.getIngestionReferenceDictionary()['invalid_chars'],
        }
return json.dumps(dict)
