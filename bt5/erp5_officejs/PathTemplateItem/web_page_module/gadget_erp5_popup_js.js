/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP, TextEncoder */
(function (window, rJS, RSVP, Handlebars, TextEncoder) {
  "use strict";

  var gadget_klass = rJS(window),
    popup = gadget_klass.__template_element
                         .getElementById("popup_password")
                         .innerHTML,
    popup_template = Handlebars.compile(popup);

/////////////////////////////////////////////////////////////////
// declared methods
/////////////////////////////////////////////////////////////////
  gadget_klass
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")

//////////////////////////////////////////
// Converting from user key to Cryptokey
/////////////////////////////////////////
    .declareMethod('convertKey', function (str) {
      var buffer = new TextEncoder("utf-8").encode(str);
        // We transform the string into an arraybuffer.
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([window.crypto.subtle.digest("SHA-256", buffer),
            window.crypto.subtle.importKey(
              "raw",
              buffer,
              {name: "PBKDF2"
                },
              false,
              ["deriveKey"]
            )
            ]);
        })
        .push(function (my_array) {
          return {
            CryptoKey: my_array[1],
            Salt: my_array[0]
          };
        })
        .push(undefined, function (error) {
          throw error;
        });
    })

//////////////////////////////////////////
// Displaying POPUP function
/////////////////////////////////////////
    .declareMethod('display_popup', function (options) {
      var gadget = this;
      if (options && options.message && options.addkey && options.error) {
        return this.changeState({
          visible: true,
          message: options.message,
          addkey: options.addkey,
          error: options.error
        })
          .push(function () {
            return gadget.notifySubmitted({message: gadget.state.error.error_message,
                                       status: 'failure'});
          });
      }
    })

    .declareMethod('close', function () {
      return this.changeState({
        visible: false
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (modification_dict.hasOwnProperty('visible')) {
        if (gadget.state.visible) {
          if (!gadget.element.classList.contains('visible')) {
            gadget.element.classList.toggle('visible');
          }
        } else {
          if (gadget.element.classList.contains('visible')) {
            gadget.element.classList.remove('visible');
          }
        }
      }

      if (modification_dict.hasOwnProperty('message') && modification_dict.hasOwnProperty('addkey') &&
          modification_dict.hasOwnProperty('error')) {
        //window.top.document.body.addEventListener("click", function (evt) {
          //evt.stopPropagation();
          //evt.preventDefault();
        //}, true);
        gadget.element.innerHTML = popup_template({
          message: gadget.state.message
        });
      }

    })

//////////////////////////////////////////
// Evenet lisener on input
/////////////////////////////////////////

    .declareMethod('add_lisener_input', function (input_pass) {
      var gadget = this;
      input_pass.addEventListener('input', function () {
        gadget.notifySubmitted();
      }, {once: true});
      return;
    })



//////////////////////////////////////////
// Form submit
/////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this,
        input_pass_value,
        input_pass = this.element.querySelector("input.ui-password-overlay");
      if (input_pass.value !== undefined && input_pass.value !== null && input_pass.value !== "") {
        input_pass_value = input_pass.value;
        if (input_pass_value.match(/^(?=[\w\W]*\d)(?=[\w\W]*[a-z])(?=[\w\W]*[A-Z])[0-9a-zA-Z]{8,}$/)) {
          return gadget.convertKey(input_pass_value)
            .push(function (obj) {
              return gadget.state.addkey(obj);
            })
            .push(function () {
              return gadget.notifySubmitted();
            })
            .push(function () {
              return gadget.close();
            })
            .push(function () {
              return gadget.redirect({command: "display", options: {page: 'ojs_sync', auto_repair: 'true'}});
            });
        }
        return gadget.add_lisener_input(input_pass)
          .push(function () {
            return gadget.notifySubmitted({message: 'Passwords must contain: \n' +
              'a lower case letter [a-z]  \n' +
              'a upper case letter [A-Z]  \n' +
              'a numeric character [0-9] and \n ' +
              'at least 8 characters in length', status: 'failure'});
          });
      }
      return gadget.notifySubmitted({message: 'no field found', status: 'failure'});
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    });

    //.onEvent('click', function (evt) {
      //if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
        // (evt.target.tagName === 'BUTTON')) {
        //return this.close();
      //}
    //}, false, false);

}(window, rJS, RSVP, Handlebars, TextEncoder));