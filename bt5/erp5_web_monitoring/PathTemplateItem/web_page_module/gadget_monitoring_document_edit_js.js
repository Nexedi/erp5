/*global document, window, rJS, $ */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, document, rJS, $) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    parameters_widget_template = Handlebars.compile(
      templater.getElementById("monitor-parameters-template").innerHTML
    );

  function getFormDataList(formElement, parameter_list) {
    var i,
      formData_list = [];
    for (i = 0; i < parameter_list.length; i += 1) {
      formData_list.push(parameter_list[i]);
      if (parameter_list[i].key) {
        // Editable fields
        if (formElement.querySelector('input[name="' + parameter_list[i].key + '"]').value !== undefined) {
          formData_list[i].value = formElement.querySelector('input[name="' +
            parameter_list[i].key + '"]').value;
        }
      }
    }
    return formData_list;
  }

  function saveDocument(gadget, document_id, jio_document) {
    // Authenticate before save
    return gadget.props.jio_gadget.put(document_id, jio_document)
      .push(function (result) {
        return {status: 'OK'};
      }, function (error) {
        console.log(error);
        return {status: 'ERROR', code: error.target.status};
      });
  }

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          gadget.props.jio_gadget = jio_gadget;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
      .push(function () {
          gadget.props.jio_gadget.createJio({
            type: "query",
            sub_storage: {
              type: "drivetojiomapping",
              sub_storage: {
                type: "dav",
                url: options.url,
                basic_login: options.basic_login
              }
            }
          });
          gadget.props.options = options;
          return gadget.props.deferred.resolve();
        });
    })
    .declareMethod("popupEdit", function (options, updateMethod) {
      var gadget = this,
        title = 'Edit - ' + options.title,
        html_form = '';
      html_form = parameters_widget_template({
        parameter_list: options.parameters || []
      });

      gadget.props.element.querySelector('.form-controlgroup')
        .innerHTML = html_form;
      gadget.props.element.querySelector('.ui-promise-title h2')
        .textContent = title;

      return new RSVP.Queue()
        .push(function () {
          return $.magnificPopup.open({
            items: {
                src: '.white-popup',
                type: 'inline'
            },
            closeBtnInside: true,
            callbacks: {
              open: function() {
                return new RSVP.Queue()
                  .push(function () {
                    return $('.white-popup form').trigger("create");
                  })
                  .push(function () {
                    var promise_list = [];

                    promise_list.push(loopEventListener(
                      document.querySelector('.mfp-content form .cancel'),
                      'click',
                      false,
                      function (evt) {
                        return $.magnificPopup.close();
                      }
                    ));
                    promise_list.push(loopEventListener(
                      document.querySelector('.mfp-content form .save'),
                      'click',
                      false,
                      function (evt) {
                        var data = getFormDataList(
                          document.querySelector('.mfp-content form'),
                          options.parameters);
                        return new RSVP.Queue()
                          .push(function () {
                            $(document.querySelector('.mfp-content spinner'))
                              .toggleClass('ui-content-hidden');
                            return RSVP.all([saveDocument(
                              gadget,
                              options.document_id,
                              data
                            )]);
                          })
                          .push(function (result) {
                            if (result[0].status === 'ERROR') {
                              document.querySelector('.mfp-content .ui-text-error')
                                .innerHTML = 'ERROR ' + result[0].code +
                                  ': Failed to save your document! ' +
                                  "Parameters cannot be saved in Offline mode.";
                            } else {
                              $.magnificPopup.close();
                              return updateMethod(data);}
                          })
                          .push(function () {
                            $(document.querySelector('.mfp-content spinner'))
                              .toggleClass('ui-content-hidden');
                          });
                      }
                    ));
                    return RSVP.all(promise_list);
                  });
              },
              close: function() {
                // Will fire when popup is closed
                $('.white-popup').remove();
              }
            }
          });
        })
        .push(function () {
          return gadget.props.deferred.resolve();
        });
    })


    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

        });
    });

}(window, document, rJS, $));