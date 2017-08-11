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
  var formatDate = function(d) {
    function addZero(n) {
      return n < 10 ? '0' + n : '' + n;
    }

    return d.getFullYear() + "-" + addZero(d.getMonth()+1)
      + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
      + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
  };

  function renderFomTemplate(template, value) {
    var html_template;

    if (!template) {
      return "";
    }
    html_template = Handlebars.compile(template);
    return html_template({value: value});
  }

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
          gadget.property_dict.filter_panel = $(gadget.property_dict.element.querySelector(".listbox-filter-panel"));
        });
    })
    .ready(function (gadget) {
      gadget.property_dict.filter_panel.panel({
        "position-fixed": true,
        "display": "overlay",
        "position": "right",
        "theme": "b"
      });
    })
    .ready(function (gadget) {
      return gadget.property_dict.filter_panel.trigger("create");
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
        filter_part_list = [],
        j,
        k,
        k_len,
        search_list = [],
        translated_column_list = [],
        all_docs_result_list = [];

      // store initial configuration
      gadget.property_dict.option_dict = option_dict;

      // filter query
      if (option_dict.filter_column === undefined) {
        option_dict.filter_column = {select: "status"};
      }
      if (option_dict.filter && option_dict.filter !== '') {
        for (j = 0; j < option_dict.filter.split('+').length; j += 1) {
          filter_part_list.push(
            '('+ option_dict.filter_column.select +':"' +
            option_dict.filter.split('+')[j].toUpperCase() + '")'
          );
        }
        if (option_dict.query.query) {
          option_dict.query.query += ' AND (' + filter_part_list.join(' OR ') + ')';
        } else {
          option_dict.query.query = '(' + filter_part_list.join(' OR ') + ')';
        }
      }
      // Create the search query
      if (option_dict.search) {
        for (k = 0, k_len = option_dict.column_list.length; k < k_len; k += 1) {
          search_list.push(option_dict.column_list[k].select + ':"%' + option_dict.search + '%"');
        }
        if (option_dict.query.query) {
          option_dict.query.query = '(' + search_list.join(' OR ') + ') AND ' + option_dict.query.query;
        } else {
          option_dict.query.query = '(' + search_list.join(' OR ') + ')';
        }
      }
      if (option_dict.view === '' || option_dict.view === undefined) {
        option_dict.view = 'view';
      }
      return gadget.jio_allDocs(option_dict.query)
        .push(function (all_docs_result_list) {
          var row_list = [],
            cell_list,
            current_value,
            i_len,
            i,
            j_len,
            j;

          // build handlebars object
          for (j = 0, j_len = all_docs_result_list.data.total_rows; j < j_len; j += 1) {
            cell_list = [];
            for (i = 0, i_len = option_dict.column_list.length; i < i_len; i += 1) {
              current_value = all_docs_result_list.data.rows[j]
                .value[option_dict.column_list[i].select];
              if (option_dict.column_list[i].convertDate) {
                current_value = formatDate(new Date(current_value));
              }
              cell_list.push({
                "href": (option_dict.disable_href) ? '' : "#page=" +
                  option_dict.view + "&key=" +
                  all_docs_result_list.data.rows[j].id,
                "value": current_value,
                "html_value": renderFomTemplate(
                  option_dict.column_list[i].template || '',
                  current_value
                ),
                "class": option_dict.column_list[i].css_class || ''
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
          var enable_search = true;
          if (option_dict.enable_search !== undefined) {
            enable_search = option_dict.enable_search;
          }
          if (!enable_search) {
            $(gadget.property_dict.element.querySelector(".custom-grid"))
              .removeClass('ui-shadow').css('padding', '0');
          }
          content += listbox_widget_table({
            widget_theme : option_dict.widget_theme,
            search: option_dict.search,
            enable_search: enable_search,
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
          var form = gadget.property_dict.element.querySelector('form.search'),
            refresh = gadget.property_dict.element.querySelector('.listbox-refresh'),
            filter = gadget.property_dict.element.querySelector('.listbox-filter'),
            form_filter = gadget.property_dict.element.querySelector('form.filter'),
            promise_list = [];

          if (form !== undefined && form !== null && form !== '') {
            promise_list.push(loopEventListener(
              form,
              'submit',
              false,
              function (evt) {
                return gadget.redirect({
                  jio_key: gadget.property_dict.option_dict.jio_key || '',
                  page: gadget.property_dict.option_dict.search_page || '',
                  filter: gadget.property_dict.option_dict.filter || '',
                  search: evt.target[0].value
                });
              }
            ));
          }
          if (refresh !== undefined && refresh !== null && refresh !== '') {
            promise_list.push(loopEventListener(
              refresh,
              'click',
              false,
              function (evt) {
                return gadget.redirect({
                  page: gadget.property_dict.option_dict.search_page || '',
                  sort_on: gadget.property_dict.option_dict.sort_on || '',
                  search: gadget.property_dict.option_dict.search || '',
                  filter: gadget.property_dict.option_dict.filter || '',
                  t: Date.now() / 1000 | 0
                });
              })
            );
          }
          if (filter !== undefined && filter !== null && filter !== '') {
            promise_list.push(loopEventListener(
              filter,
              'click',
              false,
              function (evt) {
                gadget.property_dict.filter_panel.panel("toggle");
              })
            );
          }
          if (form_filter !== undefined && form_filter !== null && form_filter !== '') {
            promise_list.push(loopEventListener(
              form_filter,
              'submit',
              false,
              function (evt) {
                var filter_status = [],
                  element = gadget.property_dict.element;
                if (element.querySelector('#monitor-promise-error').checked) {
                  filter_status.push('error');
                }
                if (element.querySelector('#monitor-promise-success').checked) {
                  filter_status.push('ok');
                }
                if (element.querySelector('#monitor-promise-warning').checked) {
                  filter_status.push('warning');
                }
                return gadget.redirect({
                  page: gadget.property_dict.option_dict.search_page || '',
                  sort_on: gadget.property_dict.option_dict.sort_on || '',
                  search: gadget.property_dict.option_dict.search || '',
                  filter: filter_status.join('+')
                });
              })
            );
          }
          return RSVP.all(promise_list);
        });
    });

}(window, rJS, RSVP, Handlebars, loopEventListener));
