/*global window, document, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
/**
 * Label gadget takes care of displaying validation errors and label.
 *
 * Every form field is wrapped in that widget which has some consequences:
 *
 * -  CSS classes sharing: label copy CSS classes of embedded field for itself
 *    because CSS selectors are not good in selectin up the DOM tree
 *    -  class "invisible" despite its name is supposed to hide only label
 *    -  class "horizontal_align_form_box" will prevent any label to show as well
 *
 */
(function (window, document, rJS, RSVP) {
  "use strict";

  var SCOPE = 'field';

  rJS(window)
    .setState({
      label_text: '',
      error_text: '',
      label: true,
      css_class: ''
    })

    .ready(function () {
      return this.changeState({
        label_element: this.element.querySelector('label'),
        label_text_element: this.element.querySelector('label').firstChild,
        error_element: this.element.querySelector('span'),
        container_element: this.element.querySelector('div')
      });
    })

    .declareMethod('render', function (options) {
      var state_dict = {
        label_text: options.field_json.title || '',
        label: options.label,
        field_url: options.field_url,
        error_text: options.field_json.error_text || '',
        options: options,
        scope: options.field_json.key,
        hidden: options.field_json.hidden,
        css_class: options.field_json.css_class
      };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        span;

      if (gadget.state.hidden) {
        this.element.hidden = true;
      } else {
        this.element.hidden = false;
      }

      if (modification_dict.hasOwnProperty('label_text')) {
        this.state.label_text_element.textContent = this.state.label_text;
      }
      this.state.label_element.setAttribute('for', gadget.state.scope);

      if (modification_dict.hasOwnProperty('css_class') && this.state.css_class) {
        this.state.label_element.classList.add(this.state.css_class);
      }

      if (modification_dict.hasOwnProperty('error_text')) {
        this.state.error_element.textContent = "";
        if (this.state.error_text) {
          span = document.createElement('span');
          span.textContent = this.state.error_text;
          this.state.error_element.appendChild(span);
        }
      }

      // Remove/add label_element from DOM
      if (modification_dict.hasOwnProperty('label')) {
        if (this.state.label === true) {
          this.state.container_element.insertBefore(this.state.label_element, this.state.container_element.firstChild);
        } else {
          this.state.container_element.removeChild(this.state.label_element);
        }
      }

      if (modification_dict.hasOwnProperty('options')) {
        if (this.state.field_url) {
          return new RSVP.Queue()
            .push(function () {
              if (modification_dict.hasOwnProperty('field_url')) {
                return gadget.declareGadget(gadget.state.field_url, {
                  scope: SCOPE
                })
                  .push(function (field_gadget) {
                    gadget.state.container_element.removeChild(
                      gadget.state.container_element.querySelector('div')
                    );
                    gadget.state.container_element.appendChild(field_gadget.element);
                    return field_gadget;
                  });
              }
              return gadget.getDeclaredGadget(SCOPE);
            })
            .push(function (field_gadget) {
              return field_gadget.render(gadget.state.options);
            });
        }
      }
    })

    .declareMethod("checkValidity", function () {
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          // XXX Implement checkValidity on all fields
          if (gadget.checkValidity !== undefined) {
            return gadget.checkValidity();
          }
          return true;
        });
    })

    .declareMethod('getContent', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          if (gadget.getContent !== undefined) {
            return gadget.getContent.apply(gadget, argument_list);
          }
          return {};
        });
    })

    .declareMethod('getListboxInfo', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          return gadget.getListboxInfo.apply(gadget, argument_list);
        });
    })

    .allowPublicAcquisition("notifyInvalid", function (param_list) {
      return this.changeState({error_text: param_list[0]});
    })

    .allowPublicAcquisition("notifyValid", function () {
      return this.changeState({error_text: ''});
    });

}(window, document, rJS, RSVP));