default_inventory_calculation_list = ({ "inventory_params" : {"payment_uid" : context.getDestinationPaymentUid(),
                                                                      "group_by_resource" : 1,
                                                                      },
                                        "list_method" : "getMovementList",
                                        "first_level" : ({'key' : 'resource_relative_url',
                                                          'getter' : 'getResource',
                                                          'setter' : ("appendToCategoryList", "resource")},
                                                         ),
                                        },
                                      )

return default_inventory_calculation_list
