/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-sale-price-record-template")
                              .innerHTML,
    template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('jio_remove', 'jio_remove')

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function (result_list) {
          return gadget.translateHtml(template(options.doc));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;

          gadget.props.element.querySelector('[name="nextowner_title"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="nextowner_reference"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="default_address_city"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="default_address_region"]').setAttribute('disabled', 'disabled');
          gadget.props.element.querySelector('[name="default_address_street_address"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="default_address_zip_code"]').setAttribute('readOnly', 'readOnly');
          gadget.props.element.querySelector('[name="default_email_coordinate_text"]').setAttribute('readOnly', 'readOnly');

          if (gadget.options.jio_key.indexOf('sale_price_record_module/') == 0){
            var submit_button = gadget.props.element.querySelector("input[type=submit][name=save]");
            submit_button.parentNode.removeChild(submit_button);
            $(gadget.props.element.querySelectorAll('input,textarea')).attr('readonly', true);
            $(gadget.props.element.querySelectorAll('select,input[type=checkbox],input[type=radio]')).attr('disabled', true);
          }
          if (!(gadget.options.doc.local_state == "validated" || ["self", "manager", "hqmanager"].indexOf(gadget.options.doc.local_validation) >= 0)){
            var create_sale_record_button = gadget.props.element.querySelector("input[type=button][name=create_sale_record]");
            create_sale_record_button.parentNode.removeChild(create_sale_record_button);
          }

          if (gadget.options.jio_key.indexOf('sale_price_record_module/') == 0){
            $('<a data-role="button" href="Base_redirectToGeneratedDocumentOf/'+gadget.options.jio_key+'" target="_blank">'+translateString('Go To ERP5')+'</a>').appendTo($(gadget.props.element.querySelector('form')))
          } else {
            var submit_button = gadget.props.element.querySelector("input[type=button][name=create_new_version]");
            if(submit_button){
              submit_button.parentNode.removeChild(submit_button);
            }
          }

          // Set my_input_user_name variable
          fillMyInputUserName(gadget);

          gadget.props.element.querySelector('#state').innerHTML = translateString(getWorkflowState(gadget.options.doc.portal_type, gadget.options.jio_key, gadget.options.doc.sync_flag, gadget.options.doc.local_validation, gadget.options.doc.local_state))

          return gadget.updateHeader({
            title: translateString("Sale Price Record") + " " + gadget.options.doc.doc_id + " " + (gadget.options.doc.record_revision || 1)
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
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

      if(gadget.props.element.querySelector('input[type=button][name=create_new_version]') == null){
        return;
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('input[type=button][name=create_new_version]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.get(gadget.options.jio_key);
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

          return gadget.post(cloned_doc);
        })
        .push(function (id) {
          new_id = id;
          // Hide the document at the end in order to still view it in case of issue
          // Better have 2 docs than none visible
          return gadget.put(gadget.options.jio_key, current_doc);
        })
        .push(function (response) {
          return gadget.redirect({
            jio_key: new_id,
            page: "view"
          });
        });

    })


    /////////////////////////////////////////
    // Create Sale Record
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      if(gadget.props.element.querySelector('input[type=button][name=create_sale_record]') == null){
        return;
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('input[type=button][name=create_sale_record]'),
            'click',
            false
          );
        })
        .push(function (click_event) {
          var doc = {
            // XXX Hardcoded
            parent_relative_url: "sale_record_module",
            portal_type: "Sale Record Temp",
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
            inputusername: my_input_user_name,
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
            drc10: 100,
          };

          return gadget.post(doc);
        })
        .push(function (response) {
          return gadget.redirect({
            jio_key: response,
            page: "view"
          });
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
          return loopEventListener(
            gadget.props.element.querySelector('form.view-sale-price-record-form'),
            'submit',
            false,
            function (submit_event) {
              return new RSVP.Queue()
                .push(function () {
                  if (gadget.options.jio_key.indexOf('sale_price_record_module/') == 0){
                    return;
                  }
                  var i,
                    doc = {
                      // XXX Hardcoded
                      parent_relative_url: "sale_price_record_module",
                      portal_type: "Sale Price Record",
                      doc_id: gadget.options.doc.doc_id,
                      local_validation: "self",
                      record_revision: (gadget.options.doc.record_revision || 1),
                    };
                  gadget.props.element.querySelector("input[type=submit]")
                                      .disabled = true;
                  for (i = 0; i < submit_event.target.length; i += 1) {
                    // XXX Should check input type instead
                    if (submit_event.target[i].name && submit_event.target[i].type != "submit") {
                      if ((submit_event.target[i].type == "radio" || submit_event.target[i].type == "checkbox") && !submit_event.target[i].checked){
                        continue
                      }
                      doc[submit_event.target[i].name] = submit_event.target[i].value;
                    }
                  }
                  if (doc.local_validation == "no"){
                    doc.sync_flag = "" // Do not sync
                  }
                  if (doc.sync_flag != "1"){
                    doc.portal_type = 'Sale Price Record Temp' // For to avoid sync
                  }

                  addTemporaryCustomer(gadget);

                  $("#saveMessage").popup('open');
                  return gadget.put(gadget.options.jio_key, doc);
                })
                .push(function () {
                  gadget.props.element.querySelector("input[type=submit]").disabled = false;
                })
            }
          )
      })
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
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type: "Currency" AND validation_state: "validated"',
            select_list: ["title", "logical_path", "relative_url"],
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
            option.text = result.data.rows[i].value.title;
            option.value = result.data.rows[i].value.relative_url;
            datalist.appendChild(option);
          }
          gadget.props.element.querySelector('[name="price_currency"]').innerHTML +=
            datalist.innerHTML;
        })
        .push(function (){
          $(gadget.props.element.querySelector("option[value='"+gadget.options.doc.price_currency+"']")).attr("selected", true);
          $(gadget.props.element.querySelector("[name='price_currency']")).selectmenu("refresh");
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
        .push(function (){
          $(gadget.props.element.querySelector("option[value='"+gadget.options.doc.quantity_unit+"']")).attr("selected", true);
          $(gadget.props.element.querySelector("[name='quantity_unit']")).selectmenu("refresh");
          });
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
        })
        .push(function (){
          $(gadget.props.element.querySelector("select[name=default_address_region]>option[value='"+gadget.options.doc.default_address_region+"']")).attr("selected", true);
          $(gadget.props.element.querySelector("[name='default_address_region']")).selectmenu("refresh");
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
    // Fill nextowner option list
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
          gadget.props.element.querySelector("#list_nextownertitle").innerHTML =
            datalist.innerHTML;
        });
    })


    /////////////////////////////////////////
    // Nextowner title changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
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
                  if (normalized_value != evt.target.value){
                    evt.target.value = normalized_value;
                  }
                  gadget.props.element.querySelector('[name="nextowner"]').value = evt.target.value;
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
                          gadget.props.element.querySelector('[name=nextowner_title]').value=doc.title;
                          gadget.props.element.querySelector('[name=nextowner]').value=doc.title
                        }
                      }
                    );
                    var event = document.createEvent("UIEvents");
                    event.initUIEvent("input", true, true, window, 1);
                    gadget.props.element.querySelector('input[name="nextowner"]').dispatchEvent(event);
                  }
                })
            })
        });
    })


    /////////////////////////////////////////
    // Nextowner changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
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
                          gadget.props.element.querySelector('[name=nextowner]').value=doc.title
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
                    gadget.props.element.querySelector('[name="nextowner_title"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="nextowner_reference"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_city"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_region"]').setAttribute('disabled', 'disabled');
                    gadget.props.element.querySelector('[name="default_address_street_address"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').setAttribute('readOnly', 'readOnly');

                    gadget.props.element.querySelector('[name="nextowner_title"]').value = result.title || "";
                    gadget.props.element.querySelector('[name="nextowner_reference"]').value = result.reference || "";
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
                    gadget.props.element.querySelector('[name="nextowner_title"]').readOnly = false;
                    gadget.props.element.querySelector('[name="nextowner_reference"]').readOnly = false;
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').readOnly = false;
                    gadget.props.element.querySelector('[name="default_address_city"]').readOnly = false;
                    gadget.props.element.querySelector('[name="default_address_region"]').disabled = false;
                    gadget.props.element.querySelector('[name="default_address_street_address"]').readOnly = false;
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').readOnly = false;
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').readOnly = false;

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


    /////////////////////////////////////////
    // Fill previouslocation option list
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
          gadget.props.element.querySelector("#list_previouslocationtitle").innerHTML =
            datalist.innerHTML;
        });
    })


    /////////////////////////////////////////
    // Fill sync flag
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          if (gadget.options.doc.sync_flag == "1"){
            var element = gadget.props.element.querySelector("input[name='sync_flag'][value='1']");
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else{
            var element = gadget.props.element.querySelector("input[name='sync_flag'][value='']");
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }
        })
    })


    /////////////////////////////////////////
    // Fill local validation
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          var element = gadget.props.element.querySelector("input[name=local_validation][value="+gadget.options.doc.local_validation+"]")
          if(element !== null){
            element.setAttribute('checked', 'checked')
            $(element).checkboxradio('refresh')
          }
        })
    })


    ///////////////////////////////
    // Initialize nextowner form
    ///////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.allDocs({
            query: 'portal_type:("Organisation" OR "Organisation Temp") AND title_lowercase: "' + gadget.props.element.querySelector('[name=nextowner_title]').value.toLowerCase() + '"',
            limit: [0, 2]
          });
        })
        .push(function (result) {
          if (result.data.total_rows === 1) {
            return gadget.get(result.data.rows[0].id);
          }
        })
        .push(function (result) {
          var tmp;
          if (result !== undefined) {
            // Fill the product fieldset
            gadget.props.element.querySelector('[name="nextowner_title"]').value = result.title || "";
            gadget.props.element.querySelector('[name="nextowner_reference"]').value = result.reference || "";
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
            gadget.props.element.querySelector('[name="nextowner_title"]').readOnly = false;
            gadget.props.element.querySelector('[name="nextowner_reference"]').readOnly = false;
            gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').readOnly = false;
            gadget.props.element.querySelector('[name="default_address_city"]').readOnly = false;
            $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('enable');
            $(gadget.props.element.querySelector('[name="default_address_region"]')).selectmenu('refresh');
            gadget.props.element.querySelector('[name="default_address_street_address"]').readOnly = false;
            gadget.props.element.querySelector('[name="default_address_zip_code"]').readOnly = false;
            gadget.props.element.querySelector('[name="default_email_coordinate_text"]').readOnly = false;
          }
        })
    })


    /////////////////////////////////////////
    // Previouslocation changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="previouslocation"]'),
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


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
