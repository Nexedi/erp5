first_level_transformation = \
{ 'portal_type' : 'Document Analysis Document'
, 'data_key'    : 'document_title'
, 'data'        : [ { 'input_data_name' : 'document_title'
                    , 'output_property' : 'title'
                    }
                  , { 'input_data_name' : 'document_analysis_document_type'
                    , 'output_property' : 'document_analysis_document_type'
                    }
                  ]
}

second_level_transformation = \
{ 'portal_type' : 'Document Analysis Document Item'
, 'data_key'    : 'item_title'
, 'data'        : [ { 'input_data_name' : 'item_title'
                    , 'output_property' : 'title'
                    }
                  , { 'input_data_name' : 'item_description'
                    , 'output_property' : 'description'
                    }
                  ]
}

fast_input_transformation_rules = [first_level_transformation, second_level_transformation]

context.FastInput_generateTwoLevelObjectStructure( transformation_rules = fast_input_transformation_rules
                                                 , listbox = listbox
                                                 , destination = context.getObject())
