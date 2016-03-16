"""
 This script is part of ERP5 Web.
 It is used to get title of an object published in an ERP5 based Web Site and is used
 for building ERP5 Web UI.

 Title can be acquired from following sources (their priority may depend):
 - translated_short_title
 - short_title
 - translated_title_or_id
 - title_or_id
 - title
 - auto generated

  XXX: move this script as an API of ERP5Type?
"""
return context.getProperty('translated_short_title', None) or \
                   context.getProperty('short_title', None) or \
                   context.getProperty('translated_title_or_id', None) or \
                   context.getProperty('title_or_id', None) or \
                   context.title
