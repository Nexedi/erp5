/*global window, rJS, Handlebars, document, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars, document, RSVP) {
  "use strict";

  function notifyValid(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.notifyValid();
      });
  }

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    option_source = gadget_klass.__template_element
                      .getElementById("option-template")
                      .innerHTML,
    option_template = Handlebars.compile(option_source),
    selected_option_source = gadget_klass.__template_element
                               .getElementById("selected-option-template")
                               .innerHTML,
    selected_option_template = Handlebars.compile(selected_option_source);

  gadget_klass
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props = {};
          g.element = element;
        });
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareMethod('getTextContent', function () {
      var select = this.element.querySelector('select');
      return select.options[select.selectedIndex || 0].text;
    })
    .declareMethod('render', function (options) {
      var i,
        template,
        input,
        gadget = this,
        select = this.element.querySelector('select'),
        field_json = options.field_json,
        tmp = "",
        wrap = document.createElement("select");

      if (this.props.gadget_created !== undefined) {
        if (field_json.default !== undefined) {
          notifyValid(this);
          input = select.querySelector('[value="' + field_json.default + '"]');
          if (field_json.disabled === 1) {
            select.setAttribute('disabled', 'disabled');
          }
          input.selected = 'selected';
        } else {
          select.disabled = false;
          input = select.querySelector('[value=""]');
          input.selected = 'selected';
        }
      } else {
        this.props.gadget_created = true;
        select.setAttribute('name', field_json.key);
        for (i = 0; i < field_json.items.length; i += 1) {
          if (field_json.items[i][1] === field_json.default) {
            template = selected_option_template;
          } else {
            template = option_template;
          }
          tmp += template({
            value: field_json.items[i][1],
            text: field_json.items[i][0]
          });
        }

      // need a <select> for transport
        wrap.innerHTML = tmp;

        return new RSVP.Queue()
          .push(function () {
            return gadget.translateHtml(wrap.outerHTML);
          })
          .push(function (my_translated_html) {
            // XXX: no fan...
            var select_div,
              div = document.createElement("div");

            div.innerHTML = my_translated_html;

            select_div = div.querySelector("select");
            select.innerHTML = select_div.innerHTML;

            if (field_json.required === 1) {
              select.setAttribute('required', 'required');
            }
            if (field_json.editable !== 1) {
              select.setAttribute('readonly', 'readonly');
              select.setAttribute('data-wrapper-class', 'ui-state-readonly');
              // select.setAttribute('disabled', 'disabled');

            }
          });
      }
    })
    .declareMethod('checkValidity', function () {
      var result;
      result = this.element.querySelector('select').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })
    .declareMethod('getContent', function () {
      var input = this.element.querySelector('select'),
        result = {};
      result[input.getAttribute('name')] = input.options[input.selectedIndex].value;
      return result;
    })
    .declareService(function () {
      ////////////////////////////////////
      // Check field validity when the value changes
      ////////////////////////////////////
      var field_gadget = this;

      function notifyChange() {
        return RSVP.all([
          field_gadget.checkValidity(),
          field_gadget.notifyChange()
        ]);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('select'),
        'change',
        false,
        notifyChange
      );
    })
    .declareService(function () {
      ////////////////////////////////////
      // Inform when the field input is invalid
      ////////////////////////////////////
      var field_gadget = this;

      function notifyInvalid(evt) {
        return field_gadget.notifyInvalid(evt.target.validationMessage);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('select'),
        'invalid',
        false,
        notifyInvalid
      );
    });

}(window, rJS, Handlebars, document, RSVP));