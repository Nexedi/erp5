/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  function renderProjectList(element_list) {
    var ul_list = document.getElementById("js-project-list");
    var project_list_dict = {}, i;

    function getProjectId(id) {
      var segments = id.split("/");
      if (segments.length === 2) {
        return id;
      } else {
        return segments.slice(0, -1).join("/");
      }
    }

    function setStatus(item) {
      //TODO check modification date and return item with status 0, 1 or 2 (green, orange, red)
      //we need 2 limit dates that should be based on portal type (e.g. Milestones segmented by months, maybe Taks by weeks)
      //where to set this limits dates? a manifest? site configuration?
      item.status = 0;
      //for quick testing purposes
      if (item.id === "project_module/1/7") {
        item.status = 2;
      }
      if (item.id === "project_module/1/6") {
        item.status = 1;
      }
      //for test results, check validation state (0 = pass, 2 = fail)
      return item;
    }

    function createProjectHtmlElement(project_id) {
      var project_li = document.createElement('li'),
        box_div = document.createElement('div'),
        title_div = document.createElement('div'),
        info_div = document.createElement('div'),
        left_div = document.createElement('div'),
        right_div = document.createElement('div'),
        right_line_div = document.createElement('div'),
        forum_link = document.createElement('a');
      box_div.classList.add("project-box");
      title_div.classList.add("project-title");
      //TODO get project info (another jio query?)
      title_div.innerHTML = project_id;
      info_div.classList.add("project-info");
      left_div.classList.add("left");
      right_line_div.classList.add("project-line");
      forum_link.href = "todo";
      forum_link.innerHTML = project_id + " forum link";
      right_line_div.appendChild(forum_link);
      right_div.appendChild(right_line_div);
      info_div.appendChild(left_div);
      info_div.appendChild(right_div);
      box_div.appendChild(title_div);
      box_div.appendChild(info_div);
      project_li.appendChild(box_div);
      return [project_li, left_div];
    }

    function createProjectLineHtmlElement(portal_type, total_count, out_count) {
      var left_line_div = document.createElement('div'),
        status_span = document.createElement('span'),
        name_span = document.createElement('span'),
        fail_span = document.createElement('span'),
        total_span = document.createElement('span');
      left_line_div.classList.add("project-line");
      status_span.classList.add("status");
      status_span.classList.add("green");//or red or orange
      name_span.classList.add("name");
      name_span.innerHTML = portal_type;
      total_span.classList.add("total"); //create style?
      total_span.innerHTML = total_count;
      fail_span.classList.add("fail"); //create style?
      fail_span.innerHTML = "(" + out_count + ")";

      left_line_div.appendChild(status_span);
      left_line_div.appendChild(name_span);
      left_line_div.appendChild(total_span);
      left_line_div.appendChild(fail_span);
      return [left_line_div, status_span, total_span, fail_span];
    }

    for (i = 0; i < element_list.length; i += 1) {
      var item = setStatus(element_list[i]),
        status_ok = ((item.status > 0) ? 0 : 1),
        project_id = ((item.value.source_project) ?
                      getProjectId(item.value.source_project) : getProjectId(item.id));
      if (project_id in project_list_dict) {
        if (item.value.portal_type in project_list_dict[project_id]) {
          var project_row = project_list_dict[project_id][item.value.portal_type];
          project_row.total_count++;
          project_row.total_html.innerHTML = project_row.total_count;
          if (!status_ok) {
            project_row.out_count++;
            project_row.out_html.innerHTML = "(" + project_row.out_count + ")";
            if (project_row.status < item.status) {
              project_row.status = item.status;
              //TODO
              project_row.status_html.classList.remove("green");
              project_row.status_html.classList.remove("orange");
              project_row.status_html.classList.add("red");
            }
          }
          project_row.list.push(item);
        } else {
          var project_line_html_element_list = createProjectLineHtmlElement(item.value.portal_type, 1, 0 + !status_ok),
            left_line_div = project_line_html_element_list[0],
            status_span = project_line_html_element_list[1],
            total_span = project_line_html_element_list[2],
            fail_span = project_line_html_element_list[3];
          project_list_dict[project_id].left_div_html.appendChild(left_line_div);
          project_list_dict[project_id][item.value.portal_type] = { "status": item.status,
                                                                    "status_html" : status_span,
                                                                    "total_count" : 1,
                                                                    "total_html" : total_span,
                                                                    "out_count" : 0 + !status_ok,
                                                                    "out_html" : fail_span,
                                                                    "list" : [item]
                                                                  };
        }
      } else {
        var project_html_element_list = createProjectHtmlElement(project_id),
          project_li = project_html_element_list[0],
          left_div = project_html_element_list[1],
          project_line_html_element_list = createProjectLineHtmlElement(item.value.portal_type, 1, 0 + !status_ok),
          left_line_div = project_line_html_element_list[0],
          status_span = project_line_html_element_list[1],
          total_span = project_line_html_element_list[2],
          fail_span = project_line_html_element_list[3];
        left_div.appendChild(left_line_div);
        project_list_dict[project_id] = {"html_element" : project_li, "left_div_html" : left_div};
        project_list_dict[project_id][item.value.portal_type] = { "status": item.status,
                                                                  "status_html" : status_span,
                                                                  "total_count" : 1,
                                                                  "total_html" : total_span,
                                                                  "out_count" : 0 + !status_ok,
                                                                  "out_html" : fail_span,
                                                                  "list" : [item],
                                                                  "html_element" : left_line_div
                                                                };
      }
    }
    console.log("project_list_dict:", project_list_dict);
    //TODO iterate projects
    ul_list.appendChild(project_list_dict["project_module/1"].html_element);
    ul_list.appendChild(project_list_dict["project_module/5"].html_element);
    ul_list.appendChild(project_list_dict["project_module/35"].html_element);
  }

  function getProjectElementList(gadget) {
    var query, i,
      milestone_query,
      non_milestone_query,
      aux_complex_query,
      aux_query_list = [],
      query_list = [],
      //TODO: test result will need a differet query because we only need the latest test per project, no all
      portal_type_list = ["Task", "Bug", "Task Report", "Benchmark Result"],
      valid_state_list = ["planned", "ordered", "confirmed", "started", "stopped", "delivered", "ready", "failed", "public_stopped"];

    //validated project milestones
    aux_query_list.push(new SimpleQuery({
      key: "parent__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    aux_query_list.push(new SimpleQuery({
      key: "portal_type",
      operator: "=",
      type: "simple",
      value: "Project Milestone"
    }));
    milestone_query = new ComplexQuery({
      operator: "AND",
      query_list: aux_query_list,
      type: "complex"
    });

    //validated project tasks, bugs, etc
    aux_query_list = [];
    query_list.push(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    //portal types
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
    //states
    aux_query_list = [];
    //for tasks, bugs, reports, tests
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

    non_milestone_query = new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    });
    // TODO: filter result by too old creation/end date? to reduce results

    return new RSVP.Queue()
      .push(function () {
        var promise_list = [],
          //TODO: review limit and fields
          limit = [0, 1000],
          select_list = ['source_project', 'source_project_title', 'portal_type', 'stop_date', 'modification_date', 'simulation_state'];
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
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        return result_list[0].data.rows.concat(result_list[1].data.rows);
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

    .onStateChange(function (modification_dict) {
      var gadget = this;
      return getProjectElementList(gadget)
        .push(function (element_list) {
          console.log("element_list:", element_list);
          renderProjectList(element_list);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query));