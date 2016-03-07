/*global window, rJS, JSLINT, Handlebars */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, Handlebars, JSLINT, window) {
  "use strict";
  var gk = rJS(window),
    template_source = gk.__template_element
                        .getElementById('jslint_template')
                        .innerHTML,
    template = Handlebars.compile(template_source);

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement().push(function (element) {
        g.props.element = element;
      });
    })

    .declareMethod("render", function (options) {
      var text_content = options.value,
        data,
        html_content,
        i,
        line_letter = "A",
        len,
        gadget = this;
      JSLINT(text_content, {});
      data = JSLINT.data();

      for (i = 0, len = data.errors.length; i < len; i += 1) {
        if (data.errors[i] !== null) {
          data.errors[i].line_letter = line_letter;
          line_letter = line_letter === "A" ? "B" : "A";
        }
      }
      html_content = template({
        error_list: data.errors
      });

      gadget.props.element.querySelector("tbody")
                          .innerHTML = html_content;
    });
}(rJS, Handlebars, JSLINT, window));