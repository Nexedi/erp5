/*global window, rJS, RSVP, Handlebars, jIO, location, console */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, Handlebars, RSVP, window) {
  "use strict";
  var gk = rJS(window);

  function output(inp) {
    document.body.appendChild(document.createElement('pre')).innerHTML = inp;
  }

  function syntaxHighlight(json) {
      json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
          var cls = 'number';
          if (/^"/.test(match)) {
            if (/:$/.test(match)) {
              cls = 'key';
            } else {
              cls = 'string';
            }
          } else if (/true|false/.test(match)) {
            cls = 'boolean';
          } else if (/null/.test(match)) {
            cls = 'null';
          }
          return '<span class="' + cls + '">' + match + '</span>';
        });
    }

  rJS(window)

    .declareMethod('render', function (options) {
      var patch = options.value;
      console.log(patch);
      // this.element.innerHTML = output(patch);
      this.element.innerHTML = '<pre>'+syntaxHighlight(JSON.stringify(JSON.parse(patch), undefined, 1))+'</pre>';
    });

}(rJS, jIO, Handlebars, RSVP, window));
