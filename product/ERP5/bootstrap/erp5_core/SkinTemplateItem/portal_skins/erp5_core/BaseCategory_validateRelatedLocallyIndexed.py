return not (value and (
  request.other['field_my_acquisition_object_id_list'] or
  request.other['field_my_acquisition_base_category_list']))
