/*global window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query,
         console */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, continue:true */
(function (window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query) {
  "use strict";
  // XXX history_previous: prevent getting to erp5 ui by checking the
  // historing or forcing the page value
  // XXX create topic by followup (allDocs group by follow up)

  var DISPLAY_READER = 'display_reader',
    DISPLAY_THREAD = 'display_thread',
    DISPLAY_POST = 'display_post',
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
              field_dict = {},
              column_list = [
                ['asStrippedHTML', 'Content'],
                ['modification_date', 'Modification Date']
              ];

            field_dict.nutnut = {
              "column_list": column_list,
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": THREAD_READER_FIELD_KEY,
              "lines": DISPLAYED_POST_COUNT,
              "list_method": "portal_catalog",
              "query": "urn:jio:allDocs?query=" + Query.objectToSearchText(
                new ComplexQuery({
                  operator: "AND",
                  query_list: [
                    new SimpleQuery({
                      key: "portal_type",
                      operator: "=",
                      type: "simple",
                      value: "Discussion Post"
                    }),
                    new SimpleQuery({
                      key: "parent_uid",
                      operator: "=",
                      type: "simple",
                      // XXX Check usual states
                      value: thread_info_dict.uid
                    })
                  ],
                  type: "complex"
                })
              ),
              "portal_type": ["Discussion Post"],
              "search_column_list": [],
              "sort_column_list": [],
              "sort": [['modification_date', 'ASC']],
              "title": "Discussion Posts XXXXXXX",
              "type": "GadgetField",
              "url": "gadget_thread_reader.html",
              "sandbox": "",
              "renderjs_extra": JSON.stringify({
                query: "urn:jio:allDocs?query=" + Query.objectToSearchText(
                  new ComplexQuery({
                    operator: "AND",
                    query_list: [
                      new SimpleQuery({
                        key: "portal_type",
                        operator: "=",
                        type: "simple",
                        value: "Discussion Post"
                      }),
                      new SimpleQuery({
                        key: "parent_uid",
                        operator: "=",
                        type: "simple",
                        // XXX Check usual states
                        value: thread_info_dict.uid
                      })
                    ],
                    type: "complex"
                  })
                ),
                sort: [['modification_date', 'ASC'], ['uid', 'ASC']],
                lines: DISPLAYED_POST_COUNT,
              }),
              "hidden": 0
            };
            group_list.push([
              "bottom",
              [["nutnut"]]
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

  function renderDiscussionPost(gadget, must_declare, jio_key) {
    return loadChildGadget(gadget, "gadget_erp5_pt_form_view.html",
                           must_declare,
                           function (form_gadget) {

        var thread_info_dict;
        return gadget.jio_allDocs({
          select_list: ['asStrippedHTML', 'title'],
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

            field_dict.content = {
              "editable": 0,
              "key": "content",
              "default": thread_info_dict.asStrippedHTML,
              "type": "EditorField"
            };
            group_list.push([
              "bottom",
              [["content"]]
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
              page_title: 'Post: ' + thread_info_dict.title,
              page_icon: 'comment',
              front_url: url
            });
          });
      });

  }

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

    .declareMethod('render2', function renderHeader() {
      var gadget = this;
      return gadget.jio_allDocs({
        select_list: ['uid', 'follow_up_title', 'title',
                      'modification_date', 'countFolder'],
        sort_on: [['modification_date', 'DESC']],
        query: Query.objectToSearchText(
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
        limit: 15
      })
        .push(function (result) {
          var uid_list = [];
          if (result.data.total_rows.length === 0) {
            uid_list.push(-1);
          } else {
            uid_list = result.data.rows.map(function (x) {
              return x.value.uid;
            });
          }
          // Search amount of documentation web pages related to those products
          return gadget.jio_allDocs({
            select_list: ['parent_uid', 'count(*)'],
            query: Query.objectToSearchText(
              new ComplexQuery({
                operator: "AND",
                query_list: [
                  new SimpleQuery({
                    key: "portal_type",
                    operator: "=",
                    type: "simple",
                    value: "Discussion Post"
                  }),
                  new ComplexQuery({
                    operator: "OR",
                    type: "complex",
                    query_list: uid_list.map(function (parent_uid) {
                      return new SimpleQuery({
                        key: "parent_uid",
                        operator: "=",
                        type: "simple",
                        value: parent_uid
                      });
                    })
                  })
                ],
                type: "complex"
              })
            ),
            group_by: ['parent_uid'],
            limit: 10000
          })
            .push(function () {
              return result;
            });

        })
        .push(function (result) {
          console.log(result);
          var element_list = [],
            i;
          console.log(result);
          for (i = 0; i < result.data.total_rows; i += 1) {
            element_list.push(
              domsugar('br'),
              domsugar('div', [
                domsugar('p', {text: result.data.rows[i].value.title}),
                domsugar('p', {text: result.data.rows[i].value.modification_date}),
                domsugar('p', {text: result.data.rows[i].value.follow_up_title}),
                domsugar('p', {text: result.data.rows[i].value.countFolder}),
              ])
            );
          }
          // XXX group by discussion post by parent_uid
          console.log(element_list);
          return domsugar(gadget.element, element_list);
        });

      var gadget = this,
        product_uid_dict = {},
        meta_product_uid_list = [],
        product_list = [];
      // First, get the list of products
      return searchAllProject(gadget, product_uid_dict,
                              meta_product_uid_list, product_list)
        .push(function () {
          return RSVP.hash({
            status_dom: buildSoftwareStatusDom(gadget, product_list,
                                               product_uid_dict),
            documentation_dom: buildDocumentationDom(gadget,
                                                     meta_product_uid_list)
          });
        })
        .push(function (result_dict) {

          domsugar(gadget.element, [
            domsugar('img', {src: 'NXD-Official.Logo.svg?format=',
                             alt: 'Nexedi Logo'}),
            domsugar('section', {class: 'ui-content-header-plain'}, [
              domsugar('h3', [
                domsugar('span', {class: 'ui-icon ui-icon-exchange',
                                  text: ' '}),
                'Documentation'
              ])
            ]),
            result_dict.documentation_dom,
            domsugar('section', {class: 'ui-content-header-plain'}, [
              domsugar('h3', [
                domsugar('span', {class: 'ui-icon ui-icon-exchange',
                                  text: ' '}),
                'Software Status'
              ])
            ]),
            result_dict.status_dom
          ]);

          return gadget.updateHeader({
            page_title: 'Nexedi Project Quality',
            page_icon: 'puzzle-piece'
          });
        });
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
            last_url_value;
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
                page: gadget.state.page,
              }
            };
            last_url_value.options[THREAD_READER_FIELD_KEY + '_begin_from'] =
              result.data.rows[i].value.DiscussionThread_getDiscussionPostCount -
              (result.data.rows[i].value.DiscussionThread_getDiscussionPostCount % DISPLAYED_POST_COUNT);

            for (key in result.data.rows[i].value) {
              if (result.data.rows[i].value.hasOwnProperty(key)) {
                result.data.rows[i].value[key] = {
                  url_value: url_value,
                  default: result.data.rows[i].value[key]
                }
              }
            }

            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date.default);
              console.log(last_url_value);
              result.data.rows[i].value.modification_date.url_value = last_url_value;
              result.data.rows[i].value.modification_date.field_gadget_param = {
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

            if (result.data.rows[i].value.hasOwnProperty("DiscussionThread_getDiscussionPostCount")) {
              result.data.rows[i].value.DiscussionThread_getDiscussionPostCount.field_gadget_param = {
                description: "Count",
                editable: 0,
                hidden: 0,
                "default": result.data.rows[i].value.DiscussionThread_getDiscussionPostCount.default,
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
          modification_dict.hasOwnProperty('display_step') || modification_dict.first_render,
          gadget.state.jio_key
        );
      }
*/
      throw new Error('Unhandled display step: ' + gadget.state.display_step);
    });

}(window, rJS, RSVP, domsugar, SimpleQuery, ComplexQuery, Query));