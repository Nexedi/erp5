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
    .declareAcquiredMethod("renderEditorPanel", "renderEditorPanel")

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
        searchable_column_list = option_dict.column_list,
        sort_list = option_dict.sort_list,
        all_docs_result;

      // store initial configuration
      gadget.property_dict.option_dict = option_dict;

      // Create the search query
      if (option_dict.search) {
        var extra_search_columns = option_dict.hidden_column_list;
        if (extra_search_columns) searchable_column_list = searchable_column_list.concat(extra_search_columns);
        for (k = 0, k_len = searchable_column_list.length; k < k_len; k += 1) {
          search_list.push(searchable_column_list[k].select + ':"%' + option_dict.search + '%"');
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
            //promise_list.push(gadget.getUrlFor({jio_key: result.data.rows[i].id, page: 'view'}));
            console.log(gadget.getUrlFor({jio_key: result.data.rows[i].id, page: 'view'}));
            var url = result.data.rows[i].value.url;
            promise_list.push({
              "link": url
            });
          }

          //return RSVP.all(promise_list);
          return promise_list;
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
                "href": link_list[j].link,
                "value": all_docs_result.data.rows[j].value[option_dict.column_list[i].select],
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
            widget_theme: option_dict.widget_theme,
            search: option_dict.search,
            column_list: result_list[1],
            row_list: result_list[0],
            num: result_list[0].length
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
            gadget.property_dict.element.querySelector('#search'),
            'submit',
            false,
            function (evt) {
              return gadget.redirect({
                command: "search",
                options: {
                  jio_key: gadget.property_dict.option_dict.jio_key || '',
                  page: gadget.property_dict.option_dict.search_page || '',
                  search: evt.target[0].value
                }
              });
            }
          );
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.property_dict.element.querySelector('#delete'),
            'submit',
            false,
            function (evt) {
              return gadget.redirect({
                command: "remove_search",
                options: {
                  jio_key: gadget.property_dict.option_dict.jio_key || '',
                  page: gadget.property_dict.option_dict.search_page || '',
                  search: evt.target[0].value,
                }
              });
            }
          );
        });
    })
    /*
    .declareService(function () {
      var gadget = this;
      
      return loopEventListener(
        gadget.property_dict.element.querySelector('#filter'),
        'submit',
        false,
        function (evt) {
          return gadget.renderEditorPanel(
            "gadget_erp5_search_editor.html",
            {
              search_column_list: gadget.property_dict.option_dict.column_list,
              begin_from: "",
              extended_search: "",
            }
          );
        }
      );
    })
    */
    .declareService(function () {
      var gadget = this,
        column_list;
      
      function objToArray(obj) {
        return [obj.select, obj.title];
      }
      
      function hasTitle(obj) {
        return obj.title !== '';
      }
      
      column_list = gadget.property_dict.option_dict.column_list.filter(hasTitle)
                                                                .map(objToArray);
                                                                
      return loopEventListener(
        gadget.property_dict.element.querySelector('button[name="Sort"]'),
        'click',
        false,
        function (evt) {
          return gadget.renderEditorPanel(
            "gadget_erp5_sort_editor.html",
            {
              sort_column_list: column_list,
              key: 'sort_on',
              sort_list: gadget.property_dict.option_dict.sort_list || [],
            }
          );
        }
      );
    });
}(window, rJS, RSVP, Handlebars, loopEventListener));


