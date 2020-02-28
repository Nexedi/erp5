/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt) {
  "use strict";

  var STATUS_OK = "green",
    STATUS_NOT_OK = "red",
    NONE_STATUS = "none",
    RADIX = 10,
    STATUS_SPAN = "status",
    TOTAL_SPAN = "total",
    OUTDATED_SPAN = "outdated",
    NUMBER_SPAN = "number",
    QUERY_LIMIT = 100000,
    SUPERVISOR_FIELD_TITLE = "Supervisor",
    //XXX hardcoded one year old date to define outdated elements
    // Where to define/get the limit date?
    // by portal_type or the same for all documents?
    LIMIT_DATE = new Date(new Date().setFullYear(new Date().getFullYear() + 1)),
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
    return segments.slice(0, -1).join("/");
  }

  function getProjectSpanId(project_id, portal_type, span_title, hash_selector) {
    hash_selector = hash_selector ? '#' : '';
    //remove not allowed html id chars (spaces, slashes)
    return hash_selector + [project_id, portal_type, span_title].join("-")
      .replace("/", "-").replace(/\s/g, "-");
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

  function getProjectDocumentList(gadget, limit_date) {
    var query_list = [],
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
        return result.data.rows;
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
      select_list: ['title', 'source_decision_title'],
      sort_on: [["modification_date", "ascending"]]
    })
      .push(function (result) {
        return result.data.rows;
      });
  }

  function renderProjectLine(project_id, portal_type, total_count, outdated_count) {
    var total_span = document.querySelector(
      getProjectSpanId(project_id, portal_type, TOTAL_SPAN, true)
    ),
      outdated_span = document.querySelector(
        getProjectSpanId(project_id, portal_type, OUTDATED_SPAN, true)
      ),
      status_span = document.querySelector(
        getProjectSpanId(project_id, portal_type, STATUS_SPAN, true)
      ),
      number_span = document.querySelector(
        getProjectSpanId(project_id, portal_type, NUMBER_SPAN, true)
      );
    total_span.textContent = parseInt(total_span.textContent, RADIX) + total_count;
    outdated_span.textContent = parseInt(outdated_span.textContent, RADIX) +
      outdated_count;
    if (outdated_count > 0) {
      status_span.classList.remove(STATUS_OK);
      status_span.classList.add(STATUS_NOT_OK);
    } else if (!status_span.classList.value.includes(STATUS_NOT_OK)) {
      status_span.classList.add(STATUS_OK);
    }
    number_span.classList.remove("ui-hidden");
  }

  function renderProjectList(gadget, project_list) {
    var i,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.querySelector("#js-project-list"),
      spinner = document.querySelector("#js-spinner"),
      url_parameter_list = [];

    function createProjectHtmlElement(project_id, project_title,
                                      project_url, supervisor) {
      var project_li = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_info_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        supervisor_line_div = document.createElement('div'),
        project_link = document.createElement('a'),
        forum_link = document.createElement('a'),
        supervisor_field_label = document.createElement('label'),
        supervisor_value_span = document.createElement('span');
      if (supervisor) {
        supervisor_line_div.classList.add("field", "project-line");
        supervisor_field_label.innerHTML = SUPERVISOR_FIELD_TITLE;
        supervisor_value_span.innerHTML = supervisor;
        supervisor_line_div.appendChild(supervisor_field_label);
        supervisor_line_div.appendChild(supervisor_value_span);
        right_div.appendChild(supervisor_line_div);
      }
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      project_link.href = project_url;
      project_link.innerHTML = project_title;
      title_div.appendChild(project_link);
      info_div.classList.add("project-info");
      left_info_div.classList.add("left");
      right_line_div.classList.add("project-line");
      //XXX
      forum_link.href = "TODO";
      forum_link.innerHTML = project_id + " forum link";
      right_line_div.appendChild(forum_link);
      right_div.appendChild(right_line_div);
      info_div.appendChild(left_info_div);
      info_div.appendChild(right_div);
      box_div.appendChild(title_div);
      box_div.appendChild(info_div);
      project_li.appendChild(box_div);
      return [project_li, left_info_div];
    }

    function createProjectLineHtmlElement(project_id, portal_type, title, total_count,
                                          out_count, status_color) {
      var line_div = document.createElement('div'),
        status_span = document.createElement('span'),
        name_span = document.createElement('span'),
        number_span = document.createElement('span'),
        outdated_span = document.createElement('span'),
        total_span = document.createElement('span'),
        open_bracket_span = document.createElement('span'),
        close_bracket_span = document.createElement('span');
      line_div.classList.add("project-line");
      status_span.classList.add(STATUS_SPAN);
      status_span.classList.add(status_color);
      status_span.classList.add("margined");
      status_span.setAttribute("id", getProjectSpanId(project_id,
                                                      portal_type, STATUS_SPAN));
      name_span.classList.add("name");
      name_span.classList.add("margined");
      name_span.innerHTML = title;
      total_span.classList.add("margined");
      total_span.innerHTML = total_count;
      total_span.setAttribute("id", getProjectSpanId(project_id,
                                                     portal_type, TOTAL_SPAN));
      outdated_span.innerHTML = out_count;
      outdated_span.setAttribute("id", getProjectSpanId(project_id,
                                                        portal_type, OUTDATED_SPAN));
      open_bracket_span.innerHTML = "(";
      close_bracket_span.innerHTML = ")";
      number_span.appendChild(total_span);
      number_span.appendChild(open_bracket_span);
      number_span.appendChild(outdated_span);
      number_span.appendChild(close_bracket_span);
      number_span.setAttribute("id", getProjectSpanId(project_id,
                                                      portal_type, NUMBER_SPAN));
      number_span.classList.add("ui-hidden");
      line_div.appendChild(status_span);
      line_div.appendChild(name_span);
      line_div.appendChild(number_span);
      return line_div;
    }

    return gadget.getSetting("hateoas_url")
      .push(function (hateoas_url) {
        for (i = 0; i < project_list.length; i += 1) {
          url_parameter_list.push({
            command: 'push_history',
            options: {
              'jio_key': project_list[i].id,
              'page': 'form',
              'view': hateoas_url +
                '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
                project_list[i].id +
                '&view=Project_viewQuickOverview'
            }
          });
        }
        return gadget.getUrlForList(url_parameter_list);
      })
      .push(function (url_list) {
        var type;
        spinner.classList.add("ui-hidden");
        for (i = 0; i < project_list.length; i += 1) {
          project_html_element_list =
            createProjectHtmlElement(project_list[i].id,
                                     project_list[i].value.title,
                                     url_list[i],
                                     project_list[i].value.source_decision_title);
          project_html = project_html_element_list[0];
          left_div_html = project_html_element_list[1];
          for (type in PORTAL_TITLE_DICT) {
            if (PORTAL_TITLE_DICT.hasOwnProperty(type)) {
              left_line_html = createProjectLineHtmlElement(project_list[i].id, type,
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
          gadget.renderProjectDocumentInfo();
          gadget.renderOutdatedDocumentInfo();
          gadget.renderTestResultInfo();
        });
    })

    .declareJob("renderMilestoneInfo", function () {
      var gadget = this,
        i,
        outdated,
        milestone_list,
        milestone_query = Query.objectToSearchText(
          getComplexQuery({"portal_type" : "Project Milestone",
                            "validation_state" : "validated",
                            "parent__portal_type" : "Project"},
                          "AND")
        );
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            query: milestone_query,
            limit: QUERY_LIMIT,
            select_list: ["title", 'portal_type', "parent__title",
                          "parent__relative_url"],
            sort_on: [["modification_date", "descending"]]
          });
        })
        .push(function (result) {
          milestone_list = result.data.rows;
          for (i = 0; i < milestone_list.length; i += 1) {
            outdated = (new Date(milestone_list[i].value.modification_date) <
                        LIMIT_DATE) ? 1 : 0;
            renderProjectLine(getProjectId(milestone_list[i].id),
                              milestone_list[i].value.portal_type,
                              1, outdated);
          }
        });
    })

    .declareJob("renderProjectDocumentInfo", function () {
      var gadget = this,
        i;
      return getProjectDocumentList(gadget)
        .push(function (document_list) {
          for (i = 0; i < document_list.length; i += 1) {
            renderProjectLine(getProjectId(document_list[i].value
                                           .source_project__relative_url),
                              document_list[i].value.portal_type,
                              1, 0);
          }
        });
    })

    .declareJob("renderOutdatedDocumentInfo", function () {
      var gadget = this,
        i,
        //date ISO string format: "yyyy-mm-ddThh:mm:ss.mmmm"
        //JIO query date format:  "yyyy-mm-dd hh:mm:ss"
        limit_date = LIMIT_DATE.toISOString()
          .substring(0, LIMIT_DATE.toISOString().length - 5)
          .replace("T", " ");
      //XXX For testing
      limit_date = new Date().toISOString()
        .substring(0, LIMIT_DATE.toISOString().length - 5).replace("T", " ");
      return getProjectDocumentList(gadget, limit_date)
        .push(function (document_list) {
          for (i = 0; i < document_list.length; i += 1) {
            renderProjectLine(getProjectId(document_list[i]
                                           .value.source_project__relative_url),
                              document_list[i].value.portal_type,
                              0, 1);
          }
        });
    })

    .declareJob("renderTestResultInfo", function () {
      var gadget = this,
        i,
        test_list,
        query_list = [],
        test_result_query,
        test_state_list = ["failed", "stopped", "public_stopped"];
      query_list.push(getComplexQuery({"portal_type" : "Test Result",
                                       "source_project__validation_state" : "validated"},
                                      "AND"));
      query_list.push(createMultipleSimpleOrQuery('simulation_state', test_state_list));
      test_result_query = new ComplexQuery({
        operator: "AND",
        query_list: query_list,
        type: "complex"
      });
      return gadget.jio_allDocs({
        query: Query.objectToSearchText(test_result_query),
        limit: QUERY_LIMIT,
        select_list: ['source_project__relative_url', 'portal_type', 'modification_date'],
        group_by: ['source_project__relative_url'],
        sort_on: [["modification_date", "descending"]]
      })
        .push(function (result) {
          test_list = result.data.rows;
          for (i = 0; i < test_list.length; i += 1) {
            //XXX total and outdated values should come with the test-result-row
            //(all_tests and failed) but those are _local_properties
            renderProjectLine(test_list[i].value.source_project__relative_url,
                              test_list[i].value.portal_type,
                              1, //parseInt(test_list[i].value.all_test, RADIX)
                              0); //parseInt(test_list[i].value.failures, RADIX)
          }
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt));