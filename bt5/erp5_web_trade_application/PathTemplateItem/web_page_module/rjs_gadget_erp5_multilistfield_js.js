/*global window, rJS, Handlebars, document, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars, document, RSVP) {
  'use strict';
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
      g.props = {};
    })
    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareMethod('render', function (options) {
      var gadget = this,
        selects = [],
        tmp,
        template,
        container,
        field_json = options.field_json,
        i,
        j;
      gadget.props.field_json = field_json;
      container = gadget.props.element.querySelector(".ui-controlgroup-controls");
      field_json.default[field_json.default.length] = "";
      for (i = 0; i < field_json.default.length; i += 1) {
        tmp = "";
        selects[i] = document.createElement("select");
        container.appendChild(selects[i]);
        for (j = 0; j < field_json.items.length; j += 1) {
          if (field_json.items[j][1] === field_json.default[i]) {
            template = selected_option_template;
          } else {
            template = option_template;
          }
          tmp += template({
            value: field_json.items[j][1],
            text: field_json.items[j][0]
          });
        }
        selects[i].innerHTML = tmp;
      }
      return new RSVP.Queue()
        .push(function () {
          var list = [];
          for (i = 0; i < selects.length; i += 1) {
            list.push(gadget.translateHtml(selects[i].outerHTML));
          }
          return RSVP.all(list);
        })
        .push(function (translated_htmls) {
          var select_div,
            wrapper_class_string,
            div = document.createElement("div");
          for (i = 0; i < translated_htmls.length; i += 1) {
            div.innerHTML = translated_htmls[i];
            select_div = div.querySelector("select");
            selects[i].innerHTML = select_div.innerHTML;
            if (field_json.editable !== 1) {
              selects[i].setAttribute('readonly', 'readonly');
              wrapper_class_string = wrapper_class_string || "";
              wrapper_class_string += 'ui-state-readonly ';
            }
            // XXX add first + last class, needs to be improved
            if (i === 0) {
              wrapper_class_string = wrapper_class_string || "";
              wrapper_class_string += 'ui-first-child';
            }
            if (i === translated_htmls.length - 1) {
              wrapper_class_string = wrapper_class_string || "";
              wrapper_class_string += 'ui-last-child';
            }
            if (wrapper_class_string) {
              selects[i].setAttribute('data-wrapper-class', wrapper_class_string);
              wrapper_class_string = undefined;
            }
          }
        });
    })
    .declareMethod('getContent', function () {
      var gadget = this,
        result = {},
        tmp = [],
        selects = this.props.element.querySelectorAll('select'),
        i;

      for (i = 0; i < selects.length; i += 1) {
        tmp.push(selects[i].options[selects[i].selectedIndex].value);
      }
      result[gadget.props.field_json.sub_select_key] = tmp;
      result[gadget.props.field_json.sub_input_key] = 0;
      return result;
    });
}(window, rJS, Handlebars, document, RSVP));