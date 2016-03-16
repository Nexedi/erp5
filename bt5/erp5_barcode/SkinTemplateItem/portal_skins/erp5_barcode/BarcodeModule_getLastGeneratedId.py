from string import zfill
return zfill(context.portal_ids.getLastGeneratedId(id_group='barcode'),12)
