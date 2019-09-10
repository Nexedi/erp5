/*global window, rJS, RSVP, jIO, DOMParser, Object */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, Object) {
  "use strict";

  var SPACE = " ",
    DOUBLE_POINT = ":",
    NA = "-",
    TRUE = "true",
    TOTAL = "total",
    ENTRIES = "entries",
    VALUE = "value",
    STR = "",
    GLOBAL_KPI_DICT = {
      2016: getEmptyKpiDict(),
      2017: getEmptyKpiDict(),
      2018: getEmptyKpiDict()
    },
    DIRTY_OLOH_LOOKUP_UNTIL_API_WORKS = {
      "https://www.openhub.net/p/alfresco/analyses/latest/languages_summary": 62894263,
      "https://www.openhub.net/p/swift-lang/analyses/latest/languages_summary": 755449,
      "https://www.openhub.net/p/bluemind/analyses/latest/languages_summary": 857795,
      "https://www.openhub.net/p/drupalcommerce/analyses/latest/languages_summary": 49743,
      "https://www.openhub.net/p/obm/analyses/latest/languages_summary": 363914,
      "https://www.openhub.net/p/linshare/analyses/latest/languages_summary": 185407,
      "https://www.openhub.net/p/linid-directory-manager/analyses/latest/languages_summary": 725443,
      "https://www.openhub.net/p/openpaas/analyses/latest/languages_summary": 228875,
      "https://www.openhub.net/p/magento/analyses/latest/languages_summary": 13507099,
      "https://www.openhub.net/p/mariadb/analyses/latest/languages_summary": 3163137,
      "https://www.openhub.net/p/vscode/analyses/latest/languages_summary": 106972,
      "https://www.openhub.net/p/mongodb/analyses/latest/languages_summary": 1734408,
      "https://www.openhub.net/p/erp5/analyses/latest/languages_summary": 11685522,
      "https://www.openhub.net/p/SlapOS/analyses/latest/languages_summary": 583328,
      "https://www.openhub.net/p/wendelin/analyses/latest/languages_summary": 123904,
      "https://www.openhub.net/p/renderjs/analyses/latest/languages_summary": 52261,
      "https://www.openhub.net/p/odoo/analyses/latest/languages_summary": 2492373,
      "https://www.openhub.net/p/mondrian/analyses/latest/languages_summary": 1319124,
      "https://www.openhub.net/p/PrestaShop/analyses/latest/languages_summary": 539680,
      "https://www.openhub.net/p/symfony/analyses/latest/languages_summary": 1480506,
      "https://www.openhub.net/p/php-twig/analyses/latest/languages_summary": 22572,
      "https://www.openhub.net/p/fabpots_Silex/analyses/latest/languages_summary": 11586,
      "https://www.openhub.net/p/talend-studio/analyses/latest/languages_summary": 287512,
      "https://www.openhub.net/p/xwiki/analyses/latest/languages_summary": 7909332
    };

  // XXX... lord have mercy
  function mockupQueryParam(param, select_list) {
    var wild_param = param.replace(/[()]/g, "%").replace(/ /g, ''),
      return_list = [],
      len,
      i;
    for (i = 0, len = select_list.length; i < len; i += 1) {
      return_list.push(select_list[i] + ':"' + wild_param + '"');
    }
    return ' (' + return_list.join(' OR ') + ')';
  }

  // XXX... lord, I need more mercy
  function updateQuery(query, select_list) {
    var query_param_list = query.split("AND"),
      param,
      len,
      i;
    for (i = 0, len = query_param_list.length; i < len; i += 1) {
      param = query_param_list[i];

      // search
      if (param.split(":").length !== 2) {
        return query.replace(param, mockupQueryParam(param, select_list));
      }

      // hide rows
      if (param.indexOf("catalog.uid") > 0) {
        return query.replace("catalog.", "");
      }
    }
    return query;
  }

  function getEmptyKpiDict() {
    return {
      "staff": {"value": 0, "entries": 0, "total": 0},
      "total_assets": {"value": 0, "entries": 0, "total": 0},
      "revenues": {"value": 0, "entries": 0, "total": 0},
      "earnings": {"value": 0, "entries": 0, "total": 0},
      "public_source": {"entries": 0, "total": 0}
    };
  }

  function updateGlobalKpiDict(data) {
    if (!data) {
      return;
    }
    Object.keys(data).map(function (year) {
      var reported_year = data[year];
      Object.keys(reported_year).map(function (kpi) {
        var reported_value = reported_year[kpi];
        if (reported_value !== TRUE) {
          GLOBAL_KPI_DICT[year][kpi][TOTAL] += 1;
          if (reported_value !== STR) {
            GLOBAL_KPI_DICT[year][kpi][VALUE] += parseInt(reported_value, 10);
            GLOBAL_KPI_DICT[year][kpi][ENTRIES] += 1;
          }
        }
      });
    });
  }

  function S4() {
    return ('0000' + Math.floor(
      Math.random() * 0x10000 /* 65536 */
    ).toString(16)).slice(-4);
  }

  function UUID() {
    return S4() + S4() + "-" +
      S4() + "-" +
      S4() + "-" +
      S4() + "-" +
      S4() + S4() + S4();
  }

  function setKpi(kpi, data) {
    if (kpi === undefined) {
      return "";
    }
    return Object.keys(data).map(function (year) {
      return year + DOUBLE_POINT + (data[year][kpi] || NA);
    }).join(SPACE);
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
              var kpi = publisher_object.kpi_dict;
              publisher_object.portal_type = "publisher";

              // first punt at financial information
              updateGlobalKpiDict(kpi);
              publisher_object.staff = setKpi("staff", kpi);
              publisher_object.revenues = setKpi("revenues", kpi);
              publisher_object.total_assets = setKpi("total_assets", kpi);
              publisher_object.earnings = setKpi("earnings", kpi);

              publisher_object.uid = UUID();
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
            return gadget.jio_put(UUID(), {
              portal_type: "kpi",
              data: GLOBAL_KPI_DICT
            });
          });
      })

      .push(function () {
        return gadget.jio_allDocs({
          select_list: ['title', 'free_software_list', 'website', 'lines'],
          query: 'portal_type: "publisher"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Create Statistic Sheets
      /////////////////////////////////////////////////////////////////
      .push(function (result_list) {
        var publisher_list = result_list.data.rows,
          statistic_list = [],
          i_len = publisher_list.length,
          i;

        // OPENHUB LOOKUP?
        // curl https://www.openhub.net/projects/{project_id}/analyses/latest.xml 

        function createStatisticSheet(my_publisher_row) {
          var software_list = my_publisher_row.value.free_software_list,
            j_len = software_list.length,
            profile_url,
            software_analysis,
            software_analysis_list = [],
            j;

          for (j = 0; j < j_len; j += 1) {
            profile_url = software_list[j].source_code_profile;
            if (profile_url && profile_url !== "") {

              // more yuck
              software_analysis = DIRTY_OLOH_LOOKUP_UNTIL_API_WORKS[profile_url];
              delete DIRTY_OLOH_LOOKUP_UNTIL_API_WORKS[profile_url];
              //software_analysis = jIO.util.ajax({
              //  type: "GET",
              //  "url": profile_url.replace("/languages_summary", ".xml")
              //});
              // prevent multiple entries into calculation
            }
            software_analysis_list.push(software_analysis || 0);
          }

          return new RSVP.Queue()
            .push(function () {
              return RSVP.all(software_analysis_list);
            })
            .push(function (my_stat_list) {
              var line_total = 0,
                k_len = my_stat_list.length,
                k;
              for (k = 0; k < k_len; k += 1) {
                if (my_stat_list[k]) {
                  // xml =  parser.parseFromString(my_stat_list[k],"text/xml");
                  //line_total += xml.getElementsByTagName("total_code_lines")[0]
                  //  .childNodes[0].nodeValue;
                  line_total += my_stat_list[k];
                }
              }
              // actually we need to store this...
              return new RSVP.Queue()
                .push(function () {
                  return gadget.jio_get(my_publisher_row.id);
                })
                .push(function (my_publisher) {
                  my_publisher.lines = line_total;
                  // my_publisher_row.value.lines = line_total.toString();
                  return gadget.jio_put(my_publisher.uid, my_publisher);
                });
            });
        }

        for (i = 0; i < i_len; i += 1) {
          statistic_list.push(createStatisticSheet(publisher_list[i]));
        }

        return new RSVP.Queue()
          .push(function () {
            return RSVP.all(statistic_list);
          })
          .push(function () {
            return result_list;
          });
      })
      /////////////////////////////////////////////////////////////////
      // Make Software datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (publisher_list) {
        var save_software_promise_list,
          publishers,
          promise_list;

        function saveSoftwareListFromPublisher(j) {
          var publisher = j.value.title,
            software_list = j.value.free_software_list,
            website = j.value.website;

          function saveSoftwareDocument(software) {
            software.portal_type = "software";
            software.publisher = publisher;
            software.publisher_website = website;
            software.uid = UUID();

            return gadget.jio_put(software.uid, software);
          }

          save_software_promise_list = software_list.map(saveSoftwareDocument);

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
            'website',
            'success_case_list',
            'publisher',
            'category_list'
          ],
          query: 'portal_type: "software"'
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
            website = softwareObject.value.website,
            success_case_list = softwareObject.value.success_case_list,
            save_success_case_promise_list;

          function isValid(success_case) {
            return (success_case !== "N/A" &&
                    success_case.title !== "" &&
                    success_case.title !== "N/A");
          }

          function addProperties(success_case) {
            success_case.portal_type = "success_case";
            success_case.software = software.title;
            success_case.software_website = software.website;
            success_case.publisher = publisher;
            success_case.publisher_website = website;
            success_case.category_list = software.category_list;
            success_case.uid = UUID();
            return gadget.jio_put(success_case.uid, success_case);
          }

          save_success_case_promise_list =
            success_case_list.filter(isValid)
                             .map(addProperties);

          return RSVP.all(save_success_case_promise_list);
        }

        softwares = software_list.data.rows.filter(function (sw) {
          return (sw.value.success_case_list !== "N/A");
        });
        promise_list = softwares.map(saveSuccessCaseListFromSoftware);

        return RSVP.all(promise_list);
/*
      })
      .push(undefined, function (error) {
        console.log(error);
*/
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
      if (options !== undefined) {
        options.query = updateQuery(options.query, options.select_list);
      }
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
}(window, rJS, RSVP, Object));