/*global window, rJS, document, RSVP, loopEventListener, jQuery */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, loopEventListener, $) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {
        textarea_deferred: RSVP.defer()
      };
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
        });
    })
    .declareMethod('render', function (options) {
      var new_element,
        field_json = options.field_json || {},
        value = field_json.value || field_json.default || "";

      this.property_dict.editable = (field_json.editable === 1);
      this.property_dict.name = field_json.key;
      if (this.property_dict.editable) {
        new_element = document.createElement('textarea');

        new_element.value = value;
        new_element.setAttribute('name', this.property_dict.name);
        new_element.setAttribute('title', field_json.title);
        if (field_json.required === 1) {
          new_element.setAttribute('required', 'required');
        }
        /*
        if (field_json.editable !== 1) {
          textarea.setAttribute('readonly', 'readonly');
          textarea.className += "ui-state-readonly";
          // textarea.setAttribute('disabled', 'disabled');
        }
        */
        this.property_dict.textarea_deferred.resolve(new_element);
      } else {
        new_element = document.createElement('pre');
        new_element.setAttribute("class",  "ui-content-non-editable");
        new_element.textContent = value;
      }
      this.property_dict.element.appendChild(new_element);
    })

    .declareMethod('getContent', function () {
      var field,
        value,
        result = {};
      if (this.property_dict.editable) {
        field = this.property_dict.element.querySelector('textarea');
        value = field.value;
      } else {
        field = this.property_dict.element.querySelector('pre');
        value = field.textContent;
      }
      result[this.property_dict.name] = value;
      return result;
    })

    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.textarea_deferred.promise;
        })
        .push(function (textarea) {
          return loopEventListener(
            textarea,
            'focus',
            false,
            function () {
              $(textarea).keyup();
            }
          );
        });
    });

}(window, rJS, document, RSVP, loopEventListener, jQuery));