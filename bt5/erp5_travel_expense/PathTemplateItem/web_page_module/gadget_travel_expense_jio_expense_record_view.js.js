/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-expense-record-template")
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

        if (gadget.options.doc.photo_data){
          var preview = gadget.props.element.querySelector('img[name=preview]')
          preview.src = gadget.options.doc.photo_data
          var photo_data = gadget.props.element.querySelector("canvas[name='photo_data']")
          var context = photo_data.getContext('2d');
          var imageObj = new Image();
          imageObj.onload = function() {
            context.canvas.height = this.height;
            context.canvas.width = this.width;
            context.drawImage(this, 0, 0);
          };
          imageObj.src = gadget.options.doc.photo_data;
        }


          if (gadget.options.jio_key.indexOf('expense_record_module/') == 0){
            var submit_button = gadget.props.element.querySelector("input[type=submit][name=save]");
            submit_button.parentNode.removeChild(submit_button);
            $(gadget.props.element.querySelectorAll('input,textarea')).attr('readonly', true);
            $(gadget.props.element.querySelectorAll('select,input[type=checkbox],input[type=radio],input[type=file]')
             ).attr('disabled', true);
          }

          if (gadget.options.jio_key.indexOf('expense_record_module/') != 0){
            var submit_button = gadget.props.element.querySelector("input[type=button][name=create_new_version]");
            if(submit_button){
              submit_button.parentNode.removeChild(submit_button);
            }
          }

          gadget.props.element.querySelector('#state').innerHTML = translateString(getWorkflowState(gadget.options.doc.portal_type, gadget.options.jio_key, gadget.options.doc.sync_flag))

          return gadget.updateHeader({
            title: gadget.options.doc.doc_id + " " + (gadget.options.doc.record_revision || 1)
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // New version of the the Expense Record
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
          cloned_doc.visible_in_html5_app_flag = 1;
          delete cloned_doc.sync_flag;
          cloned_doc.portal_type = 'Expense Record Temp';
          cloned_doc.record_revision = (cloned_doc.record_revision || 1) + 1;

          current_doc.visible_in_html5_app_flag = 0;

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
            gadget.props.element.querySelector('form.view-expense-record-form'),
            'submit',
            false,
            function (submit_event) {
              return new RSVP.Queue()
                .push(function () {
                  if (gadget.options.jio_key.indexOf('expense_record_module/') == 0){
                    return;
                  }
                  var i,
                    doc = {
                      // XXX Hardcoded
                      parent_relative_url: "expense_record_module",
                      portal_type: "Expense Record",
                      doc_id: gadget.options.doc.doc_id,
                      visible_in_html5_app_flag: 1,
                      record_revision: (gadget.options.doc.record_revision || 1),
                      photo_data: gadget.options.doc['photo_data'],
                    };
                  gadget.props.element.querySelector("input[type=submit]")
                                      .disabled = true;
                  for (i = 0; i < submit_event.target.length; i += 1) {
                    // XXX Should check input type instead
                    if (submit_event.target[i].name && submit_event.target[i].type != "submit") {
                      if ((submit_event.target[i].type == "radio" || submit_event.target[i].type == "checkbox") && !submit_event.target[i].checked){
                        continue
                      }
                      if (submit_event.target[i].name=="photo") {
                        if (submit_event.target[i].files.length > 0){
                          var photo_data = gadget.props.element.querySelector('canvas[name="photo_data"]')
                          doc['photo_data'] = photo_data.toDataURL()
                        }
                        continue
                      }
                      doc[submit_event.target[i].name] = submit_event.target[i].value;
                    }
                  }

                  if (doc.sync_flag != "1"){
                    doc.portal_type = 'Expense Record Temp' // For to avoid sync
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
        .push(function(){createResourceSelection(gadget, gadget.options.doc.resource)})
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
    // Photo changed.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="photo"]'),
            "change",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  var file = gadget.props.element.querySelector('input[name="photo"]').files[0];
                  var photo_data = gadget.props.element.querySelector('canvas[name="photo_data"]');
                  new MegaPixImage(file).render(photo_data, { width: 600 }, function(){gadget.props.element.querySelector('img[name="preview"]').src = photo_data.toDataURL();});
                });
            }
          );
        });
    })


    /////////////////////////////////////////
    // Preview clicked.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('img[name="preview"]'),
            "click",
            false,
            function (evt) {
              return new RSVP.Queue()
                .push(function () {
                  // Wait for user to finish typing
                  return RSVP.delay(100);
                })
                .push(function () {
                  $('div[name=large_preview]').popup('open', 0, 0, 'slidedown', 'window');
                  $('div[name=large_preview] img').attr('src', gadget.props.element.querySelector('canvas[name=photo_data]').toDataURL());
                });
            }
          );
        });
    });


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));