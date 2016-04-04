/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".new-daily-statement-record-template")
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
          return gadget.updateHeader({
            title: "New Daily Statement Record"
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
      var dont_save = false;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return loopEventListener(
            gadget.props.element.querySelector('form.new-daily-statement-record-form'),
            'submit',
            false,
            function (submit_event) {
              return new RSVP.Queue()
                .push(function(){
                  if (!(gadget.props.element.querySelector('input[name="daily_currency_input_flag"]').checked &&
                        gadget.props.element.querySelector('input[name="daily_purchase_input_flag"').checked &&
                        gadget.props.element.querySelector('input[name="daily_production_input_flag"').checked &&
                        gadget.props.element.querySelector('input[name="daily_sale_input_flag"').checked)){
                    alert(translateString('Please finish four tasks and check all checkboxes'));
                    dont_save = true;
                    return;
                  }
                  dont_save = false;
                  var i,
                    doc = {
                      // XXX Hardcoded
                      parent_relative_url: "daily_statement_record_module",
                      portal_type: "Daily Statement Record",
                      doc_id: getSequentialID('DSR'),
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
                    doc.portal_type = 'Daily Statement Record Temp' // For to avoid sync
                  }
                  return gadget.post(doc);
                })
                .push(function () {
                  if(dont_save == true){
                    return;
                  }
                  return gadget.redirect({
                    jio_key: gadget.props.options.jio_key,
                    page: "view"
                  });
                });
            })
        })
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
