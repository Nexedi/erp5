/*global window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query,
         console */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, continue:true */
(function (window, rJS, domsugar, SimpleQuery, ComplexQuery, Query) {
  "use strict";
  // XXX history_previous: prevent getting to erp5 ui by checking the
  // historing or forcing the page value
  // XXX create topic by followup (allDocs group by follow up)

  var DISPLAY_READER = 'display_reader',
    DISPLAY_THREAD = 'display_thread',
    // DISPLAY_POST = 'display_post',
    MAIN_SCOPE = 'child_scope',
    DISPLAYED_POST_COUNT = 15,
    THREAD_READER_FIELD_KEY = 'field_listbox';

  function loadChildGadget(gadget, gadget_url, must_declare, callback) {
    var queue,
      child_gadget;
    if (must_declare) {
      queue = gadget.declareGadget(gadget_url, {scope: MAIN_SCOPE});
    } else {
      queue = gadget.getDeclaredGadget(MAIN_SCOPE);
    }
    return queue
      .push(function (result) {
        child_gadget = result;
        if (callback) {
          return callback(result);
        }
      })
      .push(function (result) {
        if (must_declare) {
          domsugar(gadget.element, [child_gadget.element]);
        }
        return result;
      });
  }

  function renderDiscussionThreadList(gadget, must_declare) {
    return loadChildGadget(gadget, "gadget_erp5_pt_form_view.html",
                           must_declare,
                           function (form_gadget) {

        var group_list = [],
          field_dict = {},
          column_list = [
            ['title', 'Title'],
            ['DiscussionThread_getDiscussionPostCount', 'Responses'],
            ['modification_date', 'Date']
          ];

        field_dict.listbox = {
          "column_list": column_list,
          "show_anchor": 0,
          "default_params": {},
          "editable": 1,
          "editable_column_list": [],
          "key": "field_listbox",
          "lines": 15,
          "list_method": "portal_catalog",
          "query": "urn:jio:allDocs?query=" + Query.objectToSearchText(
            new ComplexQuery({
              operator: "AND",
              query_list: [
                new SimpleQuery({
                  key: "portal_type",
                  operator: "=",
                  type: "simple",
                  value: "Discussion Thread"
                }),
                new SimpleQuery({
                  key: "validation_state",
                  operator: "=",
                  type: "simple",
                  // XXX Check usual states
                  value: "shared"
                })
              ],
              type: "complex"
            })
          ),
          "portal_type": ["Discussion Thread"],
          "search_column_list": [],
          "sort_column_list": [],
          "sort": [['modification_date', 'DESC']],
          "title": "Discussion Threads",
          "type": "ListBox"
        };
        group_list.push([
          "bottom",
          [["listbox"]]
        ], [
          "hidden", ["listbox_modification_date"]
        ]);

        return form_gadget.render({
          erp5_document: {
            "_embedded": {
              "_view": field_dict
            },
            "_links": {
              "type": {
                // form_list display portal_type in header
                name: ""
              }
            }
          },
          form_definition: {
            group_list: group_list
          }
        });
      })
      .push(function () {
        return gadget.updateHeader({
          page_title: 'Forum',
          page_icon: 'comment'
        });
      });

  }

  function renderDiscussionThread(gadget, must_declare, jio_key) {
    return loadChildGadget(gadget, "gadget_erp5_pt_form_view_editable.html",
                           must_declare, function (form_gadget) {

        var thread_info_dict;
        return gadget.jio_allDocs({
          select_list: ['uid', 'title'],
          query: Query.objectToSearchText(
            new SimpleQuery({
              key: "relative_url",
              operator: "=",
              type: "simple",
              value: jio_key
            })
          ),
          limit: [0, 1]
        })
          .push(function (result_list) {
            // XXX implement pseudo getResultValue
            thread_info_dict = result_list.data.rows[0].value;
            var group_list = [],
              field_dict = {};

            field_dict.nutnut = {
              "editable": 1,
              "key": THREAD_READER_FIELD_KEY,
              "title": "Discussion Posts",
              "type": "GadgetField",
              "url": "gadget_thread_reader.html",
              "sandbox": "",
              "renderjs_extra": JSON.stringify({
                query_dict: {
                  portal_type: 'Discussion Post',
                  parent_uid: thread_info_dict.uid
                },
                sort: [['modification_date', 'ASC'], ['uid', 'ASC']],
                lines: DISPLAYED_POST_COUNT
              }),
              "hidden": 0
            };
            group_list.push([
              "bottom",
              [["nutnut"]]
            ]);

            return form_gadget.render({
              erp5_document: {
                "_embedded": {
                  "_view": field_dict
                },
                "_links": {
                  "type": {
                    // form_list display portal_type in header
                    name: ""
                  }
                }
              },
              form_definition: {
                group_list: group_list
              }
            });
          })
          .push(function () {
            return gadget.getUrlFor({command: 'history_previous'});
          })
          .push(function (url) {
            return gadget.updateHeader({
              page_title: 'Thread: ' + thread_info_dict.title,
              page_icon: 'comment',
              front_url: url
            });
          });
      });

  }

/*
  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "=",
        type: "simple",
        value: value_list[i]
      }));
    }
    return new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
  }
*/

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")

    .declareMethod('triggerSubmit', function () {
      return;
    })

    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .allowPublicAcquisition("jio_allDocs", function (param_list, scope) {
      // XXX Convert iso date to a DateTime field
      // XXX Paginate message to last message on modification date column
      if (this.state.display_step !== DISPLAY_READER) {
        throw new rJS.AcquisitionError();
      }

      var gadget = this,
        options = param_list[0];
      console.log(scope, param_list);
      return gadget.jio_allDocs(options)
        .push(function (result) {
          var i, date,
            len = result.data.total_rows,
            key,
            url_value,
            last_url_value,
            count;
          for (i = 0; i < len; i += 1) {
            url_value = {
              command: 'index',
              options: {
                jio_key: result.data.rows[i].id,
                page: gadget.state.page
              }
            };
            last_url_value = {
              command: 'index',
              options: {
                jio_key: result.data.rows[i].id,
                page: gadget.state.page
              }
            };
            count = result.data.rows[i].value
                          .DiscussionThread_getDiscussionPostCount;
            last_url_value.options[THREAD_READER_FIELD_KEY + '_begin_from'] =
              count - (count % DISPLAYED_POST_COUNT);

            for (key in result.data.rows[i].value) {
              if (result.data.rows[i].value.hasOwnProperty(key)) {
                result.data.rows[i].value[key] = {
                  url_value: url_value,
                  default: result.data.rows[i].value[key]
                };
              }
            }

            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(
                result.data.rows[i].value.modification_date.default
              );
              result.data.rows[i].value.modification_date.url_value =
                last_url_value;
              result.data.rows[i].value.modification_date
                    .field_gadget_param = {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: false,
                  description: "The Date",
                  editable: 1,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": date.toUTCString(),
                  key: "modification_date",
                  required: 0,
                  timezone_style: 0,
                  title: "Modification Date",
                  type: "DateTimeField"
                };
            }

            if (result.data.rows[i].value.hasOwnProperty(
                "DiscussionThread_getDiscussionPostCount"
              )) {
              result.data.rows[i].value
                    .DiscussionThread_getDiscussionPostCount
                    .field_gadget_param = {
                  description: "Count",
                  editable: 0,
                  hidden: 0,
                  "default": result.data.rows[i].value
                                   .DiscussionThread_getDiscussionPostCount
                                   .default,
                  key: "count",
                  required: 0,
                  title: "Responses",
                  type: "IntegerField"
                };
            }
            /*
            if (result.data.rows[i].value.hasOwnProperty("asStrippedHTML")) {
              result.data.rows[i].value.asStrippedHTML = {
                url_value: {
                  command: 'index',
                  options: {
                    jio_key: result.data.rows[i].id,
                    page: gadget.state.page
                  }
                },
                field_gadget_param: {
                  description: "Content",
                  editable: 0,
                  hidden: 0,
                  "default": result.data.rows[i].value.asStrippedHTML,
                  key: "asStrippedHTML",
                  required: 0,
                  title: "Content",
                  type: "EditorField"
                }
              };
            }
            */

          }
          return result;
        });
    })

    .declareMethod('render', function (options) {
      console.log(options);

      var display_step,
        jio_key = options.jio_key;
      if (jio_key === undefined) {
        display_step = DISPLAY_READER;
      } else if ((jio_key.match(/\//g) || []).length === 1) {
        // XXX HACK
        display_step = DISPLAY_THREAD;
      }

      return this.changeState({
        // first_render: true,
        page: options.page,
        jio_key: jio_key,
        display_step: display_step,
        options: options,
        // Force display in any case
        render_timestamp: new Date().getTime()
        /*
        display_step: DISPLAY_TREE,
        // Only build the bt5 during the first query
        extract: 1,
        diff_url: options.diff_url,
        get_tree_url: options.get_tree_url,
        remote_comment: options.remote_comment,
        remote_url: options.remote_url,
        key: options.key,
        default_changelog: options.default_changelog,
        default_push: options.default_push,
        value: options.value || JSON.stringify({
          added: [],
          modified: [],
          removed: [],
          changelog: '',
          push: false
        }),
        editable: (options.editable === undefined) ? true : options.editable
        */
      });
    })
    .onStateChange(function (modification_dict) {
      console.log('changestate', modification_dict);
      var gadget = this;

      if (gadget.state.display_step === DISPLAY_READER) {
        return renderDiscussionThreadList(
          gadget,
          modification_dict.hasOwnProperty('display_step')
        );
      }
      if (gadget.state.display_step === DISPLAY_THREAD) {
        return renderDiscussionThread(
          gadget,
          modification_dict.hasOwnProperty('display_step'),
          gadget.state.jio_key
        );
      }
    /*
        return renderDiscussionPost(
          gadget,
          modification_dict.hasOwnProperty('display_step') ||
          modification_dict.first_render,
          gadget.state.jio_key
        );
      }
*/
      throw new Error('Unhandled display step: ' + gadget.state.display_step);
    });

}(window, rJS, domsugar, SimpleQuery, ComplexQuery, Query));