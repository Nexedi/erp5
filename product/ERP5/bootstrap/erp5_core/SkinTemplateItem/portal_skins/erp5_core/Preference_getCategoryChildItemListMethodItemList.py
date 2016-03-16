from Products.ERP5Type.Message import translateString

return [
   ('', ''),
   (translateString('Logical Path'), 'getCategoryChildTranslatedLogicalPathItemList', ),
   (translateString('Logical Compact Path'), 'getCategoryChildTranslatedCompactLogicalPathItemList', ),
   (translateString('Indented Title'), 'getCategoryChildTranslatedIndentedTitleItemList', ),
   (translateString('Indented Compact Title'), 'getCategoryChildTranslatedIndentedCompactTitleItemList', ),
]
