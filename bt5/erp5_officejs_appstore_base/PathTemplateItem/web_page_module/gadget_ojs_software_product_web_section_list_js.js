/*global window, rJS, RSVP, Handlebars, jQuery */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, Handlebars, $) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareMethod("render", function (options) {
      console.log(options);
      var gadget = this,
        id = options.value;
      return gadget.jio_getAttachment(id, "view")
        .push(function (result) {
          var list_method_template;
          console.log(result);
          list_method_template = result._embedded._view.listbox.list_method_template;
          return gadget.jio_allDocs({
              list_method_template: list_method_template,
              select_list: ['relative_url', 'title', 'id'],
              sort_on:[["modification_date","descending"],]
            });
       })
        .push(function (result) {
          console.log(result);
          var i, i_len, version_list = [];
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            // XX Should do that during query
            if (result.data.rows[i].value.id !== "hateoas") {
              version_list.push({
                title: result.data.rows[i].value.title,
                link: result.data.rows[i].value.relative_url + "/",
              });
            }
          }
          gadget.props.element.innerHTML = table_template({
            documentlist: version_list
          });
          $(gadget.props.element).enhanceWithin();
          return true;
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return true;
        });
    });


}(window, rJS, RSVP, Handlebars, jQuery));