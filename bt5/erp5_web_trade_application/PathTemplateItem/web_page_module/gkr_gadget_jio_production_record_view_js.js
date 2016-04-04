/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-production-record-template")
                              .innerHTML,
    template = Handlebars.compile(source);

  var line_count;

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

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function (result_list) {
          return gadget.translateHtml(template(options.doc));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          $(gadget.props.element.querySelectorAll('fieldset')).hide()
          if (gadget.options.jio_key.indexOf('production_record_module/') == 0){
            var submit_button = gadget.props.element.querySelector("input[type=submit][name=save]");
            submit_button.parentNode.removeChild(submit_button);
            $(gadget.props.element.querySelectorAll('input,textarea')).attr('readonly', true);
            $(gadget.props.element.querySelectorAll('select,input[type=checkbox],input[type=radio]')).attr('disabled', true);
          }

          line_count = 0;
          for(var i=1; i<=10; i++){
            if(options.doc["consumed_product_"+i] != undefined && options.doc["consumed_product_"+i] != ""){
              line_count = i
            }
          }

          line_count++;

          for(var i=1; i < line_count; i++){
            $(gadget.props.element.querySelector('fieldset[name=line'+i+']')).show()
          }
          if (line_count > 10){
            $(gadget.props.element.querySelector('button[name=add_line]')).hide()
          }

          if (gadget.options.jio_key.indexOf('production_record_module/') == 0){
            $('<a data-role="button" href="Base_redirectToGeneratedDocumentOf/'+gadget.options.jio_key+'" target="_blank">'+translateString('Go To ERP5')+'</a>').appendTo($(gadget.props.element.querySelector('form')))
          } else {
            var submit_button = gadget.props.element.querySelector("input[type=button][name=create_new_version]");
            if(submit_button){
              submit_button.parentNode.removeChild(submit_button);
            }
          }

          gadget.props.element.querySelector('#state').innerHTML = translateString(getWorkflowState(gadget.options.doc.portal_type, gadget.options.jio_key, gadget.options.doc.sync_flag, gadget.options.doc.local_validation, gadget.options.doc.local_state))

          return gadget.updateHeader({
            title: translateString("Production Record") + " " + gadget.options.doc.doc_id + " " + (gadget.options.doc.record_revision || 1)
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })


    /////////////////////////////////////////
    // New version of the the Production Record
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
          cloned_doc.portal_type = 'Production Record Temp';
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
            gadget.props.element.querySelector('form.view-production-record-form'),
            'submit',
            false,
            function (submit_event) {
              return new RSVP.Queue()
                .push(function () {
                  if (gadget.options.jio_key.indexOf('production_record_module/') == 0){
                    return;
                  }
                  var i,
                    doc = {
                      // XXX Hardcoded
                      parent_relative_url: "production_record_module",
                      portal_type: "Production Record",
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
          var option_array = new Array();
          for (var i = 0; i < result.data.total_rows; i += 1) {
            option_array[i] = {text:result.data.rows[i].value.logical_path || result.data.rows[i].value.title,
                               value:result.data.rows[i].value.category_relative_url}
          }
          createOptions(gadget.props.element.querySelector('[name="quantity_unit"]'), option_array, gadget.options.doc.quantity_unit)
          createOptions(gadget.props.element.querySelector('[name="quantity_unit2"]'), option_array, gadget.options.doc.quantity_unit2)
          createOptions(gadget.props.element.querySelector('[name="quantity_unit3"]'), option_array, gadget.options.doc.quantity_unit3)
          for(var i=1; i <= 10; i++){
            createOptions(gadget.props.element.querySelector('[name="consumed_quantity_unit_'+i+'"]'), option_array, gadget.options.doc['consumed_quantity_unit_'+i])
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
            query: 'portal_type:"Storage Node" AND validation_state:"validated" AND is_my_storage_node:1',
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
    // Fill production use
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          if (gadget.options.doc.production_use == "reclassification"){
            var element = gadget.props.element.querySelector("input[name='production_use'][value='reclassification']");
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else{
            var element = gadget.props.element.querySelector("input[name='production_use'][value='normal']");
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
          if (element != null) {
            element.setAttribute('checked', 'checked')
            $(element).checkboxradio('refresh')
          }
        })
    })


    /////////////////////////////////////////
    // Nextlocation changed.
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
                })
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
    // Consumed product initialization
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          $(gadget.props.element.querySelectorAll('input[name^="consumed_product_"'))
          .each(function(index){
            var event = document.createEvent("UIEvents");
            event.initUIEvent("input", true, true, window, 1);
            this.dispatchEvent(event);
          })
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


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
