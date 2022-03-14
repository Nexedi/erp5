/*global window, RSVP, FileReader, QueryFactory, SimpleQuery, ComplexQuery, Query */
/*jslint indent: 2, maxerr: 3, unparam: true */
(function (window, RSVP) {
  "use strict";

  window.getWorkflowState = function (options)  {
    var sync_state,
      readonly = false;
    if(options.jio_key.indexOf("_module/") > 0){
      sync_state = "Synced";
      readonly = true;
    }else if(options.doc.sync_flag){
      sync_state = "Not Synced";
      if (options.doc.state) {
        readonly = true;
      }
    }else{
      sync_state = "Not Ready To Sync";
    }
    return {sync_state: sync_state, readonly: readonly};
  };
  
  window.geoLocationPromise = function() {
    return new Promise(function (resolve, reject) {
      var err;
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (result) {
          resolve(result);
        }, function (error) {
          switch(error.code) {
            case error.PERMISSION_DENIED:
              err = new Error("User denied the request for Geolocation");
              break;
            case error.POSITION_UNAVAILABLE:
              err =  new Error("Location information is unavailable");
              break;
            case error.TIMEOUT:
              err = new Error("The request to get user location timed out");
              break;
            default:
              err = new Error("An unknown error occurred");
              break;
          }
          reject(err);
        },
        {maximumAge:60000, timeout:20000});
      } else {
        reject(new Error("Geolocation is not supported by this browser"));
    }
    });
  };
  window.getSequentialID = function (gadget, record_type_prefix){
    var last_sequential_id,
      prefix,
      date = new Date(),
      date_text = date.getFullYear()+('0'+(date.getMonth()+1)).slice(-2)+('0'+date.getDate()).slice(-2);
    return new RSVP.Queue()
      .push(function () {
        if (gadget.options.doc.source_reference) {
          return gadget.options.doc.source_reference;
        } else {
          return new RSVP.Queue()
            .push(function () {
              return new RSVP.all([
                gadget.getSetting('last_sequential_id'),
                gadget.getSetting('sequential_id_prefix')
              ]);
            })
           .push(function (result_list) {
             if (result_list[0]) {
              last_sequential_id = Number(result_list[0]);
             } else {
              last_sequential_id = 0;
             }
            last_sequential_id += 1;
            if (result_list[1]) {
              prefix = result_list[1];
            } else {
             prefix = getRandomPrefixForID();
            }
            return gadget.setSetting('sequential_id_prefix', prefix);
           })
           .push(function () {
             return gadget.setSetting('last_sequential_id', last_sequential_id);
           })
          .push(function () {
           return record_type_prefix + '-' + date_text + '-' + prefix + ('0000'+last_sequential_id).slice(-5);
          });
        }
      });
  };
  
  window.getRandomPrefixForID = function(){
    function random(){
      return 65 + Math.floor( Math.random() * 26 );
    }
    return String.fromCharCode(random())+String.fromCharCode(random())+String.fromCharCode(random());
  };
  
  window.getSynchronizeQuery = function (additional_query_list) {
    var basic_query,
      expense_record_query,
      travel_request_record_query,
      leave_report_record_query,
      leave_request_record_query,
      localisation_record_query,
      expense_sheet_query,
      currency_query,
      six_month_ago,
      one_year_ago;
    six_month_ago =  new Date();
    six_month_ago.setMonth(six_month_ago.getMonth() - 6);
    six_month_ago = six_month_ago.toISOString().slice(0, 10).replace(/-/g, "/");
    one_year_ago = new Date();
    one_year_ago.setFullYear(one_year_ago.getFullYear() - 1);
    one_year_ago = one_year_ago.toISOString().slice(0, 10).replace(/-/g, "/");
    expense_record_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Expense Record'
        }),
        new SimpleQuery({
          key: 'modification_date',
          operator: '>',
          type: "simple",
          value: six_month_ago
        }),
        new ComplexQuery({
          operator: 'OR',
          query_list: [
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "draft"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "sent"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "stopped"
            })
          ],
          type: "complex"
        })
      ],
      type: "complex"
    });

    travel_request_record_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Travel Request Record'
        }),
        new SimpleQuery({
          key: 'modification_date',
          operator: '>',
          type: "simple",
          value: six_month_ago
        }),
        new ComplexQuery({
          operator: 'OR',
          query_list: [
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "draft"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "sent"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "stopped"
            })
          ],
          type: "complex"
        })
      ],
      type: "complex"
    });

    leave_report_record_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Leave Report Record'
        }),
        new SimpleQuery({
          key: 'modification_date',
          operator: '>',
          type: "simple",
          value: six_month_ago
        }),
        new SimpleQuery({
          key: 'simulation_state',
          operator: '',
          type: "simple",
          value: "stopped"
        })
      ],
      type: "complex"
    });

    leave_request_record_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Leave Request Record'
        }),
        new SimpleQuery({
          key: 'modification_date',
          operator: '>',
          type: "simple",
          value: one_year_ago
        }),
        new ComplexQuery({
          operator: 'OR',
          query_list: [
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "draft"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "sent"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "stopped"
            })
          ],
          type: "complex"
        })

      ],
      type: "complex"
    });

    localisation_record_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Localisation Record'
        }),
        new SimpleQuery({
          key: 'modification_date',
          operator: '>',
          type: "simple",
          value: six_month_ago
        }),
        new ComplexQuery({
          operator: 'OR',
          query_list: [
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "draft"
            }),
            new SimpleQuery({
              key: 'simulation_state',
              operator: '',
              type: "simple",
              value: "stopped"
            })
          ],
          type: "complex"
        })
      ],
      type: "complex"
    });

    expense_sheet_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Expense Sheet'
        }),
        new SimpleQuery({
          key: 'reference',
          operator: '',
          type: "simple",
          value: "expense_sheet"
        })
      ],
      type: "complex"
    });

    currency_query = new ComplexQuery({
      operator: 'AND',
      query_list: [
        new SimpleQuery({
          key: 'portal_type',
          operator: '',
          type: "simple",
          value: 'Currency'
        }),
        new SimpleQuery({
          key: 'validation_state',
          operator: '',
          type: "simple",
          value: "validated"
        })
      ],
      type: "complex"
    });

    basic_query = new ComplexQuery({
      operator: 'OR',
      type: 'complex',
      query_list: [
        expense_record_query,
        travel_request_record_query,
        leave_report_record_query,
        leave_request_record_query,
        localisation_record_query,
        expense_sheet_query,
        currency_query
      ]
    });
    if (additional_query_list) {
      basic_query.query_list = basic_query.query_list.concat(additional_query_list);
    }
    return Query.objectToSearchText(basic_query);
  };

}(window, RSVP));