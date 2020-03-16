/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL */
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL) {
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
    //XXX hardcoded one year old date to define outdated elements
    // Where to define/get the limit date? by portal_type or the same for all documents?
    //date ISO string format: "yyyy-mm-ddThh:mm:ss.mmmm"
    //JIO query date format:  "yyyy-mm-dd hh:mm:ss"
    //FOR DEMO
    /*LIMIT_DATE = new Date(new Date().setFullYear(new Date().getFullYear() - 1))
      .toISOString().substring(0, new Date().toISOString().length - 5).replace("T", " "),*/
    LIMIT_DATE = new Date(2019, 11, 19, 10, 33, 30, 0)
      .toISOString().substring(0, new Date().toISOString().length - 5).replace("T", " "),
    NOW_DATE = new Date().toISOString().substring(0, new Date().toISOString().length - 5).replace("T", " "),
    //XXX hardcoded portal_types, states and titles dict
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
          operator: "=",
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

  function renderMilestoneLines(gadget, limit_date) {
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
    return new RSVP.Queue()
      .push(function () {
        return gadget.jio_allDocs({
          query: Query.objectToSearchText(milestone_query),
          limit: QUERY_LIMIT,
          select_list: ['title', 'portal_type', 'count(*)'],
          group_by: ['parent_uid'],
          sort_on: [["modification_date", "descending"]]
        });
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
      select_list: ['title', 'source_decision_title',
                    'source_decision_relative_url', 'forum_link'],
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
      var project_li = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_info_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        supervisor_field_div = document.createElement('div'),
        supervisor_value_div = document.createElement('div'),
        project_link = document.createElement('a'),
        forum_link = document.createElement('a'),
        supervisor_field_label = document.createElement('label'),
        supervisor_value_link = document.createElement('a');
      if (supervisor) {
        supervisor_field_div.classList.add("field", "project-line");
        supervisor_value_div.classList.add("field", "project-line", "value");
        supervisor_field_label.innerHTML = SUPERVISOR_FIELD_TITLE;
        supervisor_value_link.innerHTML = supervisor;
        supervisor_value_link.href = supervisor_url;
        supervisor_field_div.appendChild(supervisor_field_label);
        supervisor_value_div.appendChild(supervisor_value_link);
        right_div.appendChild(supervisor_field_div);
        right_div.appendChild(supervisor_value_div);
      }
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      project_link.href = project_url;
      project_link.innerHTML = project_title;
      title_div.appendChild(project_link);
      info_div.classList.add("project-info");
      left_info_div.classList.add("project-left");
      right_div.classList.add("project-right");
      right_line_div.classList.add("project-line");
      forum_link.setAttribute("id", getProjectHtlmElementId(project_id, FORUM_LINK_TYPE,
                                                            FORUM_LINK_ID_SUFFIX));
      forum_link.classList.add("ui-hidden");
      right_line_div.appendChild(forum_link);
      right_div.appendChild(right_line_div);
      info_div.appendChild(left_info_div);
      info_div.appendChild(right_div);
      box_div.appendChild(title_div);
      box_div.appendChild(info_div);
      project_li.appendChild(box_div);
      return [project_li, left_info_div];
    }

    function createProjectLineHtmlElement(project_id, portal_type, line_url, title,
                                          total_count, out_count, status_color) {
      var line_div = document.createElement('div'),
        status_span = document.createElement('span'),
        name_span = document.createElement('span'),
        number_span = document.createElement('span'),
        outdated_span = document.createElement('span'),
        total_span = document.createElement('span'),
        open_bracket_span = document.createElement('span'),
        close_bracket_span = document.createElement('span'),
        outdated_label_span = document.createElement('span'),
        line_link = document.createElement('a');
      line_div.classList.add("project-line");
      status_span.classList.add(STATUS_SPAN);
      status_span.classList.add(status_color);
      status_span.classList.add("margined");
      status_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                             portal_type, STATUS_SPAN));
      total_span.classList.add("margined");
      total_span.innerHTML = total_count;
      total_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                            portal_type, TOTAL_SPAN));
      name_span.classList.add("name");
      name_span.classList.add("margined");
      name_span.innerHTML = title;
      name_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                           portal_type, NAME_SPAN));
      outdated_span.innerHTML = out_count;
      outdated_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                               portal_type, OUTDATED_SPAN));
      open_bracket_span.innerHTML = "(";
      outdated_label_span.innerHTML = (portal_type === TEST_RESULT_PORTAL_TYPE) ? FAILED_LABEL : OUTDATED_LABEL;
      close_bracket_span.innerHTML = ")";
      number_span.appendChild(open_bracket_span);
      number_span.appendChild(outdated_span);
      number_span.appendChild(outdated_label_span);
      number_span.appendChild(close_bracket_span);
      number_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                             portal_type, NUMBER_SPAN));
      number_span.classList.add("ui-hidden");
      line_div.appendChild(status_span);
      line_div.appendChild(total_span);
      line_div.appendChild(name_span);
      line_div.appendChild(number_span);
      line_link.appendChild(line_div);
      if (line_url) {
        line_link.href = line_url;
      }
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
        return RSVP.all([gadget.getUrlForList(url_parameter_list),
                         gadget.getUrlForList(milestone_url_list),
                         gadget.getUrlForList(task_url_list),
                         gadget.getUrlForList(task_report_url_list),
                         gadget.getUrlForList(bug_url_list),
                         gadget.getUrlForList(test_result_url_list),
                         gadget.getUrlForList(supervisor_url_list)]);
      })
      .push(function (result_list) {
        var type,
          line_url;
        spinner.classList.add("ui-hidden");
        for (i = 0; i < project_list.length; i += 1) {
          project_html_element_list =
            createProjectHtmlElement(project_list[i].id,
                                     project_list[i].value.title,
                                     result_list[0][i],
                                     project_list[i].value.source_decision_title,
                                     result_list[6][i]);
          project_html = project_html_element_list[0];
          left_div_html = project_html_element_list[1];
          for (type in PORTAL_TITLE_DICT) {
            if (PORTAL_TITLE_DICT.hasOwnProperty(type)) {
              line_url = (function (portal_type) {
                switch (portal_type) {
                case 'Project Milestone':
                  return result_list[1][i];
                case 'Task':
                  return result_list[2][i];
                case 'Task Report':
                  return result_list[3][i];
                case 'Bug':
                  return result_list[4][i];
                case 'Test Result':
                  return result_list[5][i];
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
          gadget.renderMilestoneInfo();
          gadget.renderOtdatedMilestoneInfo();
          gadget.renderProjectDocumentInfo();
          gadget.renderOutdatedDocumentInfo();
          gadget.renderTestResultInfo();
          gadget.renderProjectForumLink();
        });
    })

    .declareJob("renderMilestoneInfo", function () {
      return renderMilestoneLines(this);
    })

    .declareJob("renderOtdatedMilestoneInfo", function () {
      return renderMilestoneLines(this, LIMIT_DATE);
    })

    .declareJob("renderProjectDocumentInfo", function () {
      return renderProjectDocumentLines(this);
    })

    .declareJob("renderOutdatedDocumentInfo", function () {
      return renderProjectDocumentLines(this, LIMIT_DATE);
    })

    .declareJob("renderTestResultInfo", function () {
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

    .declareJob("renderProjectForumLink", function () {
      var gadget = this,
        i,
        forum_link_html,
        forum_link_list,
        link_query = getComplexQuery({"portal_type" : "Link",
                                      "validation_state" : "reachable",
                                      "parent__validation_state" : "validated"},
                                     "AND");
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            query: Query.objectToSearchText(link_query),
            limit: QUERY_LIMIT,
            // TODO FIX not found column url_string when group by parent
            select_list: ['title', 'portal_type'],//, 'url_string'],
            group_by: ['parent_uid'],
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
              //forum_link_html.href = forum_link_list[i].value.url_string;
              //forum_link_html.innerHTML = forum_link_list[i].value.title;
              //HARDCODED FOR DEMO
              forum_link_html.href = "https://www.erp5.com/group_section/forum";
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

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt, jIO, URL));