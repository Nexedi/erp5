/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt*/
(function (window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt) {
  "use strict";

  /*jshint esnext: true */
  const STATUS_OK = "green";
  const STATUS_NOT_OK = "red";
  const RADIX = 10;

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
                        "AND"));

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

    return gadget.jio_allDocs({
      query: project_query,
      limit: 10000,
      select_list: ['title'],
      sort_on: [["modification_date", "ascending"]]
    })
    .push(function (result) {
      return result.data.rows;
    });
  }

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
          return renderProjectList(project_list);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, SimpleQuery, ComplexQuery, Query, parseInt));