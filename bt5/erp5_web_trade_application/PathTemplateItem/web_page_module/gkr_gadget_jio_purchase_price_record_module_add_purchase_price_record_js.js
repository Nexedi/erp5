/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".new-purchase-price-record-template")
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
    .declareAcquiredMethod('jio_remove', 'jio_remove')

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;

      return gadget.translateHtml(template({
        date: new Date().toISOString().split('T')[0]
      }))
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          gadget.props.element.querySelector('[name=product_title]').setAttribute('readOnly', 'readOnly')
          gadget.props.element.querySelector('[name=product_line]').setAttribute('disabled', 'disabled')
          gadget.props.element.querySelector('[name=product_reference]').setAttribute('readOnly', 'readOnly')
          return gadget.updateHeader({
            title: "New Purchase Price Record"
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
            gadget.props.element.querySelector('form.new-purchase-price-record-form'),
            'submit',
            false
          );
        })
        .push(function (submit_event) {
          var i,
            doc = {
              // XXX Hardcoded
              parent_relative_url: "purchase_price_record_module",
              portal_type: "Purchase Price Record",
              doc_id: getSequentialID('PPR'),
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
              doc[submit_event.target[i].name] = submit_event.target[i].value;
            }
          }

          if (doc.sync_flag != "1"){
            doc.portal_type = 'Purchase Price Record Temp' // For to avoid sync
          }

          addTemporarySupplier(gadget);
          addTemporaryProduct(gadget);

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
    // Fill product line categories
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "product_line/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var i,
            datalist = document.createElement("select"),
            option;
          for (i = 0; i < result.data.total_rows; i += 1) {
            option = document.createElement("option");
            option.text = result.data.rows[i].value.logical_path || result.data.rows[i].value.title;
            option.value = result.data.rows[i].value.category_relative_url;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector('[name="product_line"]').innerHTML +=
            datalist.innerHTML;
        });
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
          var i,
            datalist = document.createElement("select"),
            option;
          for (i = 0; i < result.data.total_rows; i += 1) {
            option = document.createElement("option");
            option.text = result.data.rows[i].value.logical_path || result.data.rows[i].value.title;
            option.value = result.data.rows[i].value.category_relative_url;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector('[name="quantity_unit"]').innerHTML +=
            datalist.innerHTML;
        })
       .push(function(){
          $(gadget.props.element.querySelector("option[value='weight/kg']")).attr("selected", true);
          $(gadget.props.element.querySelector("[name=quantity_unit]")).selectmenu("refresh");
        })
    })


    /////////////////////////////////////////
    // Fill region categories
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "region/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var i,
            datalist = document.createElement("select"),
            option;
          for (i = 0; i < result.data.total_rows; i += 1) {
            option = document.createElement("option");
            option.text = result.data.rows[i].value.logical_path || result.data.rows[i].value.title;
            option.value = result.data.rows[i].value.category_relative_url;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector('[name="default_address_region"]').innerHTML +=
            datalist.innerHTML;
        });
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
          gadget.props.element.querySelector("#list_producttitle").innerHTML =
            datalist.innerHTML;
        });
    })



    /////////////////////////////////////////
    // Product title changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="product_title"]'),
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
                    gadget.props.element.querySelector('[name="product"]').value = evt.target.value;
                })
                .push(function () {
                  return gadget.allDocs({
                    query: 'portal_type:"Product" AND title_lowercase: "' + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function(result){
                  if (result !== undefined && result.data.total_rows == 1) {
                    gadget.get(result.data.rows[0].id).then(
                      function(doc){
                        if(doc.title!=evt.target.value){
                          gadget.props.element.querySelector('[name=product_title]').value=doc.title;
                          gadget.props.element.querySelector('[name=product]').value=doc.title
                        }
                      }
                    );
                    var event = document.createEvent("UIEvents");
                    event.initUIEvent("input", true, true, window, 1);
                    gadget.props.element.querySelector('input[name="product"]').dispatchEvent(event);
                  }
                })
            })
        });
    })


    /////////////////////////////////////////
    // Product changed.
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
                  if (result.data.total_rows === 1) {
                    gadget.get(result.data.rows[0].id).then(
                      function(doc){
                        if(doc.title!=evt.target.value){
                          gadget.props.element.querySelector('[name=product]').value=doc.title
                        }
                      }
                    );
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (result) {
                  var tmp;
                  if (result !== undefined) {
                    gadget.props.element.querySelector('[name="product_title"]').setAttribute('readonly', 'readonly')
                    gadget.props.element.querySelector('[name="product_reference"]').setAttribute('readonly', 'readonly')
                    gadget.props.element.querySelector('[name="product_line"]').setAttribute('disabled', 'disabled')
                    // Fill the product fieldset
                    gadget.props.element.querySelector('[name="product_title"]').value = result.title || "";
                    gadget.props.element.querySelector('[name="product_reference"]').value = result.reference || "";

                    tmp = gadget.props.element.querySelector('[name="product_line"]').querySelector('option:checked');
                    if (tmp !== null) {
                      tmp.selected = true;
                    }
                    tmp = result.product_line || "";
                    if (tmp !== "") {
                      tmp = gadget.props.element.querySelector('[name="product_line"]').querySelector('[value="' + tmp + '"]');
                      if (tmp !== null) {
                        tmp.selected = true;
                      }
                    }
                    $(gadget.props.element.querySelector('[name="product_line"]')).selectmenu('refresh');

                  } else {
                    gadget.props.element.querySelector('[name="product_title"]').value = "";
                    gadget.props.element.querySelector('[name="product_reference"]').value = "";

                    tmp = gadget.props.element.querySelector('[name="product_line"]').querySelector('option:checked');
                    if (tmp !== null) {
                      tmp.selected = false;
                      $(gadget.props.element.querySelector('[name="product_line"]')).selectmenu('refresh');
                    }

                  }
                });
            }
          );
        });
    })


    /////////////////////////////////////////
    // Fill previousowner option list
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type:("Organisation" OR "Organisation Temp")',
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
          gadget.props.element.querySelector("#list_previousownertitle").innerHTML =
            datalist.innerHTML;
        });
    })


    /////////////////////////////////////////
    // Previousowner title changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="previousowner_title"]'),
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
                  gadget.props.element.querySelector('[name="previousowner"]').value = evt.target.value;
                })
                .push(function () {
                  return gadget.allDocs({
                    query: 'portal_type:("Organisation" OR "Organisation Temp") AND title_lowercase: "' + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function(result){
                  if (result !== undefined && result.data.total_rows == 1) {
                    gadget.get(result.data.rows[0].id).then(
                      function(doc){
                        if(doc.title!=evt.target.value){
                          gadget.props.element.querySelector('[name=previousowner_title]').value=doc.title;
                          gadget.props.element.querySelector('[name=previousowner]').value=doc.title
                        }
                      }
                    );
                    var event = document.createEvent("UIEvents");
                    event.initUIEvent("input", true, true, window, 1);
                    gadget.props.element.querySelector('input[name="previousowner"]').dispatchEvent(event);
                    }
                })
            })
        });
    })


    /////////////////////////////////////////
    // Previousowner changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="previousowner"]'),
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
                    query: 'portal_type:("Organisation" OR "Organisation Temp") AND title_lowercase: "' + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result.data.total_rows === 1) {
                    gadget.get(result.data.rows[0].id).then(
                      function(doc){
                        if(doc.title!=evt.target.value){
                          gadget.props.element.querySelector('[name=previousowner]').value=doc.title
                        }
                      }
                    );
                    return gadget.get(result.data.rows[0].id);
                  }
                })
                .push(function (result) {
                  var tmp;
                  if (result !== undefined) {
                    // Fill the product fieldset

                    gadget.props.element.querySelector('[name="previousowner_title"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="previousowner_reference"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_address_city"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_address_region"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_address_street_address"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').setAttribute('disabled', 'disabled')
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').setAttribute('disabled', 'disabled')


                    gadget.props.element.querySelector('[name="previousowner_title"]').value = result.title || "";
                    gadget.props.element.querySelector('[name="previousowner_reference"]').value = result.reference || "";
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').value = result.default_telephone_coordinate_text || "";
                    gadget.props.element.querySelector('[name="default_address_city"]').value = result.default_address_city || "";
                    gadget.props.element.querySelector('[name="default_address_region"]').value = result.default_address_region || "";
                    tmp = gadget.props.element.querySelector('[name="default_address_region"]').querySelector('option:checked');
                    if (tmp !== null) {
                      tmp.selected = true;
                    }
                    tmp = result.default_address_region || "";
                    if (tmp !== "") {
                      tmp = gadget.props.element.querySelector('[name="default_address_region"]').querySelector('[value="' + tmp + '"]');
                      if (tmp !== null) {
                        tmp.selected = true;
                      }
                    }
                    $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('refresh');
                    gadget.props.element.querySelector('[name="default_address_street_address"]').value = result.default_address_street_address || "";
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').value = result.default_address_zip_code || "";
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').value = result.default_email_coordinate_text || "";
                  } else {
                    gadget.props.element.querySelector('[name="previousowner_title"]').disabled = false;
                    gadget.props.element.querySelector('[name="previousowner_reference"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_city"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_region"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_street_address"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').disabled = false;

                    gadget.props.element.querySelector('[name="previousowner_title"]').value = "";
                    gadget.props.element.querySelector('[name="previousowner_reference"]').value = "";
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').value = "";
                    gadget.props.element.querySelector('[name="default_address_city"]').value = "";
                    tmp = gadget.props.element.querySelector('[name="default_address_region"]').querySelector('option:checked');
                    if (tmp !== null) {
                      tmp.selected = false;
                      $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('refresh');
                    }
                    gadget.props.element.querySelector('[name="default_address_street_address"]').value = "";
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').value = "";
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').value = "";
                  }
                });
            }
          );
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