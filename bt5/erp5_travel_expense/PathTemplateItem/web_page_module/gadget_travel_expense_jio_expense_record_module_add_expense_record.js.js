/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $, MegaPixImage) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".new-expense-record-template")
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
          return gadget.updateHeader({
            title: "New Expense Record"
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
            gadget.props.element.querySelector('form.new-expense-record-form'),
            'submit',
            false
          );
        })
        .push(function (submit_event) {
          var i,
            doc = {
              // XXX Hardcoded
              parent_relative_url: "expense_record_module",
              portal_type: "Expense Record",
              doc_id: getSequentialID('EXP'),
              visible_in_html5_app_flag: 1,
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
              if (submit_event.target[i].name=="photo") {
                if (submit_event.target[i].files.length > 0){
                  var photo_data = gadget.props.element.querySelector('canvas[name="photo_data"]')
                  doc['photo_data'] = photo_data.toDataURL()
                }else{
                  doc['photo_data'] = ''
                }
                continue
              }
              doc[submit_event.target[i].name] = submit_event.target[i].value;
            }
          }
          if (doc.sync_flag != "1"){
            doc.portal_type = 'Expense Record Temp' // For to avoid sync
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
        .push(function(){createResourceSelection(gadget, my_resource)})
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


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery, MegaPixImage));