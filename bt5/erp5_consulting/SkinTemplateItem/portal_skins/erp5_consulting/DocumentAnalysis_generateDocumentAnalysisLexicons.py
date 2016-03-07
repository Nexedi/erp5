first_level_transformation = \
{ 'portal_type' : 'Document Analysis Lexicon'
, 'data_key'    : 'lexicon_title'
, 'data'        : [ { 'input_data_name' : 'lexicon_title'
                    , 'output_property' : 'title'
                    }
                  , { 'input_data_name' : 'lexicon_source_type'
                    , 'output_property' : 'lexicon_source_type'
                    }
                  ]
}

second_level_transformation = \
{ 'portal_type' : 'Document Analysis Lexicon Item'
, 'data_key'    : 'item_title'
, 'data'        : [ { 'input_data_name' : 'item_title'
                    , 'output_property' : 'title'
                    }
                  , { 'input_data_name' : 'item_description'
                    , 'output_property' : 'description'
                    }
                  , { 'input_data_name' : 'type'
                    , 'output_property' : 'lexicon_item_type'
                    }
                  , { 'input_data_name' : 'ubm'
                    , 'output_property' : 'lexicon_item_ubm'
                    }
                  , { 'input_data_name' : 'class'
                    , 'output_property' : 'item_class'
                    }
                  , { 'input_data_name' : 'propertysheet'
                    , 'output_property' : 'item_property_sheet'
                    }
                  ]
}

fast_input_transformation_rules = [first_level_transformation, second_level_transformation]

context.FastInput_generateTwoLevelObjectStructure( transformation_rules = fast_input_transformation_rules
                                                 , listbox = listbox
                                                 , destination = context.getObject())
