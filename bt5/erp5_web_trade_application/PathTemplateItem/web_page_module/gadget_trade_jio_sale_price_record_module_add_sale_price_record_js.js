/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars,
            promiseEventListener, loopEventListener, $) {
  "use strict";


  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.region = [];
      g.props.quantity_unit = [];
      g.props.currency = [];
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();

    })

   /////////////////////////////////////////
   // Form submit
   /////////////////////////////////////////

    .declareService(function () {
      var form_gadget = this;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("erp5_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (doc) {

            doc.parent_relative_url = "sale_price_record_module";
            doc.portal_type = "Sale Price Record";
            doc.doc_id = getSequentialID('SPR');
            doc.local_validation = "self";
            doc.record_revision = 1;
            if (doc.sync_flag !== "1") {
              doc.portal_type = 'Sale Price Record Temp'; // For to avoid sync
            }


            addTemporaryCustomer(form_gadget);

            return form_gadget.jio_post(doc);

          })

          .push(function () {

            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({
                jio_key: form_gadget.options.jio_key,
                page: "view"

              })
            ]);

          });

      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    })

  /////////////////////////////////////////
    // Nextowner title changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()

        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="nextowner_title"]'),
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
                  if (normalized_value !== evt.target.value) {
                    evt.target.value = normalized_value;
                  }
                  gadget.props.element.querySelector('[name="nextowner"]')
                    .value = evt.target.value;
                })
                .push(function () {
                  return gadget.allDocs({
                    query: 'portal_type:("Organisation"' +
                      'OR "Organisation Temp") AND title_lowercase: "'
                      + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result !== undefined && result.data.total_rows === 1) {
                    gadget.jio_get(result.data.rows[0].id).then(
                      function (doc) {
                        if (doc.title !== evt.target.value) {
                          gadget.props.element
                            .querySelector('[name=nextowner_title]')
                            .value = doc.title;
                          gadget.props.element
                            .querySelector('[name=nextowner]')
                            .value = doc.title;
                        }
                      }
                    );
                    var event = document.createEvent("UIEvents");
                    event.initUIEvent("input", true, true, window, 1);
                    gadget.props.element
                      .querySelector('input[name="nextowner"]')
                      .dispatchEvent(event);
                  }
                });
            }
          );
        });
    })


  /////////////////////////////////////////
    // Nextowner changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()

        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="nextowner"]'),
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
                  if (normalized_value !== evt.target.value) {
                    evt.target.value = normalized_value;
                  }
                  return gadget.allDocs({
                    query:
                      'portal_type:("Organisation" OR "Organisation Temp")'
                       + 'AND title_lowercase: "'
                       + evt.target.value.toLowerCase() + '"',
                    limit: [0, 2]
                  });
                })
                .push(function (result) {
                  if (result.data.total_rows === 1) {
                    gadget.jio_get(result.data.rows[0].id).then(
                      function (doc) {
                        if (doc.title !== evt.target.value) {
                          gadget.props.element
                            .querySelector('[name=nextowner]').value
                            = doc.title;
                        }
                      }
                    );
                    return gadget.jio_get(result.data.rows[0].id);
                  }
                })
                .push(function (result) {
                  var tmp;
                  if (result !== undefined) {
                    // Fill the product fieldset
                    gadget.props.element
                      .querySelector('[name="nextowner_title"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="nextowner_reference"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name=' +
                                     '"default_telephone_coordinate_text"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="default_address_city"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="default_address_region"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="default_address_street_address"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="default_address_zip_code"]')
                      .setAttribute('disabled', 'disabled');
                    gadget.props.element
                      .querySelector('[name="default_email_coordinate_text"]')
                      .setAttribute('disabled', 'disabled');

                    gadget.props.element
                      .querySelector('[name="nextowner_title"]')
                      .value = result.title || "";
                    gadget.props.element
                      .querySelector('[name="nextowner_reference"]')
                      .value = result.reference || "";
                    gadget.props.element
                      .querySelector('[name=' +
                                     '"default_telephone_coordinate_text"]')
                      .value = result.default_telephone_coordinate_text || "";
                    gadget.props.element
                      .querySelector('[name="default_address_city"]')
                      .value = result.default_address_city || "";
                    gadget.props.element
                      .querySelector('[name="default_address_region"]')
                      .value = result.default_address_region || "";
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
                    gadget.props.element.querySelector('[name="nextowner_title"]').disabled = false;
                    gadget.props.element.querySelector('[name="nextowner_reference"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_city"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_region"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_street_address"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').disabled = false;

                    gadget.props.element.querySelector('[name="nextowner_title"]').value = "";
                    gadget.props.element.querySelector('[name="nextowner_reference"]').value = "";
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').value = "";
                    gadget.props.element.querySelector('[name="default_address_city"]').value = "";
                    tmp = gadget.props.element.querySelector('[name="default_address_region"]').querySelector('option:checked');
                    if (tmp !== null) {
                      tmp.selected = false;
                    }
                    $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('enable');
                    $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('refresh');
                    gadget.props.element.querySelector('[name="default_address_street_address"]').value = "";
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').value = "";
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').value = "";
                  }
                });
            }
          );
        });
    })




    .declareMethod("render", function (options) {
      var page_gadget = this,
          gadget,
          sycn_method,
          title,
          relative_url;

          
      page_gadget.options = options;
        
       sycn_method= "1"; 
      
        
      
      
      var state=translateString(getWorkflowState(page_gadget.options.doc.portal_type, page_gadget.options.jio_key, page_gadget.options.doc.sync_flag,   page_gadget.options.doc.local_validation, page_gadget.options.doc.local_state));
    
     return new RSVP.Queue()
     .push(function () {
          return page_gadget.updateHeader({
            title: "New Sale Price Record",
            add_action: true
          });
        })
        
       .push(function () {
      
          return RSVP.all([

           page_gadget.allDocs({
            query: 'portal_type: "Currency" AND validation_state: "validated"',
            select_list: ["title", "logical_path", "relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          }),
      
           page_gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "quantity_unit/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          }),
      
      
      
           page_gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "region/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          })
      
      
          ]);
            })
        .push(function (allresult) {
            var i,j;
            for (i = 0; i < allresult[0].data.total_rows; i += 1) {
              title=allresult[0].data.rows[i].value.title;
              relative_url=allresult[0].data.rows[i].value.relative_url;
              page_gadget.props.currency.push([title,relative_url]);
             }

      
      
            for (i = 0; i < allresult[1].data.total_rows; i += 1) {
              title= allresult[1].data.rows[i].value.logical_path || allresult[1].data.rows[i].value.title;
              relative_url=allresult[1].data.rows[i].value.category_relative_url;
              page_gadget.props.quantity_unit.push([title,relative_url]);
  
            
            }
      
      
            for (i = 0; i < allresult[2].data.total_rows; i += 1) {
              title=allresult[2].data.rows[i].value.logical_path || allresult[2].data.rows[i].value.title;
              relative_url=allresult[2].data.rows[i].value.category_relative_url;
              page_gadget.props.region.push([title,relative_url]);

            
           }
      
          return;
      
      })
       .push(function () {

          return  page_gadget.getDeclaredGadget("erp5_form")
      })
        .push(function (form_gadget) {
          gadget=form_gadget;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
        
               "sale_price": {
                "description": "",
                "title": "",
                "default":"Sale price of a specific product to a specific customer",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 1,
                "key": "sale_price",
                "hidden": 0,
                "type": "ReadonlyField"
              },
        
              "product": {
                "description": "",
                "title": "Product Title",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "nextowner": {
                "description": "",
                "title": "Client",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "nextowner",
                "hidden": 0,
                "type": "StringField"
              },
              "organisation": {
                "description": "",
                "title": "Sales Organisation",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "previousowner",
                "hidden": 0,
                "type": "StringField"
              },
              "warehouse": {
                "description": "",
                "title": "Sender Warehouse",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "previouslocation",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "base_price",
                "hidden": 0,
                "type": "StringField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": "",
                "items":page_gadget.props.currency,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "price_currency",
                "hidden": 0,
                "type": "ListField"
              },
              "priced_quantity": {
                "description": "",
                "title": "Priced Quantity",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "priced_quantity",
                "hidden": 0,
                "type": "StringField"
              },
               "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": "",
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "total_dry_quantity": {
                "description": "",
                "title": "Quantity",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "total_dry_quantity",
                "hidden": 0,
                "type": "StringField"
              },
              "total_amount_price": {
                "description": "",
                "title": "Total Price",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "total_amount_price",
                "hidden": 0,
                "type": "StringField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "date",
                "hidden": 0,
                "type": "StringField"
              },
              "contract_no": {
                "description": "",
                "title": "Contract No",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "contract_no",
                "hidden": 0,
                "type": "StringField"
              },
              "batch": {
                "description": "",
                "title": "Batch",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "batch",
                "hidden": 0,
                "type": "TextAreaField"
              },
              "comment": {
                "description": "",
                "title": "Comment",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "comment",
                "hidden": 0,
                "type": "StringField"
              },
              "sync_method": {
                "description": "",
                "title": "Sync Method",
                "default": sycn_method,
                "items":[["Ready To Sync","1"],
                         ["Do Not Sync","0"],
                        ],
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "sync_flag",
                "hidden": 0,
                "type": "RadioField"
              },
              
               "username": {
                "description": "",
                "title": "Input User Name",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "inputusername",
                "hidden": 0,
                "type": "StringField"
              },
        
              "client_head": {
                "description": "",
                "title": "",
                "default": "Client",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 1,
                "key": "client_head",
                "hidden": 0,
                "type": "ReadonlyField"
              },
              
              
              
              "client": {
                "description": "",
                "title": "Client",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "nextowner_title",
                "hidden": 0,
                "type": "StringField"
              },
              "client_reference": {
                "description": "",
                "title": "Client Reference",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "nextowner_reference",
                "hidden": 0,
                "type": "StringField"
              },
              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              },
              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField"
              },
              "region": {
                "description": "",
                "title": "Region",
                "default": "",
                "items":page_gadget.props.region,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField"
              },
              "address_street": {
                "description": "",
                "title": "Street Address",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField"
              },
              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_address_zip_code",
                "hidden": 0,
                "type": "StringField"
              },
              "email": {
                "description": "",
                "title": "Email",
                "default": "",
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              }
         
            }}},
            form_definition: {
              group_list: [
                
                
                [
                 "left",
                [["sale_price"],["product"],
                ["nextowner"], ["organisation"], ["warehouse"],
                ["price"], ["currency"], ["priced_quantity"],
                ["quantity_unit"],["total_dry_quantity"], ["total_amount_price"], 
                ["date"],["contract_no"], ["batch"], 
                ["comment"],["sync_method"],["username"], ]
                ],
                
                [
                "right",
                [["client_head"],
                ["client"], ["client_reference"], ["telephone"],
                ["address_city"], ["region"], ["address_street"],
                ["postal_code"], ["email"]]
                ]
                 
              ]
   
            }
          });
        })
     .push(function () {
                  gadget.props.element.querySelector('[name="date"]').setAttribute('type', 'date');
     



        

     })

    })

   

}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
