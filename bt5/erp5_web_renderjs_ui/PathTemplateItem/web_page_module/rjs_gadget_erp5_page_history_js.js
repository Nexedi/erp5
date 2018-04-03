/*global window, rJS, RSVP, Handlebars, SimpleQuery, ComplexQuery, Query */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, SimpleQuery, ComplexQuery, Query) {
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
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        id_list = options.id_list || [],
        header_dict = {
          page_title: 'History',
          page_icon: 'history'
        };

      return gadget.getUrlFor({command: 'display'})
        .push(function (front_url) {
          header_dict.front_url = front_url;
          return gadget.updateHeader(header_dict);
        })
        .push(function () {
          var i,
            query_list = [];
          for (i = 0; i < id_list.length; i += 1) {
            query_list.push(new SimpleQuery({key: 'relative_url', value: id_list[i]}));
          }
          if (i === 0) {
            return {
              data: {
                rows: []
              }
            };
          }
          return gadget.jio_allDocs({
            query: Query.objectToSearchText(new ComplexQuery({operator: 'OR', query_list: query_list})),
            select_list: ["title", "translated_portal_type"],
            limit: id_list.length
          });
        })
        .push(function (result) {
          var result_list = [],
            i;
          for (i = 0; i < result.data.rows.length; i += 1) {
            result_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display', options: {jio_key: result.data.rows[i].id}}),
              result.data.rows[i].value,
              result.data.rows[i].id
            ]));
          }
          return RSVP.all(result_list);
        })
        .push(function (result_list) {
          var i,
            document_list = [],
            document_dict = {};

          for (i = 0; i < result_list.length; i += 1) {
            document_dict[result_list[i][2]] = {
              link: result_list[i][0],
              title: (result_list[i][1].title || result_list[i][2]) + " (" + result_list[i][1].translated_portal_type + ")"
            };
          }
          // Sort by access time
          for (i = 0; i < id_list.length; i += 1) {
            if (document_dict.hasOwnProperty(id_list[i])) {
              document_list.push(document_dict[id_list[i]]);
            }
          }
          return gadget.translateHtml(table_template({document_list: document_list}));
        })
        .push(function (translated_html) {
          gadget.element.querySelector('.document_list').innerHTML  = translated_html;
        });
    });
}(window, rJS, RSVP, Handlebars, SimpleQuery, ComplexQuery, Query));