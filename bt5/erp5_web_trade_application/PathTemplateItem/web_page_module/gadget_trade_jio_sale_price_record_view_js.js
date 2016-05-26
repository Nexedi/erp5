/*globals window, rJS, Handlebars, RSVP, rJS,Handlebars, promiseEventListener, loopEventListener,jQuery,
translateString, getWorkflowState, document, getSequentialID, addTemporaryCustomer */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, promiseEventListener, $) {
  "use strict";

 /////////////////////////////////////////
  // Nextowner changed.
  /////////////////////////////////////////
  function nextownerChange(gadget) {
    var page_gadget = gadget,
      result_tmp,
      disabled,
      nextowner_title,
      nextowner_reference,
      default_telephone_coordinate_text,
      default_address_city,
      default_address_region,
      default_address_street_address,
      default_address_zip_code,
      default_email_coordinate_text;
    return new RSVP.Queue()
      .push(function () {

        return gadget.allDocs({
          query: 'portal_type:("Organisation"' +
                   'OR "Organisation Temp") AND title_lowercase: "'
                  + page_gadget.stringChange.toLowerCase() + '"',
          limit: [0, 2]
        });
      })

      .push(function (result) {
        if (result.data.total_rows === 1) {
          return gadget.jio_get(result.data.rows[0].id);
        }
      })


      .push(function (result) {
        result_tmp = result;
        return page_gadget.getDeclaredGadget("erp5_form");
      })
      .push(function (form_gadget) {
        if (result_tmp !== undefined) {
          nextowner_title =  result_tmp.title;
          nextowner_reference =  result_tmp.reference;
          default_telephone_coordinate_text =
            result_tmp.default_telephone_coordinate_text;
          default_address_city =  result_tmp.default_address_city;
          default_address_region =  result_tmp.default_address_region;
          default_address_street_address =
            result_tmp.default_address_street_address;
          default_address_zip_code =
            result_tmp.default_address_zip_code;
          default_email_coordinate_text =
            result_tmp.default_email_coordinate_text;
          disabled = 1;

        }
        if (page_gadget.nextownerTitleChange) {
          nextowner_title = page_gadget.stringChange;
          page_gadget.nextownerTitleChange = 0;
        }
        return RSVP.all([

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Client",
                "default": nextowner_title,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "nextowner_title",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "nextowner_title"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Client Reference",
                "default": nextowner_reference,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "nextowner_reference",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "nextowner_reference"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Default Telephone",
                "default": default_telephone_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "default_telephone_coordinate_text"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Default Address City",
                "default": default_address_city,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "default_address_city"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Region",
                "default": default_address_region,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField",
                "change" : 1,
                "disabled" : disabled

              }

            }
                                         }},

            gadget: "default_address_region"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Street Address",
                "default": default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "default_address_street_address"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Postal Code",
                "default": default_address_zip_code,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_address_zip_code",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }
            }
                                         }},

            gadget: "default_address_zip_code"
          }),

          form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Email",
                "default": default_email_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField",
                "change" : 1,
                "disabled" : disabled
              }

            }
                                         }},
            gadget: "default_email_coordinate_text"
          })
        ]);


      });

  }



  /////////////////////////////////////////
  // Nextowner title changed.
  /////////////////////////////////////////
  function nextownerTitleChange(gadget) {
    var page_gadget = gadget;
    page_gadget.nextownerTitleChange = 1;

    nextownerChange(page_gadget);

    return new RSVP.Queue()

      .push(function () {
        return page_gadget.getDeclaredGadget("erp5_form");
      })
      .push(function (form_gadget) {

        return form_gadget.render({
          erp5_document: {"_embedded": {"_view": {
            field_json : {
              "description": "",
              "title": "Client",
              "default": page_gadget.stringChange,
              "css_class": "",
              "required": 1,
              "editable": 1,
              "key": "nextowner",
              "hidden": 0,
              "type": "StringField",
              "change" : 1,
              "disabled" : 0
            }
          }
                                         }},

          gadget: "nextowner"
        });



      });


  }


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

    .allowPublicAcquisition("inputChange", function (param_list) {
      this.gadgetChange = param_list[1];
      if (this.gadgetChange === "nextowner") {
        this.stringChange = param_list[0].nextowner;

        return nextownerChange(this);
      }
      if (this.gadgetChange === "nextowner_title") {
        this.stringChange = param_list[0].nextowner_title;

        return nextownerTitleChange(this);

      }

    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function (options) {
      var page_gadget = this,
        gadget,
        sycn_method,
        title,
        relative_url,
        editable,
        state;
      page_gadget.options = options;
      if (page_gadget.options.doc.sync_flag === 1) {
        sycn_method = "Ready To Sync";
      } else {
        sycn_method = "Do Not Sync";
      }
      state = translateString(getWorkflowState(
        page_gadget.options.doc.portal_type,
        page_gadget.options.jio_key,
        page_gadget.options.doc.sync_flag,
        page_gadget.options.doc.local_validation,
        page_gadget.options.doc.local_state
      ));
      if (page_gadget.options.jio_key.indexOf('sale_price_record_module/')
          === 0) {
        editable = 0;
        $('<a data-role="button" href="Base_redirectToGeneratedDocumentOf/'
          + page_gadget.options.jio_key + '" target="_blank">'
          + translateString('Go To ERP5') + '</a>').appendTo(
          $(page_gadget.props.element.querySelector('form'))
        );
      } else {
        editable = 1;
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([

            page_gadget.allDocs({
              query:
                'portal_type: "Currency" AND validation_state: "validated"',
              select_list: ["title", "logical_path", "relative_url"],
              // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            }),
            page_gadget.allDocs({
              query:
                'portal_type: "Category" AND relative_url: "quantity_unit/%"',
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
          var i;
          for (i = 0; i < allresult[0].data.total_rows; i += 1) {
            title = allresult[0].data.rows[i].value.title;
            relative_url = allresult[0].data.rows[i].value.relative_url;
            page_gadget.props.currency.push([title, relative_url]);
          }

          for (i = 0; i < allresult[1].data.total_rows; i += 1) {
            title = allresult[1].data.rows[i].value.logical_path
              || allresult[1].data.rows[i].value.title;
            relative_url =
              allresult[1].data.rows[i].value.category_relative_url;
            page_gadget.props.quantity_unit.push([title, relative_url]);

          }
          page_gadget.props.region.push(["", ""]);


          for (i = 0; i < allresult[2].data.total_rows; i += 1) {
            title = allresult[2].data.rows[i].value.logical_path
              || allresult[2].data.rows[i].value.title;
            relative_url =
              allresult[2].data.rows[i].value.category_relative_url;
            page_gadget.props.region.push([title, relative_url]);

          }

          return;
        })
        .push(function () {

          return page_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          gadget = form_gadget;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {

              "sale_price": {
                "description": "",
                "title": "",
                "default":
                   "Sale price of a specific product to a specific customer",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": editable,
                "key": "sale_price",
                "hidden": 0,
                "type": "ReadonlyField"
              },

              "username": {
                "description": "",
                "title": "Input User Name",
                "default": page_gadget.options.doc.inputusername,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "inputusername",
                "hidden": 0,
                "type": "StringField"
              },
              "state": {
                "description": "",
                "title": "State",
                "default": state,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "state",
                "hidden": 0,
                "type": "ReadonlyField"
              },
              "product": {
                "description": "",
                "title": "Product Title",
                "default": page_gadget.options.doc.product,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "nextowner": {
                "description": "",
                "title": "Client",
                "default": page_gadget.options.doc.nextowner,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "nextowner",
                "hidden": 0,
                "type": "StringField"
              },
              "organisation": {
                "description": "",
                "title": "Sales Organisation",
                "default": page_gadget.options.doc.previousowner,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "previousowner",
                "hidden": 0,
                "type": "StringField"
              },
              "warehouse": {
                "description": "",
                "title": "Sender Warehouse",
                "default": page_gadget.options.doc.previouslocation,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "previouslocation",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": page_gadget.options.doc.base_price,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "base_price",
                "hidden": 0,
                "type": "StringField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": page_gadget.options.doc.price_currency,
                "items": page_gadget.props.currency,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "price_currency",
                "hidden": 0,
                "type": "ListField"
              },
              "priced_quantity": {
                "description": "",
                "title": "Priced Quantity",
                "default": page_gadget.options.doc.priced_quantity,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "priced_quantity",
                "hidden": 0,
                "type": "StringField"
              },
              "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": page_gadget.options.doc.quantity_unit,
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "total_dry_quantity": {
                "description": "",
                "title": "Quantity",
                "default": page_gadget.options.doc.total_dry_quantity,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "total_dry_quantity",
                "hidden": 0,
                "type": "StringField"
              },
              "total_amount_price": {
                "description": "",
                "title": "Total Price",
                "default": page_gadget.options.doc.total_amount_price,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "total_amount_price",
                "hidden": 0,
                "type": "StringField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": page_gadget.options.doc.date,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "date",
                "hidden": 0,
                "type": "StringField"
              },
              "contract_no": {
                "description": "",
                "title": "Contract No",
                "default": page_gadget.options.doc.contract_no,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "contract_no",
                "hidden": 0,
                "type": "StringField"
              },
              "batch": {
                "description": "",
                "title": "Batch",
                "default": page_gadget.options.doc.batch,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "batch",
                "hidden": 0,
                "type": "TextAreaField"
              },
              "comment": {
                "description": "",
                "title": "Comment",
                "default": page_gadget.options.doc.comment,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "comment",
                "hidden": 0,
                "type": "StringField"
              },
              "sync_method": {
                "description": "",
                "title": "Sync Method",
                "default": sycn_method,
                "items": [["Ready To Sync", "Ready To Sync"],
                          ["Do Not Sync", "Do Not Sync"]
                         ],
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "sync_flag",
                "hidden": 0,
                "type": "RadioField"
              },
              "client_head": {
                "description": "",
                "title": "",
                "default": "Client",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 0,
                "key": "client_head",
                "hidden": 0,
                "type": "ReadonlyField"
              },

              "client": {
                "description": "",
                "title": "Client",
                "default": page_gadget.options.doc.nextowner_title,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "nextowner_title",
                "hidden": 0,
                "type": "StringField"
              },
              "client_reference": {
                "description": "",
                "title": "Client Reference",
                "default": page_gadget.options.doc.nextowner_reference,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "nextowner_reference",
                "hidden": 0,
                "type": "StringField"
              },
              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default":
                   page_gadget.options.doc.default_telephone_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              },
              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": page_gadget.options.doc.default_address_city,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField"
              },
              "region": {
                "description": "",
                "title": "Region",
                "default": page_gadget.options.doc.default_address_region,
                "items": page_gadget.props.region,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField"
              },
              "address_street": {
                "description": "",
                "title": "Default Address",
                "default":
                  page_gadget.options.doc.default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField"
              },
              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default": page_gadget.options.doc.default_address_zip_code,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_address_zip_code",
                "hidden": 0,
                "type": "StringField"
              },
              "email": {
                "description": "",
                "title": "Email",
                "default":
                  page_gadget.options.doc.default_email_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              }

            }}},
            form_definition: {
              group_list: [

                [
                  "left",
                  [["sale_price"],
                    ["username"], ["state"], ["product"],
                    ["nextowner"], ["organisation"], ["warehouse"],
                    ["price"], ["currency"], ["priced_quantity"],
                    ["quantity_unit"], ["total_dry_quantity"],
                    ["total_amount_price"],
                    ["date"], ["contract_no"], ["batch"],
                    ["comment"], ["sync_method"]]
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
          var btn, t, btn2, t2;

          btn2 = document.createElement("BUTTON");
          btn2.setAttribute('name', 'create_sale_record');
          t2 = document.createTextNode("Create Sale Record");
          btn2.appendChild(t2);

          gadget.props.element.querySelector('.right').appendChild(btn2);

          if (page_gadget.options.jio_key.indexOf('sale_price_record_module/')
              === 0) {
            btn = document.createElement("BUTTON");
            btn.setAttribute('name', 'create_new_version');
            t = document.createTextNode("Update Data");
            btn.appendChild(t);
            gadget.props.element.querySelector('.right').appendChild(btn);

          } else {
            return page_gadget.updateHeader({
              title: "New Sale Price Record",
              save_action: true
            });
          }



        });


    })

    /////////////////////////////////////////
    // New version of the the Sale Price Record
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        cloned_doc,
        current_doc,
        new_id;

      if (gadget.props.element
          .querySelector('[name=create_new_version]') === null) {
        return;
      }

      return new RSVP.Queue()
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('[name=create_new_version]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.jio_get(gadget.options.jio_key);
        })
        .push(function (result) {
          current_doc = result;
          cloned_doc = JSON.parse(JSON.stringify(result));

          // Do not sync the cloned document
          cloned_doc.copy_of = gadget.options.jio_key;
          cloned_doc.hidden_in_html5_app_flag = "0";
          delete cloned_doc.local_state;
          delete cloned_doc.sync_flag;
          cloned_doc.portal_type = 'Sale Price Record Temp';
          cloned_doc.record_revision = (cloned_doc.record_revision || 1) + 1;

          current_doc.hidden_in_html5_app_flag = "1";

          return gadget.jio_post(cloned_doc);
        })
        .push(function (id) {
          new_id = id;
          // Hide the document
          //at the end in order to still view it in case of issue
          // Better have 2 docs than none visible
          return gadget.jio_put(gadget.options.jio_key, current_doc);
        })
        .push(function () {
          return gadget.redirect({
            jio_key: new_id,
            page: "view"
          });
        });

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
            doc.doc_id = form_gadget.options.doc.doc_id;
            doc.local_validation = "self";
            doc.record_revision =  form_gadget.options.doc.record_revision || 1;
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
                jio_key: "sale_price_record_module",
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
    // Create Sale Record
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      if (gadget.props.element.querySelector('[name=create_sale_record]')
          === null) {
        return;
      }

      return new RSVP.Queue()

        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('[name=create_sale_record]'),
            'click',
            false
          );
        })
        .push(function () {
          var doc = {
            // XXX Hardcoded
            parent_relative_url: "sale_record_module",
            portal_type: "Sale Price Record Temp",
            doc_id: getSequentialID('SR'),
            causality_doc_id: gadget.options.doc.doc_id,
            causality_price_record: gadget.options.jio_key,
            record_revision: 1,
            quantity: 0,
            price: gadget.options.doc.base_price,
            price_quantity_unit: gadget.options.doc.quantity_unit,
            product: gadget.options.doc.product,
            nextowner: gadget.options.doc.nextowner,
            previousowner: gadget.options.doc.previousowner,
            previouslocation: gadget.options.doc.previouslocation,
            price_currency: gadget.options.doc.price_currency,
            quantity_unit: gadget.options.doc.quantity_unit,
            date: gadget.options.doc.date,
            contract_no: gadget.options.doc.contract_no,
            batch: gadget.options.doc.batch,
            comment: gadget.options.doc.comment,
            sync_flag: "",
            local_validation: "self",
            //inputusername: my_input_user_name,
            hidden_in_html5_app_flag: "0",
            drc: 100,
            drc2: 100,
            drc3: 100,
            drc4: 100,
            drc5: 100,
            drc6: 100,
            drc7: 100,
            drc8: 100,
            drc9: 100,
            drc10: 100
          };

          return gadget.jio_post(doc);
        })
        .push(function (response) {
          return gadget.redirect({
            jio_key: response,
            page: "view"
          });
        });

    }
      );

}(window, document, RSVP,
  rJS, promiseEventListener, jQuery));
