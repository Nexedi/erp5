first_level_transformation = \
{ 'portal_type' : 'Document Analysis Document'
, 'primary_key' : 'document_title'
, 'data'        : [ { 'input_data_name' : 'document_title'
                    , 'output_property' : 'title'
                    , 'required' : True
                    }
                  , { 'input_data_name' : 'document_analysis_document_type'
                    , 'output_property' : 'document_analysis_document_type'
                    , 'required' : False
                    }
                  ]
}

second_level_transformation = \
{ 'portal_type' : 'Document Analysis Document Item'
, 'primary_key' : 'item_title'
, 'data'        : [ { 'input_data_name' : 'item_title'
                    , 'output_property' : 'title'
                    , 'required' : True
                    }
                  , { 'input_data_name' : 'item_description'
                    , 'output_property' : 'description'
                    , 'required' : False
                    }
                  ]
}

fast_input_transformation_rules = [first_level_transformation, second_level_transformation]

return context.FastInput_generateObjectStructure( transformation_rules = fast_input_transformation_rules
                                                 , listbox = listbox
                                                 , destination = context.getObject())
