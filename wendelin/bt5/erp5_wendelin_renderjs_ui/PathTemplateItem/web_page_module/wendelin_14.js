/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener,
          loopEventListener, jQuery, console, jIO*/
/*jslint indent: 2, maxerr: 30, nomen:true */
(function () {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("contact-list-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

  // Ivan: we extend gadget API like so:
  rJS(window).declareMethod('render', function () {
    var gadget = this,
      html;
    return gadget.aq_allDocs()
      .push(function (result) {
        var promise_list = [],
          len = result.data.rows.length,
          i;
        for (i = 0; i < len; i += 1) {
          promise_list.push(result.data.rows[i].id);
        }
        return RSVP.all(promise_list);
      })
      .push(function (rows) {
        // posts contains an array of results for the given promises
        var new_url_list = [],
          len = rows.length,
          i;
        for (i = 0; i < len; i += 1) {
          // XXX: renderjs generate URL ?
          new_url_list.push({'url': '#page=show&id=' + rows[i],
                             'id': rows[i]});
        }
        html = table_template({'url_list': new_url_list});
        return gadget.getElement();
      })
      .push(function (element) {
        // append produced HTML
        element.innerHTML = html;
      });

  })

    // ivan: decalre we want to use JIO functionality as an alias (aq_post)
    .declareAcquiredMethod("aq_allDocs", "jio_allDocs");

}());