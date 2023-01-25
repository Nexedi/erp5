from Products.ERP5Type.Message import translateString
portal_type_list = ['Internal Packing List' ,
                    'Sale Order',
                    'Sale Packing List',
                    'Purchase Order',
                    'Purchase Packing List']

return [('', '')] + [(translateString(x), x) for x in portal_type_list ]
