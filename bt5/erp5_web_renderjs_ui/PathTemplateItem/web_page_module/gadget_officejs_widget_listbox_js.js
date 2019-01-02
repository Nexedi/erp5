/*global window, rJS, RSVP, Handlebars, loopEventListener */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Handlebars, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    listbox_widget_table = Handlebars.compile(
      templater.getElementById("listbox-widget-table").innerHTML
    );
  Handlebars.registerPartial(
    "listbox-widget-table-partial",
    templater.getElementById("listbox-widget-table-partial").innerHTML
  );

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.property_dict = {
        render_deferred: RSVP.defer()
      };
    })

    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (option_dict) {
      var gadget = this,
        content = '',
        k,
        k_len,
        search_list = [],
        translated_column_list = [],
        all_docs_result;

      // store initial configuration
      gadget.property_dict.option_dict = option_dict;

      // Create the search query
      if (option_dict.search) {
        for (k = 0, k_len = option_dict.column_list.length; k < k_len; k += 1) {
          search_list.push(option_dict.column_list[k].select + ':"%' + option_dict.search + '%"');
        }
        option_dict.query.query = '(' + search_list.join(' OR ') + ') AND ' + option_dict.query.query;
      }
      return gadget.jio_allDocs(option_dict.query)
        .push(function (result) {
          var promise_list = [],
            i_len,
            i;
          all_docs_result = result;
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {
            promise_list.push(gadget.getUrlFor({jio_key: result.data.rows[i].id, page: 'view'}));
          }

          return RSVP.all(promise_list);
        })
        .push(function (link_list) {
          var row_list = [],
            cell_list,
            i_len,
            i,
            j_len,
            j;

          // build handlebars object

          for (j = 0, j_len = all_docs_result.data.total_rows; j < j_len; j += 1) {
            cell_list = [];
            for (i = 0, i_len = option_dict.column_list.length; i < i_len; i += 1) {
              cell_list.push({
                "href": link_list[j],
                "value": all_docs_result.data.rows[j].value[option_dict.column_list[i].select]
              });
            }
            row_list.push({"cell_list": cell_list});
          }

          for (i = 0; i < option_dict.column_list.length; i += 1) {
            translated_column_list.push(gadget.translate(option_dict.column_list[i].title));
          }
          return RSVP.all([
            row_list,
            RSVP.all(translated_column_list)
          ]);
        })
        .push(function (result_list) {
          content += listbox_widget_table({
            widget_theme : option_dict.widget_theme,
            search: option_dict.search,
            column_list: result_list[1],
            row_list: result_list[0]
          });

          gadget.property_dict.element.querySelector(".custom-grid .ui-body-c")
            .innerHTML = content;
          gadget.property_dict.render_deferred.resolve();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.property_dict.element.querySelector('form'),
            'submit',
            false,
            function (evt) {
              return gadget.redirect({
                jio_key: gadget.property_dict.option_dict.jio_key || '',
                page: gadget.property_dict.option_dict.search_page || '',
                search: evt.target[0].value
              });
            }
          );
        });
    });

}(window, rJS, RSVP, Handlebars, loopEventListener));