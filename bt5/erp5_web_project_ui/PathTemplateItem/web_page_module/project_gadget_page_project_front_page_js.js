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
    NAME_SPAN = "name",
    FORUM_LINK_ID_SUFFIX = "forum",
    FORUM_LINK_TYPE = "link",
    QUERY_LIMIT = 100000,
    SUPERVISOR_FIELD_TITLE = "Supervisor",
    //XXX hardcoded one year old date to define outdated elements
    // Where to define/get the limit date? by portal_type or the same for all documents?
    //date ISO string format: "yyyy-mm-ddThh:mm:ss.mmmm"
    //JIO query date format:  "yyyy-mm-dd hh:mm:ss"
    LIMIT_DATE = new Date(new Date().setFullYear(new Date().getFullYear() - 1))
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
    return segments.slice(0, -1).join("/");
  }

  function getProjectHtlmElementId(project_id, type, suffix, hash_selector) {
    hash_selector = hash_selector ? '#' : '';
    //remove not allowed html id chars (spaces, slashes)
    return hash_selector + [project_id, type, suffix].join("-")
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
    if (total_count > 0) {
      total_span.textContent = parseInt(total_span.textContent, RADIX) + total_count;
    }
    outdated_span.textContent = parseInt(outdated_span.textContent, RADIX) +
      outdated_count;
    if (outdated_count > 0) {
      status_span.classList.remove(STATUS_OK);
      status_span.classList.add(STATUS_NOT_OK);
    } else if (!status_span.classList.value.includes(STATUS_NOT_OK)) {
      status_span.classList.add(STATUS_OK);
    }
    number_span.classList.remove("ui-hidden");
    number_span.classList.add("ui-visible");
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
      select_list: ['title', 'source_decision_title'],
      sort_on: [["modification_date", "ascending"]]
    })
      .push(function (result) {
        return result.data.rows;
      });
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
      status_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                             portal_type, STATUS_SPAN));
      name_span.classList.add("name");
      name_span.classList.add("margined");
      name_span.innerHTML = title;
      name_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                           portal_type, NAME_SPAN));
      total_span.classList.add("margined");
      total_span.innerHTML = total_count;
      total_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                            portal_type, TOTAL_SPAN));
      outdated_span.innerHTML = out_count;
      outdated_span.setAttribute("id", getProjectHtlmElementId(project_id,
                                                               portal_type, OUTDATED_SPAN));
      open_bracket_span.innerHTML = "(";
      close_bracket_span.innerHTML = ")";
      number_span.appendChild(total_span);
      number_span.appendChild(open_bracket_span);
      number_span.appendChild(outdated_span);
      number_span.appendChild(close_bracket_span);
      number_span.setAttribute("id", getProjectHtlmElementId(project_id,
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
          gadget.renderOtdatedMilestoneInfo();
          gadget.renderProjectDocumentInfo();
          gadget.renderOutdatedDocumentInfo();
          gadget.renderTestResultInfo(gadget.state.project_list);
          gadget.renderProjectForumLink();
        });
    })

    .declareJob("renderMilestoneInfo", function () {
      return renderMilestoneLines(this);
    })

    .declareJob("renderOtdatedMilestoneInfo", function () {
      //XXX For testing -> use NOW_DATE
      //return renderMilestoneLines(this, NOW_DATE);
      return renderMilestoneLines(this, LIMIT_DATE);
    })

    .declareJob("renderProjectDocumentInfo", function () {
      return renderProjectDocumentLines(this);
    })

    .declareJob("renderOutdatedDocumentInfo", function () {
      //XXX For testing -> use NOW_DATE
      //return renderProjectDocumentLines(this, NOW_DATE);
      return renderProjectDocumentLines(this, LIMIT_DATE);
    })

    .declareJob("renderTestResultInfo", function (project_list) {
      var gadget = this,
        i,
        test_result,
        query_list = [],
        test_result_query,
        test_state_list = ["failed", "stopped", "public_stopped"];
      return new RSVP.Queue()
        .push(function () {
          var promise_list = [];
          for (i = 0; i < project_list.length; i += 1) {
            query_list = [getComplexQuery({"portal_type" : "Test Result",
                                           "source_project__relative_url" : project_list[i].id},
                                          "AND")];
            query_list.push(createMultipleSimpleOrQuery('simulation_state', test_state_list));
            test_result_query = new ComplexQuery({
              operator: "AND",
              query_list: query_list,
              type: "complex"
            });
            promise_list.push(gadget.jio_allDocs({
              query: Query.objectToSearchText(test_result_query),
              limit: 1,
              select_list: ['source_project__relative_url', 'portal_type', 'modification_date', 'all_tests', 'failures'],
              sort_on: [["modification_date", "descending"]]
            }));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          for (i = 0; i < result_list.length; i += 1) {
            test_result = result_list[i].data.rows[0];
            if (test_result) {
              renderProjectLine(test_result.value.source_project__relative_url,
                                test_result.value.portal_type,
                                parseInt(test_result.value.all_tests, RADIX),
                                parseInt(test_result.value.failures, RADIX));
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
              forum_link_html.href = forum_link_list[i].value.url_string;
              forum_link_html.innerHTML = forum_link_list[i].value.title;
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

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt));