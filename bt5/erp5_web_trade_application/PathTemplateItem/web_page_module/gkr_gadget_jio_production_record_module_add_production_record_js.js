/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".new-production-record-template")
                              .innerHTML,
    template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod('get', 'jio_get')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;

      return gadget.translateHtml(template({
        date: new Date().toISOString().split('T')[0]
      }))
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          $(gadget.props.element.querySelectorAll('fieldset')).hide()
          $(gadget.props.element.querySelector('fieldset[name=line1]')).show()
          return gadget.updateHeader({
            title: "New Production Record"
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('form.new-production-record-form'),
            'submit',
            false
          );
        })
        .push(function (submit_event) {
          var i,
            doc = {
              // XXX Hardcoded
              parent_relative_url: "production_record_module",
              portal_type: "Production Record",
              doc_id: getSequentialID('PRR'),
              local_validation: "self",
              record_revision: 1,
            };
          gadget.props.element.querySelector("input[type=submit]")
                              .disabled = true;

          for (i = 0; i < submit_event.target.length; i += 1) {
            // XXX Should check input type instead
            if (submit_event.target[i].name) {
              if ((submit_event.target[i].type == "radio" || submit_event.target[i].type == "checkbox") && !submit_event.target[i].checked){
                continue
              }
              if (submit_event.target[i].tagName == "FIELDSET"){
                continue
              }
              if (submit_event.target[i].name == "add_line"){
                continue
              }
              doc[submit_event.target[i].name] = submit_event.target[i].value;
            }
          }

          if (doc.sync_flag != "1"){
            doc.portal_type = 'Production Record Temp' // For to avoid sync
          }

          return gadget.post(doc);
        })
        .push(function () {
          return gadget.redirect({
            jio_key: gadget.props.options.jio_key,
            page: "view"
          });
        });

    })


    /////////////////////////////////////////
    // Fill currencies
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function(){createPriceCurrencySelection(gadget, my_price_currency)})
    })


    /////////////////////////////////////////
    // Fill quantity unit categories
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "quantity_unit/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var option_array = new Array();
          for (var i = 0; i < result.data.total_rows; i += 1) {
            option_array[i] = {text:result.data.rows[i].value.logical_path || result.data.rows[i].value.title,
                               value:result.data.rows[i].value.category_relative_url}
          }
          createOptions(gadget.props.element.querySelector('[name="quantity_unit"]'), option_array, 'weight/kg')
          createOptions(gadget.props.element.querySelector('[name="quantity_unit2"]'), option_array, 'weight/kg')
          createOptions(gadget.props.element.querySelector('[name="quantity_unit3"]'), option_array, 'weight/kg')
          for(i=1; i <= 10; i++){
            createOptions(gadget.props.element.querySelector('[name="consumed_quantity_unit_'+i+'"]'), option_array, 'weight/kg')
          }
        })
    })


    /////////////////////////////////////////
    // Fill product option list
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type:"Product"',
            select_list: ["title"],
            // sort_on: [["title", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var i,
            datalist = document.createElement("datalist"),
            option;
          for (i = 0; i < result.data.total_rows; i += 1) {
            option = document.createElement("option");
            option.text = result.data.rows[i].value.title;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector("#list_producttitle").innerHTML = datalist.innerHTML;
          gadget.props.element.querySelector("#list_consumedproducttitle").innerHTML = datalist.innerHTML;
        });
    })


    /////////////////////////////////////////
    // Fill location option lists
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: '(portal_type:"Storage Node" AND validation_state:"validated" AND is_my_storage_node:1)',
            select_list: ["title", "reference"],
            // sort_on: [["title", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var i,
            datalist = document.createElement("datalist"),
            option;
          for (i = 0; i < result.data.total_rows; i += 1) {
            option = document.createElement("option");
            option.text = result.data.rows[i].value.title;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector("#list_previouslocationtitle").innerHTML = datalist.innerHTML;
          gadget.props.element.querySelector("#list_nextlocationtitle").innerHTML = datalist.innerHTML;
        });
    })


    /////////////////////////////////////////
    // Initialization
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type:"Organisation" AND is_my_main_organisation:1',
            select_list: ["title", "reference"],
            // sort_on: [["title", "ascending"]],
            limit: [0, 2]
          });
        })
        .push(function (result) {
          if (result !== undefined && result.data.total_rows == 1) {
            return gadget.get(result.data.rows[0].id);
          }
        })
        .push(function (result) {
          if (result !== undefined) {
            gadget.props.element.querySelector("[name=nextowner]").value = result.title;
          }
        });
    })


    /////////////////////////////////////////
    // Nextlocation N changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name^="nextlocation"]'),
            "input",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  var normalized_value = normalizeTitle(evt.target.value);
                  if (normalized_value != evt.target.value){
                    evt.target.value = normalized_value;
                  }
                  return gadget.allDocs({
                    query: 'portal_type:"Storage Node" AND validation_state:"validated" AND title_lowercase: "' + evt.target.value.toLowerCase() + '" AND is_my_storage_node:1',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result !== undefined && result.data.total_rows == 1) {
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (doc) {
                  if (doc !== undefined) {
                    evt.target.value = doc.title;
                  }
                })
            }
          );
        });
    })


    /////////////////////////////////////////
    // product changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="product"]'),
            "input",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  var normalized_value = normalizeTitle(evt.target.value);
                  if (normalized_value != evt.target.value){
                    evt.target.value = normalized_value;
                  }
                  return gadget.allDocs({
                    query: 'portal_type:"Product" AND title_lowercase: "' + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result !== undefined && result.data.total_rows == 1) {
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (doc) {
                  if (doc !== undefined) {
                    evt.target.value = doc.title;
                  }
                })
            }
          );
        });
    })


    /////////////////////////////////////////
    // Consumed product N changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return multiLoopEventListener(
            $(gadget.props.element.querySelectorAll('input[name^="consumed_product_"]')),
            "input",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  var normalized_value = normalizeTitle(evt.target.value);
                  if (normalized_value != evt.target.value){
                    evt.target.value = normalized_value;
                  }
                  return gadget.allDocs({
                    query: 'portal_type:"Product" AND title_lowercase: "' + evt.target.value.toLowerCase() + '"',
                    select_list: ["title", "is_material"],
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result !== undefined && result.data.total_rows == 1) {
                    var regex_result = evt.target.name.match(/[0-9]{1,2}$/);
                    var postfix = "";
                    if (regex_result) {
                      postfix = regex_result[0];
                    }
                    if (result.data.rows[0].value.is_material) {
                      $(gadget.props.element.querySelector('input[name="consumed_drc_' + postfix + '"]')).textinput("enable");
                      $(gadget.props.element.querySelector('input[name="consumed_wet_quantity_' + postfix + '"]')).textinput("enable");
                    } else {
                      $(gadget.props.element.querySelector('input[name="consumed_drc_' + postfix + '"]')).textinput("disable").val("100");
                      $(gadget.props.element.querySelector('input[name="consumed_wet_quantity_' + postfix + '"]')).textinput("disable").val("");
                    }
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (doc) {
                  if (doc !== undefined) {
                    evt.target.value = doc.title;
                  }
                });
            }
          );
        });
    })


    /////////////////////////////////////////
    // DRC, dry quantity, wet quantity changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return multiLoopEventListener(
            $(gadget.props.element.querySelectorAll('input[name^="consumed_dry_quantity_"],input[name^="consumed_wet_quantity_"],input[name^="consumed_drc_"]')),
            "input",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(1000);
                })
                .push(function () {
                  var regex_result = evt.target.name.match(/[0-9]{1,2}$/);
                  var postfix = "";
                  if (regex_result) {
                    postfix = regex_result[0];
                  }
                  var dry_element = gadget.props.element.querySelector('input[name="consumed_dry_quantity_' + postfix + '"]');
                  var wet_element = gadget.props.element.querySelector('input[name="consumed_wet_quantity_' + postfix + '"]');
                  var drc_element = gadget.props.element.querySelector('input[name="consumed_drc_' + postfix + '"]');
                  fillDryWetDrc(evt, dry_element, wet_element, drc_element);
                });
            }
          );
        });
    })


    /////////////////////////////////////////
    // Previouslocation N changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return multiLoopEventListener(
            $(gadget.props.element.querySelectorAll('input[name^="previouslocation_"]')),
            "input",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  var normalized_value = normalizeTitle(evt.target.value);
                  if (normalized_value != evt.target.value){
                    evt.target.value = normalized_value;
                  }
                  return gadget.allDocs({
                    query: 'portal_type:"Storage Node" AND validation_state:"validated" AND title_lowercase: "' + evt.target.value.toLowerCase() + '" AND is_my_storage_node:1',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result !== undefined && result.data.total_rows == 1) {
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (doc) {
                  if (doc !== undefined) {
                    evt.target.value = doc.title;
                  }
                })
            }
          );
        });
    })


    /////////////////////////////////////////
    // add line button
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      var line_count = 2;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('button[name=add_line]'),
            'click',
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  $(gadget.props.element.querySelector('fieldset[name=line'+line_count+']')).show()
                  gadget.props.element.querySelector('fieldset[name=line'+line_count+'] input').focus()
                  line_count++;
                  if(line_count > 10){
                    $(gadget.props.element.querySelector('button[name=add_line]')).hide()
                  }
                })
            })
        })
    })


    /////////////////////////////////////////
    // Fill inputusername
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          fillMyInputUserName(gadget);
        })
    })


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));