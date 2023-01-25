"""
  This script will find applicable taxes for customer based on his/hers location.
  For example.
    - B2B in EU in same country, tax
    - B2B in EU in different country, no tax
    - B2B and B2P from EU to outside EU, no tax
    - B2P in EU, tax
"""

return {'VAT': {'translated_title':context.Base_translateString('VAT'),
                'percent': 20.,
               },
       }
