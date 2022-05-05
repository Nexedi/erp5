/*global window, rJS, RSVP, jIO, DOMParser, Object, Intl, encodeURIComponent */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, Object, Intl, encodeURIComponent) {
  "use strict";

  var NA = "-",
    TRUE = "true",
    STAFF = "staff",
    GLOBAL_KPI_DICT = {};

  function createEmptyKpiDict() {
    return {
      "staff": {"value": 0, "entries": 0, "total": 0},
      "total_assets": {"value": 0, "entries": 0, "total": 0},
      "revenues": {"value": 0, "entries": 0, "total": 0},
      "earnings": {"value": 0, "entries": 0, "total": 0},
      "source_url": {"entries": 0, "total": 0}
    };
  }

  function updateGlobalKpiDict(kpi_list) {
    if (!kpi_list) {
      return;
    }
    kpi_list.map(function (kpi) {
      var year = kpi.year;
      for (var key in kpi) {
        if (kpi.hasOwnProperty(key) && key !== 'year') {
          var reported_value = kpi[key];
          if (reported_value !== TRUE) {
            if (!GLOBAL_KPI_DICT.hasOwnProperty(year)) {
              GLOBAL_KPI_DICT[year] = createEmptyKpiDict();
            }
            GLOBAL_KPI_DICT[year][key].total += 1;
            if (reported_value !== "") {
              GLOBAL_KPI_DICT[year][key].value += parseInt(reported_value, 10);
              GLOBAL_KPI_DICT[year][key].entries += 1;
            }
          }
        }
      }
    });
  }

  function setKpi(key, kpi_list) {
    if (key === undefined || kpi_list === "") {
      return "";
    }
    return kpi_list.map(function (kpi) {
      var value = kpi[key];
      if (value && key !== 'staff') {
        value = new Intl.NumberFormat('en-EN', {
          style: 'currency',
          currency: 'EUR',
          minimumFractionDigits: "0"
        }).format(value);
      }
      return kpi.year + ":" + (value || NA);
    }).join(" ");
  }

  function createDataSheets(gadget) {
    gadget.jio_allDocs = gadget.state_parameter_dict.jio_storage.allDocs;
    gadget.jio_get = gadget.state_parameter_dict.jio_storage.get;
    gadget.jio_put = gadget.state_parameter_dict.jio_storage.put;

    return gadget.jio_allDocs()
      /////////////////////////////////////////////////////////////////
      // Make Publisher datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (data) {
        var publisher_id_list,
          promise_list;

        function setPortalTypeOnPublisher(el) {
          return gadget.jio_get(el.id)
            .push(function (publisher_object) {
              var kpi_list = publisher_object.kpi_list;
              publisher_object.portal_type = "publisher";

              // first punt at financial information
              if (kpi_list === undefined) {
                kpi_list = [];
              }
               updateGlobalKpiDict(kpi_list);
               publisher_object.staff = setKpi("staff", kpi_list);
               publisher_object.revenues = setKpi("revenues", kpi_list);
               publisher_object.total_assets = setKpi("total_assets", kpi_list);
               publisher_object.earnings = setKpi("earnings", kpi_list);

              publisher_object.uid = "publisher_" + publisher_object.title;
              return gadget.jio_put(publisher_object.uid, publisher_object);
            });
        }

        publisher_id_list = data.data.rows;
        promise_list = publisher_id_list.map(setPortalTypeOnPublisher);

        return new RSVP.Queue()
          .push(function () {
            return RSVP.all(promise_list);
          })
          .push(function () {
            return gadget.jio_put("kpi_dict", {
              portal_type: "kpi",
              data: GLOBAL_KPI_DICT
            });
          });
      })

      .push(function () {
        return gadget.jio_allDocs({
          select_list: ['title', 'solution_list', 'website_url'],
          query: 'portal_type: "publisher"'
        });
      })
      .push(function (publisher_list) {
        var save_software_promise_list,
          publishers,
          promise_list;

        function saveSoftwareListFromPublisher(j) {
          var publisher = j.value.title,
            solution_list = j.value.solution_list,
            website = j.value.website_url;

          function saveSoftwareDocument(software) {
            software.portal_type = "solution";
            software.publisher = publisher;
            software.publisher_website = website;
            software.uid = "software_" + software.title.replace(/\?/g, '.');

            return gadget.jio_put(software.uid, software);
          }
          if (solution_list) {
            save_software_promise_list = solution_list.map(saveSoftwareDocument);
          }
          return RSVP.all(save_software_promise_list);
        }

        publishers = publisher_list.data.rows;
        promise_list = publishers.map(saveSoftwareListFromPublisher);

        return RSVP.all(promise_list);
      })

      .push(function () {
        return gadget.jio_allDocs({
          select_list: [
            'title',
            'publisher_website',
            'success_case_list',
            'publisher',
            'category_list',
            'website_url'
          ],
          query: 'portal_type: "solution"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Success Case datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (software_list) {
        var softwares,
          promise_list;

        function saveSuccessCaseListFromSoftware(softwareObject) {
          var software = softwareObject.value,
            publisher = softwareObject.value.publisher,
            website = softwareObject.value.publisher_website,
            success_case_list = softwareObject.value.success_case_list,
            save_success_case_promise_list;

          function isValid(success_case) {
            return (success_case !== "N/A" &&
                    success_case !== "" &&
                    success_case.title !== "" &&
                    success_case.title !== "N/A");
          }

          function addProperties(success_case) {
            success_case.portal_type = "success_case";
            success_case.software = software.title;
            success_case.software_website = software.website_url;
            success_case.publisher = publisher;
            success_case.publisher_website = website;
            success_case.category_list = software.category_list;
            success_case.uid = "case_" + success_case.title.replace(/\?/g, '.');
            return gadget.jio_put(success_case.uid, success_case);
          }
          save_success_case_promise_list =
            success_case_list.filter(isValid)
                             .map(addProperties);

          return RSVP.all(save_success_case_promise_list);
        }

        softwares = software_list.data.rows.filter(function (sw) {
          return (sw.value.success_case_list !== "N/A" &&
                  sw.value.success_case_list !== "" &&
                  sw.value.success_case_list !== undefined
                 );
        });
        promise_list = softwares.map(saveSuccessCaseListFromSoftware);

        return RSVP.all(promise_list);
      });
  }

  rJS(window)

    .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('createJio', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.createJio({
            check_local_modification: false,
            check_local_creation: false,
            check_local_deletion: false,
            parallel_operation_amount: 100,
            type: "replicate",
            local_sub_storage : {
              type: "query",
              sub_storage: {
                type: "memory"
              }
            },
            remote_sub_storage : {
              type: "query",
              sub_storage: {
                type: "publisher_storage",
                url: "/"
              }
            }
          })
            .push(function () {
              return gadget.state_parameter_dict.jio_storage.repair();
            })
            .push(function () {
              return createDataSheets(gadget);
            });
        });
    })

    .declareMethod('allDocs', function (options) {
      return this.state_parameter_dict.jio_storage.allDocs(options);
    })
    .declareMethod('getAttachment', function (id, view) {
      return this.state_parameter_dict.jio_storage.getAttachment(id, view);
    })
    .declareMethod('get', function (id) {
      return this.state_parameter_dict.jio_storage.get(id);
    })
    .declareMethod('put', function (object1, object2) {
      return this.state_parameter_dict.jio_storage.put(object1, object2);
    })
    .declareMethod('repair', function () {
      return this.state_parameter_dict.jio_storage.repair();
    });
}(window, rJS, RSVP, Object, Intl, encodeURIComponent));