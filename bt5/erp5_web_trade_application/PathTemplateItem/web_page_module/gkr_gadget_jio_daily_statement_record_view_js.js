/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-daily-statement-record-template")
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

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function (result_list) {
          return gadget.translateHtml(template(options.doc));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          if (gadget.options.jio_key.indexOf('daily_statement_record_module/') == 0){
            var submit_button = gadget.props.element.querySelector("input[type=submit][name=save]");
            submit_button.parentNode.removeChild(submit_button);
            $(gadget.props.element.querySelectorAll('input,textarea')).attr('readonly', true);
            $(gadget.props.element.querySelectorAll('select,input[type=checkbox],input[type=radio]')).attr('disabled', true);
          }

          if (gadget.options.jio_key.indexOf('daily_statement_record_module/') == 0){
            $('<a data-role="button" href="Base_redirectToGeneratedDocumentOf/'+gadget.options.jio_key+'" target="_blank">'+translateString('Go To ERP5')+'</a>').appendTo($(gadget.props.element.querySelector('form')))
          }else {
            var submit_button = gadget.props.element.querySelector("input[type=button][name=create_new_version]");
            if(submit_button){
              submit_button.parentNode.removeChild(submit_button);
            }
          }

          gadget.props.element.querySelector('#state').innerHTML = translateString(getWorkflowState(gadget.options.doc.portal_type, gadget.options.jio_key, gadget.options.doc.sync_flag, gadget.options.doc.local_validation, gadget.options.doc.local_state))

          return gadget.updateHeader({
            title: translateString("Daily Statement Record") + " " + gadget.options.doc.doc_id + " " + (gadget.options.doc.record_revision || 1)
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // New version of the the Daily Statement Record
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
          cloned_doc.portal_type = 'Daily Statement Record Temp';
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
            gadget.props.element.querySelector('form.view-daily-statement-record-form'),
            'submit',
            false,
            function (submit_event) {
              return new RSVP.Queue()
                .push(function () {
                  if (gadget.options.jio_key.indexOf('daily_statement_record_module/') == 0){
                    return;
                  }
                  if (!(gadget.props.element.querySelector('input[name="daily_currency_input_flag"]').checked &&
                        gadget.props.element.querySelector('input[name="daily_purchase_input_flag"').checked &&
                        gadget.props.element.querySelector('input[name="daily_production_input_flag"').checked &&
                        gadget.props.element.querySelector('input[name="daily_sale_input_flag"').checked)){
                    alert(translateString('Please finish four tasks and check all checkboxes'));
                    return;
                  }
                  var i,
                    doc = {
                      // XXX Hardcoded
                      parent_relative_url: "daily_statement_record_module",
                      portal_type: "Daily Statement Record",
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
                  if (doc.sync_flag != "1"){
                    doc.portal_type = 'Daily Statement Record Temp' // For to avoid sync
                  }
                  $("#saveMessage").popup('open');
                  return gadget.put(gadget.options.jio_key, doc);
                })
                .push(function () {
                  gadget.props.element.querySelector("input[type=submit]").disabled = false;
                })
            }
          );
        })
    })


    /////////////////////////////////////////
    // 4 input flags
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          var element = gadget.props.element.querySelector("input[name='daily_currency_input_flag']");
          if (gadget.options.doc.daily_currency_input_flag == "1"){
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else if(gadget.options.jio_key.indexOf('daily_statement_record_module/') != 0){
            $(element).checkboxradio('enable');
          }
        })
        .push(function () {
          var element = gadget.props.element.querySelector("input[name='daily_purchase_input_flag']");
          if (gadget.options.doc.daily_purchase_input_flag == "1"){
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else if(gadget.options.jio_key.indexOf('daily_statement_record_module/') != 0){
            $(element).checkboxradio('enable');
          }
        })
        .push(function () {
          var element = gadget.props.element.querySelector("input[name='daily_production_input_flag']");
          if (gadget.options.doc.daily_production_input_flag == "1"){
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else if(gadget.options.jio_key.indexOf('daily_statement_record_module/') != 0){
            $(element).checkboxradio('enable');
          }
        })
        .push(function () {
          var element = gadget.props.element.querySelector("input[name='daily_sale_input_flag']");
          if (gadget.options.doc.daily_sale_input_flag == "1"){
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else if(gadget.options.jio_key.indexOf('daily_statement_record_module/') != 0){
            $(element).checkboxradio('enable');
          }
        })
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
          if (element !== null){
            element.setAttribute('checked', 'checked')
            $(element).checkboxradio('refresh')
          }
        })
    })


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
