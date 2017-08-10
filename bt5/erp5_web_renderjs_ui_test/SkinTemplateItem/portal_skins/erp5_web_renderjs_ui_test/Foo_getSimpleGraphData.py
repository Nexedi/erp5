import json
data = {"data": [{ "value_dict": {0: ["2016-02-01", "2016-02-02", "2016-02-03", "2016-02-04"],
                                   1: [0, 1, 3, 2]},
                      "type": "line",
                      "title": "Value"
                   },
                   { "value_dict": {0: ["2016-02-01", "2016-02-02", "2016-02-03", "2016-02-04"],
                                   1: [1, 2, 4, 3]},
                      "type": "line",
                      "title": "Value2"
                   }],
             "layout": {"axis_dict" : {0: {"title": "date", "value_type": "date"},
                              1: {"title": "value"}
                             },
                     "title": "Simple Graph"}
            }
return json.dumps(data)
