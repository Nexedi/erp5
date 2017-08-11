/*global document, window, rJS, $ */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, document, rJS, $) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    hashCode = new Rusha().digestFromString;

  /*function getHtmlFromJson(parameter_list) {
    var i,
      html_content = '';

    for (i = 0; i < parameter_list.length; i += 1) {
      html_content += '<span class="label-text">' + parameter_list[i].title + ':</span>\n';
      if (parameter_list[i].key) {
        html_content += '<input type="text" name="' + parameter_list[i].key +
          '" placeholder="' + parameter_list[i].title + '" value="' +
          parameter_list[i].value +'" data-mini="true">\n';
      } else {
        html_content += '<input type="text" name="' + parameter_list[i].key +
          '" placeholder="' + parameter_list[i].title + '" value="'+
          parameter_list[i].value +'" data-mini="true" disabled="disabled">\n';
      }
    }
    return html_content;
  }

  function getFormDataList(formElement, parameter_list) {
    var i,
      formData_list = [];
    for (i = 0; i < parameter_list.length; i += 1) {
      formData_list.push(parameter_list[i]);
      if (parameter_list[i].key) {
        // Editable fields
        if (formElement.querySelector('input[name="' + parameter_list[i].key + '"]').value !== undefined) {
          formData_list[i].value = formElement.querySelector('input[name="' + parameter_list[i].key + '"]').value;
        }
      }
    }
    return formData_list;
  }

  function saveDocument(gadget, jio_document) {
    // Authenticate before save
    return gadget.props.login_gadget.getUrlInfo(
        hashCode(gadget.props.options.url)
      )
      .push(function (cred) {
        var url = gadget.props.options.url;
        if (gadget.props.options.path) {
          url += (url.endsWith('/') ? '':'/') + gadget.props.options.path;
        }
        if (cred === undefined) {
          cred = {};
        }
        gadget.props.jio_gadget.createJio({
          type: "query",
          sub_storage: {
            type: "drivetojiomapping",
            sub_storage: {
              type: "dav",
              url: url,
              basic_login: cred.hash
            }
          }
        }, false);
        return gadget.props.jio_gadget.put(gadget.props.options.key, jio_document);
      })
      .push(function (result) {
        return {status: 'OK'};
      }, function (error) {
        console.log(error);
        return {status: 'ERROR', code: error.target.status};
      });
    
  }*/

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
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("login_gadget")
        .push(function (login_gadget) {
          gadget.props.login_gadget = login_gadget;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
      .push(function () {
          return gadget.props.deferred.resolve();
        });
    })
    .declareMethod("popupEdit", function (options, updateMethod) {
      var gadget = this,
        title = 'Edit ' + (options.title || 'Monitoring Parameters'),
        html_form = '';

      gadget.props.options = options;
      /*html_form = getHtmlFromJson(options.parameters || []);

      gadget.props.element.querySelector('.form-controlgroup')
        .innerHTML = html_form;
      gadget.props.element.querySelector('.ui-promise-title h2')
        .innerHTML = title;*/

      return new RSVP.Queue()
        /*.push(function () {
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
                        var data = getFormDataList(document.querySelector('.mfp-content form'), options.parameters);
                        return new RSVP.Queue()
                          .push(function () {
                            $(document.querySelector('.mfp-content spinner')).toggleClass('ui-content-hidden');
                            return RSVP.all([saveDocument(gadget, data)]);
                          })
                          .push(function (result) {
                            if (result[0].status === 'ERROR') {
                              document.querySelector('.mfp-content .ui-text-error')
                                .innerHTML = 'ERROR ' + result[0].code + ': Failed to save your document! ' +
                                  "Parameters cannot be saved in Offline mode.";
                            } else {
                              $.magnificPopup.close();
                              return updateMethod(data);}
                          })
                          .push(function () {
                            $(document.querySelector('.mfp-content spinner')).toggleClass('ui-content-hidden');
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
        })*/
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