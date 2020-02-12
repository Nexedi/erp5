/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  function getProjectDict(gadget) {
    var query, i,
      milestone_query,
      non_milestone_query,
      aux_complex_query,
      aux_query_list = [],
      query_list = [],
      //TODO: test result will need a differet query because we only need the last test per project, no all
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
        var element_list = result_list[0].data.rows.concat(result_list[1].data.rows);
        var project_list_dict = {};

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

        for (i = 0; i < element_list.length; i += 1) {
          var item = setStatus(element_list[i]),
            status_ok = ((item.status > 0) ? 0 : 1),
            project_id = ((item.value.source_project) ?
                          getProjectId(item.value.source_project) : getProjectId(item.id));
          if (project_id in project_list_dict) {
            if (item.value.portal_type in project_list_dict[project_id]) {
              var project_row = project_list_dict[project_id][item.value.portal_type];
              if (status_ok) {
                project_row.ok_count++;
              } else {
                project_row.out_count++;
                if (project_row.status < item.status) {
                  project_row.status = item.status;
                }
              }
              project_row.list.push(item);
            } else {
              project_list_dict[project_id][item.value.portal_type] = { "status": item.status, "ok_count" : 0 + status_ok, "out_count" : 0 + !status_ok, "list" : [item] };
            }
          } else {
            project_list_dict[project_id] = {};
            project_list_dict[project_id][item.value.portal_type] = { "status": item.status, "ok_count" : 0 + status_ok, "out_count" : 0 + !status_ok, "list" : [item] };
          }
        }
        return project_list_dict;
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
      return getProjectDict(gadget)
        .push(function (project_dict) {
          console.log(project_dict);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query));