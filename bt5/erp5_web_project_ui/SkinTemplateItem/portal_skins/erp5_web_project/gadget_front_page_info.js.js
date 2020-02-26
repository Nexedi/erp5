/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt) {
  "use strict";

  /*jshint esnext: true */
  const STATUS_OK = "green";
  const STATUS_NOT_OK = "red";
  const NONE_STATUS = "none";
  const RADIX = 10;
  const STATUS_SPAN = "status";
  const TOTAL_SPAN = "total";
  const OUTDATED_SPAN = "outdated";
  const QUERY_LIMIT = 100000;
  //XXX hardcoded portal_types, states and titles dict (build a template?)
  const PORTAL_TITLE_DICT = {"Task": "Tasks",
                             "Test Result" : "Test Results",
                             "Bug" : "Bugs",
                             "Project Milestone" : "Milestones",
                             "Task Report": "Task Reports",
                             "Support Request" : "Support Requests"};
  const PORTAL_TYPE_LIST = ["Task", "Bug", "Task Report", "Support Request"];
  const VALID_STATE_LIST = ["planned", "auto_planned", "ordered", "confirmed", "ready", "stopped", "started", "submitted", "validated"];

  function getProjectId(id) {
    var segments = id.split("/");
    if (segments.length === 2) {
      return id;
    }
    return segments.slice(0, -1).join("/");
  }

  function getProjectSpanId(project_id, portal_type, span_title) {
    return [project_id, portal_type, span_title].join("-").replace("/", "-").replace(" ", "-");
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
    var document_query;
    document_query = Query.objectToSearchText(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    document_query += ' AND simulation_state: ("' + VALID_STATE_LIST.join('", "') + '")';
    document_query += ' AND portal_type: ("' + PORTAL_TYPE_LIST.join('", "') + '")';
    if (limit_date) {
      document_query += ' AND modification_date: < "' + limit_date + '"';
    }
    return gadget.jio_allDocs({
      query: document_query,
      limit: QUERY_LIMIT,
      select_list: ['source_project__relative_url', 'portal_type', 'count(*)'],
      group_by: ['portal_type', 'source_project__relative_url'],
      sort_on: [["modification_date", "descending"]]
    })
    .push(function (result) {
      return result.data.rows;
    });
  }

  function getProjectElementList(gadget) {
    var project_query = Query.objectToSearchText(
      getComplexQuery({"portal_type" : "Project",
                       "validation_state" : "validated"},
                      "AND"));
    return gadget.jio_allDocs({
      query: project_query,
      limit: QUERY_LIMIT,
      select_list: ['title'],
      sort_on: [["modification_date", "ascending"]]
    })
    .push(function (result) {
      return result.data.rows;
    });
  }

  function renderProjectLine(project_id, portal_type, total_count, outdated_count) {
    var total_span = document.getElementById(getProjectSpanId(project_id, portal_type, TOTAL_SPAN)),
      outdated_span = document.getElementById(getProjectSpanId(project_id, portal_type, OUTDATED_SPAN)),
      status_span = document.getElementById(getProjectSpanId(project_id, portal_type, STATUS_SPAN));
    total_span.textContent = parseInt(total_span.textContent, RADIX) + total_count;
    outdated_span.textContent = parseInt(outdated_span.textContent, RADIX) + outdated_count;
    if (outdated_count > 0) {
      status_span.classList.remove(STATUS_OK);
      status_span.classList.add(STATUS_NOT_OK);
    } else if (!status_span.classList.value.includes(STATUS_NOT_OK)) {
      status_span.classList.add(STATUS_OK);
    }
  }

  function renderProjectList(gadget, project_list) {
    var i,
      item,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.getElementById("js-project-list"),
      spinner = document.getElementById("js-spinner"),
      url_parameter_list = [],
      project_id,
      project_dict,
      outdated;

    function createProjectHtmlElement(project_id, project_title, project_url) {
      var project_element = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_info_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        project_link = document.createElement('a'),
        forum_link = document.createElement('a');
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      project_link.href = project_url;
      project_link.innerHTML = project_title;
      title_div.appendChild(project_link);
      info_div.classList.add("project-info");
      left_info_div.classList.add("left");
      right_line_div.classList.add("project-line");
      //TODO
      forum_link.href = "TODO";
      forum_link.innerHTML = project_id + " forum link";
      right_line_div.appendChild(forum_link);
      right_div.appendChild(right_line_div);
      info_div.appendChild(left_info_div);
      info_div.appendChild(right_div);
      box_div.appendChild(title_div);
      box_div.appendChild(info_div);
      project_element.appendChild(box_div);
      return [project_element, left_info_div];
    }

    function createProjectLineHtmlElement(project_id, portal_type, title, total_count, out_count, status_color) {
      var line_div = document.createElement('div'),
        status = document.createElement('span'),
        name = document.createElement('span'),
        outdated = document.createElement('span'),
        total = document.createElement('span'),
        open_bracket = document.createElement('span'),
        close_bracket = document.createElement('span');
      line_div.classList.add("project-line");
      status.classList.add(STATUS_SPAN);
      status.classList.add(status_color);
      status.classList.add("margined");
      status.setAttribute("id", getProjectSpanId(project_id, portal_type, STATUS_SPAN));
      name.classList.add("name");
      name.classList.add("margined");
      name.innerHTML = title;
      total.classList.add("margined");
      total.innerHTML = total_count;
      total.setAttribute("id", getProjectSpanId(project_id, portal_type, TOTAL_SPAN));
      outdated.innerHTML = out_count;
      outdated.setAttribute("id", getProjectSpanId(project_id, portal_type, OUTDATED_SPAN));
      line_div.appendChild(status);
      line_div.appendChild(name);
      line_div.appendChild(total);
      open_bracket.innerHTML = "(";
      close_bracket.innerHTML = ")";
      line_div.appendChild(open_bracket);
      line_div.appendChild(outdated);
      line_div.appendChild(close_bracket);
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
        spinner.classList.add("ui-hidden");
        for (i = 0; i < project_list.length; i += 1) {
          project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title, url_list[i]);
          project_html = project_html_element_list[0];
          left_div_html = project_html_element_list[1];

          for (var type in PORTAL_TITLE_DICT) {
            if (PORTAL_TITLE_DICT.hasOwnProperty(type)) {
              left_line_html = createProjectLineHtmlElement(project_list[i].id, type,
                                                            ((PORTAL_TITLE_DICT.hasOwnProperty(type)) ? PORTAL_TITLE_DICT[type] : type),
                                                            0, 0, NONE_STATUS);
              left_div_html.appendChild(left_line_html);
            }
          }
          ul_list.appendChild(project_html);
        }
      });
  }

  rJS(window)

    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('render', function (options) {
      return this.changeState(options);
    })

    .onStateChange(function () {
      var gadget = this;
      return getProjectElementList(gadget)
        .push(function (project_list) {
          return renderProjectList(gadget, project_list);
        })
        .push(function (project_list) {
          //run the rest of queries and render async
          gadget.renderMilestoneInfo();
          gadget.renderProjectDocumentInfo();
          gadget.renderOutdatedDocumentInfo();
          gadget.renderTestResultInfo();
        });
    })

    .declareJob("renderMilestoneInfo", function () {
      var gadget = this,
        i, outdated,
        milestone_list,
        milestone_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Project Milestone",
                          "validation_state" : "validated",
                          "parent__portal_type" : "Project"},
                        "AND")),
        milestone_limit_date = new Date();
      //TODO Where to define/get the limit date? byt portal_type or the same for all documents?
      milestone_limit_date.setFullYear(milestone_limit_date.getFullYear() - 1);
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            query: milestone_query,
            limit: QUERY_LIMIT,
            select_list: ["title", 'portal_type', "parent__title", "parent__relative_url"],
            sort_on: [["modification_date", "descending"]]
          })
          .push(function (result) {
            milestone_list = result.data.rows;
            for (i = 0; i < milestone_list.length; i += 1) {
              outdated = (new Date(milestone_list[i].value.modification_date) < milestone_limit_date) ? 1 : 0;
              renderProjectLine(getProjectId(milestone_list[i].id),
                                milestone_list[i].value.portal_type,
                                1, outdated);
            }
          });
        });
    })

    .declareJob("renderProjectDocumentInfo", function () {
      var gadget = this,
        i,
        document_list;
      return getProjectDocumentList(gadget)
      .push(function (document_list) {
        for (i = 0; i < document_list.length; i += 1) {
          renderProjectLine(getProjectId(document_list[i].value.source_project__relative_url),
                            document_list[i].value.portal_type,
                            1, 0);
        }
      });
    })

    .declareJob("renderOutdatedDocumentInfo", function () {
      var gadget = this,
        i,
        document_list,
        limit_date = new Date();
      //TODO Where to define/get the limit date? byt portal_type or the same for all documents?
      limit_date.setFullYear(limit_date.getFullYear() - 1);
      limit_date = limit_date.toISOString();
      //XXX For testing
      limit_date = new Date().toISOString();
      limit_date = limit_date.substring(0, limit_date.length - 5).replace("T", " ");
      return getProjectDocumentList(gadget, limit_date)
      .push(function (document_list) {
        for (i = 0; i < document_list.length; i += 1) {
          renderProjectLine(getProjectId(document_list[i].value.source_project__relative_url),
                            document_list[i].value.portal_type,
                            0, 1);
        }
      });
    })

    .declareJob("renderTestResultInfo", function () {
      var gadget = this,
        i,
        test_list,
        test_result_query = Query.objectToSearchText(
          getComplexQuery({"portal_type" : "Test Result",
                            "source_project__validation_state" : "validated"},
                          "AND")),
        test_state_list = ["failed", "stopped", "public_stopped"];
      test_result_query += ' AND simulation_state: ("' + test_state_list.join('", "') + '")';
      return gadget.jio_allDocs({
        query: test_result_query,
        limit: QUERY_LIMIT,
        select_list: ['source_project__relative_url', 'portal_type'],
        group_by: ['source_project__relative_url'],
        sort_on: [["modification_date", "descending"]]
      })
      .push(function (result) {
        test_list = result.data.rows;
        for (i = 0; i < test_list.length; i += 1) {
          //TODO total and outdated values should come with the test-result-row
          //(all_tests and failed) but those are _local_properties
          renderProjectLine(test_list[i].value.source_project__relative_url,
                            test_list[i].value.portal_type,
                            //
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