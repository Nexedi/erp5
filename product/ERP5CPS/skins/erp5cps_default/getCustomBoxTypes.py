## Script (Python) "getCustomBoxTypes"
##parameters=
# $Id$
"""Return custom  box types."""

items = [
    {'category': 'basebox',
     'title': 'portal_type_BaseBox_title',
     'desc': 'portal_type_BaseBox_description',
     'types': [{'provider': 'erp5cps',
                'id': 'header',
                'desc': 'Entête ERP5'},
                ,
               ]
     },

    ]

return items
