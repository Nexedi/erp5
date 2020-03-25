/*global window, rJS, JSLINT, document */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, JSLINT, window, document) {
  "use strict";

  rJS(window)
    .declareMethod("render", function (options) {
      var text_content = options.value,
        data,
        html_content,
        i,
        line_letter = "A",
        len,
        gadget = this,
        fragment = document.createDocumentFragment(),
        td_element,
        tr_element;
      JSLINT(text_content, {});
      data = JSLINT.data();

      for (i = 0, len = data.errors.length; i < len; i += 1) {
        if (data.errors[i] !== null) {
          tr_element = document.createElement('tr');
          tr_element.setAttribute('class', 'Data' + line_letter);
          line_letter = (line_letter === "A") ? "B" : "A";
          fragment.appendChild(tr_element);

          td_element = document.createElement('td');
          td_element.setAttribute('class', 'listbox-table-data-cell');
          td_element.textContent = "line: " + data.errors[i].line + ": " +
                                   data.errors[i].character + ": " +
                                   data.errors[i].evidence;
          tr_element.appendChild(td_element);

          td_element = document.createElement('td');
          td_element.setAttribute('class', 'listbox-table-data-cell');
          td_element.textContent = data.errors[i].reason;
          tr_element.appendChild(td_element);
        }
      }
      if (len === 0) {
        tr_element = document.createElement('tr');
        tr_element.setAttribute('class', 'DataA');
        fragment.appendChild(tr_element);

        td_element = document.createElement('td');
        td_element.textContent = "No error!";
        tr_element.appendChild(td_element);
      }

      gadget.element.querySelector("tbody").appendChild(fragment);
    });
}(rJS, JSLINT, window, document));