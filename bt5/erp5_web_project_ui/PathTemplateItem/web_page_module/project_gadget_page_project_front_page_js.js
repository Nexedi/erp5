/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL, domsugar */
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL, domsugar) {
  "use strict";

  var STATUS_OK = "green",
    STATUS_NOT_OK = "red",
    NONE_STATUS = "none",
    RADIX = 10,
    STATUS_SPAN = "status",
    TOTAL_SPAN = "total",
    OUTDATED_SPAN = "outdated",
    NUMBER_SPAN = "number",
    NAME_SPAN = "name",
    FORUM_LINK_ID_SUFFIX = "forum",
    FORUM_LINK_TYPE = "link",
    OUTDATED_LABEL = " out of date",
    FAILED_LABEL = " failed",
    TEST_RESULT_PORTAL_TYPE = "Test Result",
    QUERY_LIMIT = 100000,
    SUPERVISOR_FIELD_TITLE = "Supervisor",
    //XXX hardcoded limit dates (3 months for milestones, 3 weeks for documents)
    //define dates in System Preference Project tab?
    //date ISO string format: "yyyy-mm-ddThh:mm:ss.mmmm"
    //JIO query date format:  "yyyy-mm-dd hh:mm:ss"
    MILESTONE_LIMIT_DATE = new Date(new Date().setDate(new Date().getDate() - 90))
      .toISOString().substring(0, new Date().toISOString().length - 5).replace("T", " "),
    DOCUMENT_LIMIT_DATE = new Date(new Date().setDate(new Date().getDate() - 21))
      .toISOString().substring(0, new Date().toISOString().length - 5).replace("T", " "),
    PORTAL_TITLE_DICT = {"Task": "Tasks",
                         "Test Result" : "Test Results",
                         "Bug" : "Bugs",
                         "Project Milestone" : "Milestones",
                         "Task Report": "Task Reports"},
    PORTAL_TYPE_LIST = ["Task", "Bug", "Task Report"],
    VALID_STATE_LIST = ["planned", "auto_planned", "ordered", "confirmed",
                        "ready", "stopped", "started", "submitted", "validated"];

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "",
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

  function getProjectId(id) {
    var segments = id.split("/");
    if (segments.length === 2) {
      return id;
    }
    return segments.slice(0, 2).join("/");
  }

  function getProjectHtlmElementId(project_id, type, suffix, hash_selector) {
    hash_selector = hash_selector ? '#' : '';
    //remove not allowed html id chars (spaces, slashes)
    return hash_selector + [project_id, type, suffix].join("-")
      .replace(/\//g, "-").replace(/\s/g, "-");
  }

  function getComplexQuery(query_dict, operator, extra_query) {
    var key,
      query_list = [];
    for (key in query_dict) {
      if (query_dict.hasOwnProperty(key)) {
        query_list.push(new SimpleQuery({
          key: key,
          operator: "",
          type: "simple",
          value: query_dict[key]
        }));
      }
    }
    if (extra_query) {
      query_list.push(extra_query);
    }
    return new ComplexQuery({
      operator: operator,
      query_list: query_list,
      type: "complex"
    });
  }

  function renderProjectLine(project_id, portal_type, total_count, outdated_count) {
    var total_span = document.querySelector(
      getProjectHtlmElementId(project_id, portal_type, TOTAL_SPAN, true)
    ),
      outdated_span = document.querySelector(
        getProjectHtlmElementId(project_id, portal_type, OUTDATED_SPAN, true)
      ),
      status_span = document.querySelector(
        getProjectHtlmElementId(project_id, portal_type, STATUS_SPAN, true)
      ),
      number_span = document.querySelector(
        getProjectHtlmElementId(project_id, portal_type, NUMBER_SPAN, true)
      );
    if (total_count > 0 && total_span) {
      total_span.textContent = parseInt(total_span.textContent, RADIX) + total_count;
    }
    if (outdated_span) {
      outdated_span.textContent = parseInt(outdated_span.textContent, RADIX) +
        outdated_count;
    }
    if (status_span) {
      if (outdated_count > 0) {
        status_span.classList.remove(STATUS_OK);
        status_span.classList.add(STATUS_NOT_OK);
      } else if (!status_span.classList.value.includes(STATUS_NOT_OK)) {
        status_span.classList.add(STATUS_OK);
      }
    }
    if (number_span) {
      if (outdated_count > 0) {
        number_span.classList.remove("ui-hidden");
        number_span.classList.add("ui-visible");
      }
    }
  }

  function renderProjectDocumentLines(gadget, limit_date) {
    var i,
      query_list = [],
      document_list = [],
      document_query;
    query_list.push(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    query_list.push(createMultipleSimpleOrQuery('portal_type', PORTAL_TYPE_LIST));
    query_list.push(createMultipleSimpleOrQuery('simulation_state', VALID_STATE_LIST));
    if (limit_date) {
      query_list.push(new SimpleQuery({
        key: "modification_date",
        operator: "<",
        type: "simple",
        value: limit_date
      }));
    }
    document_query = new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    });
    return gadget.jio_allDocs({
      query: Query.objectToSearchText(document_query),
      limit: QUERY_LIMIT,
      select_list: ['source_project__relative_url', 'portal_type', 'count(*)'],
      group_by: ['portal_type', 'source_project__relative_url'],
      sort_on: [["modification_date", "descending"]]
    })
      .push(function (result) {
        document_list = result.data.rows;
        for (i = 0; i < document_list.length; i += 1) {
          renderProjectLine(getProjectId(document_list[i].value
                                         .source_project__relative_url),
                            document_list[i].value.portal_type,
                            limit_date ? 0 : document_list[i].value["count(*)"],
                            limit_date ? document_list[i].value["count(*)"] : 0);
        }
      });
  }

  function renderMilestoneLineList(gadget, limit_date) {
    var i,
      query_list = [],
      milestone_list,
      milestone_query = getComplexQuery({"portal_type" : "Project Milestone",
                                          "validation_state" : "validated"},
                                        "AND");
    if (limit_date) {
      query_list.push(milestone_query);
      query_list.push(new SimpleQuery({
        key: "modification_date",
        operator: "<",
        type: "simple",
        value: limit_date
      }));
      milestone_query = new ComplexQuery({
        operator: "AND",
        query_list: query_list,
        type: "complex"
      });
    }
    return gadget.jio_allDocs({
      query: Query.objectToSearchText(milestone_query),
      limit: QUERY_LIMIT,
      select_list: ['title', 'portal_type', 'count(*)'],
      group_by: ['parent_uid'],
      sort_on: [["modification_date", "descending"]]
    })
      .push(function (result) {
        milestone_list = result.data.rows;
        for (i = 0; i < milestone_list.length; i += 1) {
          renderProjectLine(getProjectId(milestone_list[i].id),
                            milestone_list[i].value.portal_type,
                            limit_date ? 0 : milestone_list[i].value["count(*)"],
                            limit_date ? milestone_list[i].value["count(*)"] : 0);
        }
      });
  }

  function getProjectList(gadget) {
    var project_query = Query.objectToSearchText(
      getComplexQuery({"portal_type" : "Project",
                       "validation_state" : "validated"},
                      "AND")
    );
    return gadget.jio_allDocs({
      query: project_query,
      limit: QUERY_LIMIT,
      select_list: ['title', 'source_decision_title', 'source_decision_relative_url'],
      sort_on: [["title", "ascending"]]
    })
      .push(function (result) {
        return result.data.rows;
      });
  }

  function getUrlParameterDict(jio_key, view, sort_list, column_list, extended_search) {
    return {
      command: 'push_history',
      options: {
        'jio_key': jio_key,
        'page': 'form',
        'view': view,
        'field_listbox_sort_list:json': sort_list,
        'field_listbox_column_list:json': column_list,
        'extended_search': extended_search
      }
    };
  }

  function createProjectQuery(project_jio_key, key_value_list) {
    var i, query_list = [], id_query_list = [], id_complex_query;
    if (project_jio_key) {
      //relation to project or child project lines
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key
      }));
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key + "/%%"
      }));
      id_complex_query = new ComplexQuery({
        operator: "OR",
        query_list: id_query_list,
        type: "complex"
      });
      query_list.push(id_complex_query);
    }
    for (i = 0; i < key_value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key_value_list[i][0],
        operator: "",
        type: "simple",
        value: key_value_list[i][1]
      }));
    }
    return Query.objectToSearchText(new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    }));
  }

  function renderProjectList(gadget, project_list) {
    var i,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.querySelector("#js-project-list"),
      spinner = document.querySelector("#js-spinner"),
      url_parameter_list = [],
      milestone_url_list = [],
      task_url_list = [],
      task_report_url_list = [],
      bug_url_list = [],
      test_result_url_list = [],
      supervisor_url_list = [],
      milestone_view,
      project_view;

    function createProjectHtmlElement(project_id, project_title,
                                      project_url, supervisor, supervisor_url) {
      var project_link = domsugar('a', {
          href: project_url
        }, [project_title]),
        title_div = domsugar('div', { class: "project-title" },
                             [project_link]),
        left_info_div = domsugar('div', { class: "project-left" }),
        supervisor_field_label = domsugar('label', {}, [SUPERVISOR_FIELD_TITLE]),
        supervisor_value_link = domsugar('a', {
          href: supervisor_url
        }, [supervisor]),
        supervisor_field_div = domsugar('div', { class: "field project-line" },
                             [supervisor_field_label]),
        supervisor_value_div = domsugar('div', { class: "field project-line value" },
                             [supervisor_value_link]),
        forum_link = domsugar('a', {
          id: getProjectHtlmElementId(project_id, FORUM_LINK_TYPE, FORUM_LINK_ID_SUFFIX),
          class: "ui-hidden"
        }),
        right_line_div = domsugar('div', { class: "project-line" },
                                  [forum_link]),
        right_div = domsugar('div', { class: "project-right" }),
        info_div = domsugar('div', { class: "project-info" },
                            [left_info_div, right_div]),
        box_div = domsugar('div', { class: "project-box" },
                           [title_div, info_div]),
        project_li = domsugar('li', {}, [box_div]);
      if (supervisor) {
        right_div.appendChild(supervisor_field_div);
        right_div.appendChild(supervisor_value_div);
      }
      right_div.appendChild(right_line_div);
      return [project_li, left_info_div];
    }

    function createProjectLineHtmlElement(project_id, portal_type, line_url, title,
                                          total_count, out_count, status_color) {
      var status_span = domsugar('span', {
          id: getProjectHtlmElementId(project_id, portal_type, STATUS_SPAN),
          class: [STATUS_SPAN, status_color, "margined"].join(" ")
        }),
        name_span = domsugar('span', {
          id: getProjectHtlmElementId(project_id, portal_type, NAME_SPAN),
          class: "name margined"
        }, [title]),
        outdated_span = domsugar('span', {
          id: getProjectHtlmElementId(project_id, portal_type, OUTDATED_SPAN)
        }, [String(out_count)]),
        total_span = domsugar('span', {
          id: getProjectHtlmElementId(project_id, portal_type, TOTAL_SPAN),
          class: "margined"
        }, [String(total_count)]),
        open_bracket_span = domsugar('span', {}, ["("]),
        close_bracket_span = domsugar('span', {}, [")"]),
        outdated_label_span = domsugar('span', {}, [
          (portal_type === TEST_RESULT_PORTAL_TYPE) ? FAILED_LABEL : OUTDATED_LABEL
        ]),
        number_span = domsugar('span', {
          id: getProjectHtlmElementId(project_id, portal_type, NUMBER_SPAN),
          class: "ui-hidden"
        }, [open_bracket_span, outdated_span, outdated_label_span, close_bracket_span]),
        line_div = domsugar('div', { class: "project-line" },
                            [status_span, total_span, name_span, number_span]),
        line_link = domsugar('a', {
          href: line_url || ""
        }, [line_div]);
      return line_link;
    }

    return gadget.getSetting("hateoas_url")
      .push(function (hateoas_url) {
        for (i = 0; i < project_list.length; i += 1) {
          milestone_view = hateoas_url +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            project_list[i].id + '&view=Project_viewMilestoneList';
          project_view = hateoas_url +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            project_list[i].id +
            '&view=Project_viewQuickOverview';
          url_parameter_list.push(
            getUrlParameterDict(project_list[i].id,
                                project_view)
          );
          milestone_url_list.push(
            getUrlParameterDict('milestone_module',
                                milestone_view,
                                [["stop_date", "ascending"]],
                                null,
                                createProjectQuery(null,
                                                   [["selection_domain_date_milestone_domain", "future"]]))
          );
          task_url_list.push(
            getUrlParameterDict('task_module',
                                "view",
                                [["delivery.start_date", "descending"]],
                                ["title", "delivery.start_date", "source_title", "translated_simulation_state_title"],
                                createProjectQuery(project_list[i].id,
                                                   [["selection_domain_state_task_domain", "opened"]]))
          );
          task_report_url_list.push(
            getUrlParameterDict('task_report_module',
                                'view',
                                [["delivery.start_date", "descending"]],
                                ["title", "delivery.start_date", "source_title", "translated_simulation_state_title"],
                                createProjectQuery(project_list[i].id,
                                                   [["selection_domain_state_task_report_domain", "confirmed"]]))
          );
          bug_url_list.push(
            getUrlParameterDict('bug_module',
                                "view",
                                [["delivery.start_date", "descending"]],
                                ["title", "description", "source_person_title", "destination_person_title",
                                 "delivery.start_date", "translated_simulation_state_title"],
                                createProjectQuery(project_list[i].id,
                                                   [["selection_domain_state_bug_domain", "open"]]))
          );
          test_result_url_list.push(
            getUrlParameterDict('test_result_module',
                                'view',
                                [["delivery.start_date", "descending"]],
                                null,
                                createProjectQuery(project_list[i].id, []))
          );
          supervisor_url_list.push(
            getUrlParameterDict(project_list[i].value.source_decision_relative_url,
                                'view')
          );
        }
        return RSVP.hash({
          url_parameter_list: gadget.getUrlForList(url_parameter_list),
          milestone_url_list: gadget.getUrlForList(milestone_url_list),
          task_url_list: gadget.getUrlForList(task_url_list),
          task_report_url_list: gadget.getUrlForList(task_report_url_list),
          bug_url_list: gadget.getUrlForList(bug_url_list),
          test_result_url_list: gadget.getUrlForList(test_result_url_list),
          supervisor_url_list: gadget.getUrlForList(supervisor_url_list)
        });
      })
      .push(function (result_dict) {
        var type,
          line_url;
        spinner.classList.add("ui-hidden");
        for (i = 0; i < project_list.length; i += 1) {
          project_html_element_list =
            createProjectHtmlElement(project_list[i].id,
                                     project_list[i].value.title,
                                     result_dict.url_parameter_list[i],
                                     project_list[i].value.source_decision_title,
                                     result_dict.supervisor_url_list[i]);
          project_html = project_html_element_list[0];
          left_div_html = project_html_element_list[1];
          for (type in PORTAL_TITLE_DICT) {
            if (PORTAL_TITLE_DICT.hasOwnProperty(type)) {
              line_url = (function (portal_type) {
                switch (portal_type) {
                case 'Project Milestone':
                  return result_dict.milestone_url_list[i];
                case 'Task':
                  return result_dict.task_url_list[i];
                case 'Task Report':
                  return result_dict.task_report_url_list[i];
                case 'Bug':
                  return result_dict.bug_url_list[i];
                case 'Test Result':
                  return result_dict.test_result_url_list[i];
                }
              })(type);
              left_line_html = createProjectLineHtmlElement(project_list[i].id, type,
                                                            line_url,
                                                            ((PORTAL_TITLE_DICT
                                                              .hasOwnProperty(type)) ?
                                                             PORTAL_TITLE_DICT[type] :
                                                             type),
                                                            0, 0, NONE_STATUS);
              left_div_html.appendChild(left_line_html);
            }
          }
          ul_list.appendChild(project_html);
        }
      });
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('render', function (options) {
      var gadget = this;
      return getProjectList(gadget)
        .push(function (project_list) {
          options.project_list = project_list;
          return gadget.changeState(options);
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: 'Project Management'
      });
    })

    .declareService(function () {
      var gadget = this;
      return renderProjectList(gadget, gadget.state.project_list)
        .push(function () {
          //run the rest of queries and render async
          gadget.detachRenderMilestoneInfo();
          gadget.detachRenderOutdatedMilestoneInfo();
          gadget.detachRenderProjectDocumentInfo();
          gadget.detachRenderOutdatedDocumentInfo();
          gadget.detachRenderTestResultInfo();
          gadget.detachRenderProjectForumLink();
        });
    })

    .declareJob("detachRenderMilestoneInfo", function () {
      return renderMilestoneLineList(this);
    })

    .declareJob("detachRenderOutdatedMilestoneInfo", function () {
      return renderMilestoneLineList(this, MILESTONE_LIMIT_DATE);
    })

    .declareJob("detachRenderProjectDocumentInfo", function () {
      return renderProjectDocumentLines(this);
    })

    .declareJob("detachRenderOutdatedDocumentInfo", function () {
      return renderProjectDocumentLines(this, DOCUMENT_LIMIT_DATE);
    })

    .declareJob("detachRenderTestResultInfo", function () {
      return new RSVP.Queue()
        .push(function () {
          return jIO.util.ajax({
            type: "GET",
            url: new URL('./ERP5Site_getProjectTestStatusData', window.location.href)
          });
        })
        .push(function (result) {
          var project_id,
            project_test_status_dict;
          project_test_status_dict = JSON.parse(result.target.response);
          for (project_id in project_test_status_dict) {
            if (project_test_status_dict.hasOwnProperty(project_id)) {
              renderProjectLine(project_id,
                                TEST_RESULT_PORTAL_TYPE,
                                parseInt(project_test_status_dict[project_id].all_tests, RADIX),
                                parseInt(project_test_status_dict[project_id].failures, RADIX));
            }
          }
        });
    })

    .declareJob("detachRenderProjectForumLink", function () {
      var gadget = this,
        i,
        forum_link_html,
        forum_link_list,
        link_query = getComplexQuery({"portal_type" : "Link",
                                      "validation_state" : "reachable",
                                      "relative_url" : "project_module/%/forum_link"},
                                     "AND");
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            query: Query.objectToSearchText(link_query),
            limit: QUERY_LIMIT,
            select_list: ['url_string'],
            sort_on: [["modification_date", "descending"]]
          });
        })
        .push(function (result) {
          forum_link_list = result.data.rows;
          for (i = 0; i < forum_link_list.length; i += 1) {
            forum_link_html = document.querySelector(
              getProjectHtlmElementId(getProjectId(forum_link_list[i].id),
                                      FORUM_LINK_TYPE,
                                      FORUM_LINK_ID_SUFFIX, true)
            );
            if (forum_link_html) {
              forum_link_html.href = forum_link_list[i].value.url_string;
              forum_link_html.innerHTML = "Project Forum";
              forum_link_html.classList.remove("ui-hidden");
            }
          }
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL, domsugar));