/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  const STATUS_OK = "green";
  const STATUS_NOT_OK = "red";

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

  function getProjectElementList(gadget) {

    var i,
      project_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Project",
                         "validation_state" : "validated"},
                        "AND"))/*,
      milestone_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Project Milestone",
                         "parent__validation_state" : "validated",
                         "parent__portal_type" : "Project"},
                        "AND")),
      test_result_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Test Result",
                         "source_project__validation_state" : "validated"},
                        "AND")),
      test_state_list = ["failed", "stopped"];

    console.log("milestone_query:", milestone_query);
    test_result_query += ' AND simulation_state: ("' + test_state_list.join('", "') + '")'*/;

    //TODO filter too old objects?
    /*var date_query, one_year_old_date = new Date();
    one_year_old_date.setFullYear(one_year_old_date.getFullYear() - 1);
    one_year_old_date = one_year_old_date.toISOString();
    one_year_old_date = one_year_old_date.substring(0, one_year_old_date.length - 5).replace("T", " ");
    date_query = new SimpleQuery({
      type: "simple",
      key: "creation_date",
      operator: ">",
      value: one_year_old_date
    });*/

    var document_query,
      portal_type_list = ["Task", "Bug", "Task Report"],
      valid_state_list = ["planned", "ordered", "confirmed", "delivered", "ready"];

    document_query = Query.objectToSearchText(new SimpleQuery({
      key: "source_project__validation_state",
      operator: "=",
      type: "simple",
      value: "validated"
    }));
    // Only way to build these queries using Query objects is by iterating the lists and
    // creating a Simple OR query for each one (then AND)
    // JIO Queries doesn't cover "IN" operator to do a one SimpleQuery like "portal_type IN ('a','b' ... 'etc')"
    document_query += ' AND simulation_state: ("' + valid_state_list.join('", "') + '")';
    document_query += ' AND portal_type: ("' + portal_type_list.join('", "') + '")';

    return new RSVP.Queue()
      .push(function () {
        var promise_list = [],
          limit = [0, 100000];
        //this project query is needed to get each project info like title, etc
        //that can't be get via milestones (there could be a project without milestones)
        //or via documents (documents could be related to a project line and no the project itself)
        promise_list.push(gadget.jio_allDocs({
          query: project_query,
          limit: limit,
          select_list: ['title'],
          sort_on: [["modification_date", "ascending"]]
        }));
        /*promise_list.push(gadget.jio_allDocs({
          query: milestone_query,
          limit: limit,
          select_list: ["title", 'portal_type', "parent__title", "parent__relative_url"],
          //select_list: ["title", 'portal_type', "parent__title", "parent__relative_url", 'count(*)'],
          //select_list: ["parent__title", 'portal_type', 'count(*)'],
          sort_on: [["modification_date", "descending"]]
          //group_by: ['portal_type', 'parent__relative_url']
        }));
        promise_list.push(gadget.jio_allDocs({
          query: test_result_query,
          limit: limit,
          select_list: ['source_project__relative_url', 'portal_type'],
          group_by: ['source_project__relative_url'],
          sort_on: [["modification_date", "descending"]]
        }));
        promise_list.push(gadget.jio_allDocs({
          query: document_query,
          limit: limit,
          select_list: ['source_project__relative_url', 'portal_type', 'count(*)'],
          group_by: ['portal_type', 'source_project__relative_url'],
          sort_on: [["modification_date", "descending"]]
        }));*/
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        return result_list[0].data.rows;
        //return [result_list[0].data.rows, result_list[1].data.rows, result_list[2].data.rows, result_list[2].data.rows];
      });
  }

  //function renderProjectList(project_info_dict, project_list, milestone_list, test_result_list) {
  function renderProjectList(project_list) {
    var i,
      item,
      project_html,
      left_div_html,
      project_html_element_list,
      left_line_html,
      ul_list = document.getElementById("js-project-list"),
      //XXX hardcoded portal_type-title dict (build a template?)
      line_title_list = {"Task": "Tasks",
                         "Test Result" : "Test Results",
                         "Bug" : "Bugs",
                         "Project Milestone" : "Milestones",
                         "Task Report": "Task Reports"},
      project_id,
      project_dict,
      type,
      outdated,
      milestone_limit_date = new Date();
    milestone_limit_date.setFullYear(milestone_limit_date.getFullYear() - 1);

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
        fail = document.createElement('span'),
        total = document.createElement('span');
      line_div.classList.add("project-line");
      status.classList.add("status");
      status.classList.add(status_color);
      status.setAttribute("id", getProjectSpanId(project_id, portal_type, "status"));
      name.classList.add("name");
      name.innerHTML = title;
      total.innerHTML = total_count;
      total.setAttribute("id", getProjectSpanId(project_id, portal_type, "total"));
      //fail.innerHTML = "(" + out_count + ")";
      fail.innerHTML = out_count;
      fail.setAttribute("id", getProjectSpanId(project_id, portal_type, "outdated"));
      line_div.appendChild(status);
      line_div.appendChild(name);
      line_div.appendChild(total);
      line_div.appendChild(fail);
      return line_div;
    }

    for (i = 0; i < project_list.length; i += 1) {
      project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title);
      project_html = project_html_element_list[0];
      left_div_html = project_html_element_list[1];

      for (type in line_title_list) {
        if (line_title_list.hasOwnProperty(type)) {
          left_line_html = createProjectLineHtmlElement(project_list[i].id, type,
                                                        ((line_title_list.hasOwnProperty(type)) ? line_title_list[type] : type),
                                                        0, 0, "none");
          left_div_html.appendChild(left_line_html);
        }
      }
      ul_list.appendChild(project_html);
    }

    /*for (i = 0; i < milestone_list.length; i += 1) {
      project_id = getProjectId(milestone_list[i].id);
      if (!project_info_dict.hasOwnProperty(project_id)) {
        project_info_dict[project_id] = {};
      }
      outdated = (new Date(milestone_list[i].value.modification_date) < milestone_limit_date) ? 1 : 0;
      if (project_info_dict[project_id].hasOwnProperty(milestone_list[i].value.portal_type)) {
        project_info_dict[project_id][milestone_list[i].value.portal_type].total += 1;
        project_info_dict[project_id][milestone_list[i].value.portal_type].total += outdated;
      } else {
        project_info_dict[project_id][milestone_list[i].value.portal_type] = { 'total' : 1, 'outdated' : outdated };
      }
    }

    for (i = 0; i < test_result_list.length; i += 1) {
      project_id = test_result_list[i].value.source_project__relative_url;
      if (!project_info_dict.hasOwnProperty(project_id)) {
        project_info_dict[project_id] = {};
      }
      //TODO for test result, total and outdated are values the test itself should retrieve (all_tests and failed) but those are _local_properties
      project_info_dict[project_id][test_result_list[i].value.portal_type] = { 'total' : 1, 'outdated' : 0 };
    }

    for (i = 0; i < project_list.length; i += 1) {
      project_html_element_list = createProjectHtmlElement(project_list[i].id, project_list[i].value.title);
      project_html = project_html_element_list[0];
      left_div_html = project_html_element_list[1];

      project_dict = project_info_dict[project_list[i].id];
      for (type in project_dict) {
        if (project_dict.hasOwnProperty(type)) {
          left_line_html = createProjectLineHtmlElement(((line_title_list.hasOwnProperty(type)) ? line_title_list[type] : type),
                                                        project_dict[type].total, project_dict[type].outdated,
                                                        ((project_dict[type].outdated > 0) ? STATUS_NOT_OK : STATUS_OK));
          left_div_html.appendChild(left_line_html);
        }
      }
      ul_list.appendChild(project_html);
    }*/
  }

  rJS(window)

    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('render', function (options) {
      if (options.project_info_dict) {
        options.project_info_dict = JSON.parse(options.project_info_dict);
      }
      return this.changeState(options);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      return getProjectElementList(gadget)
        .push(function (project_list) {
          return renderProjectList(project_list);
          //renderProjectList(element_list[3], element_list[0], element_list[1], element_list[2]);
          //renderProjectList(modification_dict.project_info_dict, element_list[0], element_list[1], element_list[2]);
        })
        .push(function (project_list) {
          gadget.myJob();
        });
    })

    .declareJob("myJob", function () {
      console.log("myJob!");
      var gadget = this,
        i, project_id,
        outdated,
        milestone_list,
        status_span,
        status_total,
        status_outdated,
        milestone_query = Query.objectToSearchText(
        getComplexQuery({"portal_type" : "Project Milestone",
                         //"parent__validation_state" : "validated",
                         "validation_state" : "validated",
                         "parent__portal_type" : "Project"},
                        "AND")),
        milestone_limit_date = new Date();
      milestone_limit_date.setFullYear(milestone_limit_date.getFullYear() - 1);
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            query: milestone_query,
            limit: 10000,
            select_list: ["title", 'portal_type', "parent__title", "parent__relative_url"],
            sort_on: [["modification_date", "descending"]]
          })
          .push(function (result) {
            milestone_list = result.data.rows;
            console.log("milestone_list:", milestone_list);
            for (i = 0; i < milestone_list.length; i += 1) {
              console.log("milestone ", milestone_list[i].id);
              project_id = getProjectId(milestone_list[i].id);
              console.log("project_id ", project_id);
              outdated = (new Date(milestone_list[i].value.modification_date) < milestone_limit_date) ? 1 : 0;
              console.log("outdated ", outdated);
              status_span = document.getElementById(getProjectSpanId(project_id, milestone_list[i].value.portal_type, "status"));
              status_total = document.getElementById(getProjectSpanId(project_id, milestone_list[i].value.portal_type, "total"));
              status_outdated = document.getElementById(getProjectSpanId(project_id, milestone_list[i].value.portal_type, "outdated"));
              console.log("status_span ", status_span);
              console.log("status_total ", status_total);
              console.log("status_outdated ", status_outdated);
              console.log("status_total.value ", parseInt(status_total.textContent));
              status_total.textContent = parseInt(status_total.textContent) + 1;
              status_outdated.textContent = parseInt(status_outdated.textContent) + outdated;
              status_span.classList.add((parseInt(status_outdated.textContent) > 0) ? STATUS_NOT_OK : STATUS_OK);
              console.log("");
            }
          });
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query));