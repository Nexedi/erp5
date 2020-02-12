/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  //TODO
  //get lastest (unique) TR for each project
  function getProjectElementList(gadget) {

    //TODO ATTEMPT TO FILTER BY DATE
    var date_query_list = [],
      date_query,
      now_date = new Date(),
      one_year_old_date = new Date();
    one_year_old_date.setFullYear(one_year_old_date.getFullYear() - 1);

    //var date = "Wed, 16 Oct 2019 09:06:19 +0000";
    //var js_date = new Date(date);
    /*date_query_list.push(new SimpleQuery({
      key: "portal_type",
      operator: "=",
      type: "simple",
      value: "Task"
    }));
    date_query_list.push(new SimpleQuery({
      type: "simple",
      key: "creation_date",
      value: {"query": one_year_old_date, "range": ">="}
      //value: {'query': (one_year_old_date, now_date), 'range': 'minmax'}
    }));
    date_query = new ComplexQuery({
      operator: "AND",
      query_list: date_query_list,
      type: "complex"
    });*/
    date_query = new SimpleQuery({
      type: "simple",
      key: "creation_date",
      value: {"query": one_year_old_date, "range": ">="}
      //value: {'query': (one_year_old_date, now_date), 'range': 'minmax'}
    });

    function getComplexQuery(query_dict, operator) {
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
      return new ComplexQuery({
        operator: operator,
        query_list: query_list,
        type: "complex"
      });
    }

    var i,
      project_query = getComplexQuery({"portal_type" : "Project",
                                       "validation_state" : "validated"},
                                      "AND"),
      milestone_query = getComplexQuery({"portal_type" : "Project Milestone",
                                         "parent__validation_state" : "validated"},
                                        "AND"),
      non_milestone_query,
      aux_complex_query,
      aux_query_list = [],
      query_list = [],
      portal_type_list = ["Task", "Bug", "Task Report", "Benchmark Result"],
      valid_state_list = ["planned", "ordered", "confirmed", "started", "stopped", "delivered", "ready", "failed", "public_stopped"];

    //validated project tasks, bugs, etc
    query_list.push(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));

    //portal types
    /*//ATTEMPT 1 TO AVOID ITERATE portal_type VALUE LIST
    //(from jio documentation)
    var in_list = function (object_value, comparison_value_list) {
      return comparison_value_list.indexOf(object_value) >= 0;
    };
    aux_complex_query = new SimpleQuery({
      type: "simple",
      key: {
        read_from: "portal_type",
        equal_match: in_list
      },
      value: ["Task", "Bug", "Task Report", "Benchmark Result"]
    });
    // in_list function is never called, no query on portal types

    //ATTEMPT 2 TO AVOID ITERATE portal_type VALUE LIST (same for states)
    aux_complex_query = new SimpleQuery({
      key: "portal_type",
      operator: "=",
      type: "simple",
      value: ("Task", "Bug", "Task Report", "Benchmark Result")
    });
    //only last portal type value of the list is considered
    //the rest, ignored*/

    aux_query_list = [];
    for (i = 0; i < portal_type_list.length; i += 1) {
      aux_query_list.push(new SimpleQuery({
        key: "portal_type",
        operator: "=",
        type: "simple",
        value: portal_type_list[i]
      }));
    }
    aux_complex_query = new ComplexQuery({
      operator: "OR",
      query_list: aux_query_list,
      type: "complex"
    });
    query_list.push(aux_complex_query);

    //states for tasks, bugs, reports, tests
    aux_query_list = [];
    for (i = 0; i < valid_state_list.length; i += 1) {
      aux_query_list.push(new SimpleQuery({
        key: "simulation_state",
        operator: "=",
        type: "simple",
        value: valid_state_list[i]
      }));
    }
    aux_complex_query = new ComplexQuery({
      operator: "OR",
      query_list: aux_query_list,
      type: "complex"
    });
    query_list.push(aux_complex_query);

    
    // TODO: filter result by too old creation date? to reduce results
    query_list.push(date_query);
    
    non_milestone_query = new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    });

    return new RSVP.Queue()
      .push(function () {
        var promise_list = [],
          //TODO: review limit and fields
          limit = [0, 1000],
          select_list = ['source_project', 'portal_type', 'stop_date', 'modification_date', 'simulation_state', 'creation_date'];
        // XXX: two separated queries because this query fails with not implemented error:
        // ( parent__validation_state = "validated" OR source_project__validation_state = "validated" )
        // TODO: do some research
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(milestone_query),
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(non_milestone_query),
          limit: limit,
          select_list: select_list,
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(project_query),
          limit: limit,
          select_list: ['title'],
          sort_on: [["modification_date", "descending"]]
        }));
        /*promise_list.push(gadget.jio_allDocs({
          query: Query.objectToSearchText(date_query),
          limit: [0, 30],
          select_list: ['title', 'creation_date'],
          sort_on: [["creation_date", "descending"]]
        }));*/
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        return [result_list[0].data.rows.concat(result_list[1].data.rows), result_list[2].data.rows];
      });
  }

  function renderProjectList(element_list, project_list) {
    var i,
      project,
      item,
      status_ok,
      project_id,
      project_row,
      project_li,
      project_html_element_list,
      project_line_html_element_list,
      left_div,
      left_line_div,
      status_span,
      total_span,
      fail_span,
      ul_list = document.getElementById("js-project-list"),
      project_list_dict = {};

    function getProjectId(id) {
      var segments = id.split("/");
      if (segments.length === 2) {
        return id;
      }
      return segments.slice(0, -1).join("/");
    }

    function setStatus(item) {
      //TODO check modification date and return item with status 0, 1 or 2 (green, orange, red)
      //we need 2 limit dates that should be based on portal type (e.g. Milestones segmented by months, maybe Taks by weeks)
      //where to set this limits dates? a manifest? site configuration?
      var js_date = new Date(item.value.modification_date);
      item.status = 0;
      item.status_color = "green";
      //for quick testing purposes
      if (item.id === "project_module/1/7") {
        item.status = 2;
        item.status_color = "red";
      }
      if (item.id === "project_module/1/6") {
        item.status = 1;
        item.status_color = "orange";
      }
      if (item.id === "bug_module/5") {
        item.status = 1;
        item.status_color = "orange";
      }
      //for test results, check validation state (0 = pass, 2 = fail)
      return item;
    }

    function createProjectHtmlElement(project_id, project_title) {
      var project_element = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_info_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        forum_link = document.createElement('a');
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      title_div.innerHTML = project_title;
      info_div.classList.add("project-info");
      left_info_div.classList.add("left");
      right_line_div.classList.add("project-line");
      forum_link.href = "todo";
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

    function createProjectLineHtmlElement(portal_type, total_count, out_count, status_color) {
      var line_div = document.createElement('div'),
        status = document.createElement('span'),
        name = document.createElement('span'),
        fail = document.createElement('span'),
        total = document.createElement('span');
      line_div.classList.add("project-line");
      status.classList.add("status");
      status.classList.add(status_color);
      name.classList.add("name");
      name.innerHTML = portal_type;
      total.innerHTML = total_count;
      fail.innerHTML = "(" + out_count + ")";
      line_div.appendChild(status);
      line_div.appendChild(name);
      line_div.appendChild(total);
      line_div.appendChild(fail);
      return [line_div, status, total, fail];
    }

    for (i = 0; i < project_list.length; i += 1) {
      project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title);
      project_list_dict[project_list[i].id] = {"html_element" : project_html_element_list[0],
                                       "left_div_html" : project_html_element_list[1]};
    }

    for (i = 0; i < element_list.length; i += 1) {
      item = setStatus(element_list[i]);
      status_ok = ((item.status > 0) ? 0 : 1);
      project_id = ((item.value.source_project) ?
                    getProjectId(item.value.source_project) : getProjectId(item.id));
      if (project_list_dict.hasOwnProperty(project_id)) {
        if (project_list_dict[project_id].hasOwnProperty(item.value.portal_type)) {
          project_row = project_list_dict[project_id][item.value.portal_type];
          project_row.total_count += 1;
          project_row.total_html.innerHTML = project_row.total_count;
          if (!status_ok) {
            project_row.out_count += 1;
            project_row.out_html.innerHTML = "(" + project_row.out_count + ")";
            if (project_row.status < item.status) {
              project_row.status = item.status;
              project_row.status_html.classList.remove("green", "red", "orange");
              project_row.status_html.classList.add(item.status_color);
            }
          }
        } else {
          project_line_html_element_list = createProjectLineHtmlElement(item.value.portal_type, 1, 0 + !status_ok, item.status_color);
          left_line_div = project_line_html_element_list[0];
          status_span = project_line_html_element_list[1];
          total_span = project_line_html_element_list[2];
          fail_span = project_line_html_element_list[3];
          project_list_dict[project_id].left_div_html.appendChild(left_line_div);
          project_list_dict[project_id][item.value.portal_type] = { "status": item.status,
                                                                    "status_html" : status_span,
                                                                    "total_count" : 1,
                                                                    "total_html" : total_span,
                                                                    "out_count" : 0 + !status_ok,
                                                                    "out_html" : fail_span
                                                                  };
        }
      }
    }
    console.log("project_list_dict:", project_list_dict);
    for (project in project_list_dict) {
      if (project_list_dict.hasOwnProperty(project)) {
        ul_list.appendChild(project_list_dict[project].html_element);
      }
    }
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
        .push(function (element_list) {
          console.log("element_list:", element_list);
          renderProjectList(element_list[0], element_list[1]);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query));