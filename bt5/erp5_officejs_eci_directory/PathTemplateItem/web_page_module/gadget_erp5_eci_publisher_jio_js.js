/*global window, rJS, RSVP, jIO, DOMParser, Object, Intl, encodeURIComponent */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function(window, rJS, RSVP, Object, Intl, encodeURIComponent) {
  "use strict";

  var NA = "-",
    TRUE = "true",
    STAFF = "staff",
    GLOBAL_KPI_DICT = {};

  function createEmptyKpiDict() {
    return {
      "staff": {
        "value": 0,
        "entries": 0,
        "total": 0
      },
      "total_assets": {
        "value": 0,
        "entries": 0,
        "total": 0
      },
      "revenues": {
        "value": 0,
        "entries": 0,
        "total": 0
      },
      "earnings": {
        "value": 0,
        "entries": 0,
        "total": 0
      },
      "source_url": {
        "entries": 0,
        "total": 0
      }
    };
  }

  function updateGlobalKpiDict(kpi_list) {
    if (!kpi_list) {
      return;
    }
    kpi_list.map(function(kpi) {
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
    return kpi_list.map(function(kpi) {
      var value = kpi[key];
      if (value && key !== 'staff') {
        value = new Intl.NumberFormat('en-EN', {
          style: 'currency',
          currency: 'EUR',
          minimumFractionDigits: "0"
        }).format(value.replace(/[^\d.]/g, ''));
      }
      return kpi.year + ":" + (value || NA);
    }).join(" ");
  }

  function createDataSheets(gadget) {
    var kpi_year_list = [], all_data;
    gadget.jio_allDocs = gadget.state_parameter_dict.jio_storage.allDocs;
    gadget.jio_get = gadget.state_parameter_dict.jio_storage.get;
    gadget.jio_put = gadget.state_parameter_dict.jio_storage.put;

    return gadget.jio_allDocs()
      /////////////////////////////////////////////////////////////////
      // Make Publisher datasheets
      /////////////////////////////////////////////////////////////////
      .push(function (data) {
        var promise_list;
        function getKpiYearList(el) {
          return gadget.jio_get(el.id)
            .push(function (result) {
              var i;
              for (i = 0; i < result.kpi_list.length; i += 1) {
                if (result.kpi_list[i].year) {
                  result.kpi_list[i].year = parseInt(result.kpi_list[i].year);
                  if (kpi_year_list.indexOf(result.kpi_list[i].year) === -1){
                    kpi_year_list.push(result.kpi_list[i].year);
                  }
                }
              }
          });
        }
        all_data = data;
        promise_list = data.data.rows.map(getKpiYearList);
        return RSVP.all(promise_list);
      })
      .push(function() {
        var publisher_id_list,
          promise_list;

        function setPortalTypeOnPublisher(el) {
          return gadget.jio_get(el.id)
            .push(function(publisher_object) {
              var i, year_list = [];
              publisher_object.portal_type = "publisher";
              publisher_object.title = publisher_object.title;

              // first punt at financial information
              if (publisher_object.kpi_list === undefined) {
                publisher_object.kpi_list = [];
              }
              for (i = 0; i < publisher_object.kpi_list.length; i += 1) {
                publisher_object.kpi_list[i].year = parseInt( publisher_object.kpi_list[i].year);
                year_list.push( publisher_object.kpi_list[i].year);
              }
              for (i = 0; i < kpi_year_list.length; i += 1) {
                if (year_list.indexOf(kpi_year_list[i]) === -1) {
                  publisher_object.kpi_list.push({
                    "year": kpi_year_list[i],
                    "staff": "",
                    "earnings": "",
                    "total_assets": "",
                    "revenues": ""
                  });
                }
              }
              publisher_object.kpi_list.sort(function (a, b) { return a.year - b.year});
              updateGlobalKpiDict(publisher_object.kpi_list);
              publisher_object.dummy = "";

              publisher_object.location.country_code = publisher_object.location.country.toLowerCase();
              if (window.country_data.hasOwnProperty(publisher_object.location.country_code)) {
                publisher_object.location.country = window.country_data[publisher_object.location.country_code];
              }
              publisher_object.selection_domain_country = [publisher_object.location.country];
              publisher_object.selection_domain_type = [publisher_object.type];
              var year = 0;
              for (i = 0; i < publisher_object.kpi_list.length; i += 1) {
                if (publisher_object.kpi_list[i].year > year) {
                  year = publisher_object.kpi_list[i].year;
                  publisher_object.staff_quantity = publisher_object.kpi_list[i].staff;
                  publisher_object.price = publisher_object.kpi_list[i].revenues
                }
              }
              if (publisher_object.price) {
                publisher_object.price = parseInt(publisher_object.price.slice(0, -3).replace(/\s/g, ''));
              }
              publisher_object.selection_domain_category = []
              for (i = 0; i < publisher_object.solution_list.length; i += 1) {
                if (publisher_object.solution_list[i].category_list) {
                  publisher_object.selection_domain_category = publisher_object.selection_domain_category.concat(publisher_object.solution_list[i].category_list);
                } else {
                  publisher_object.solution_list[i].category_list = [];
                }
              }
              publisher_object.selection_domain_category = Array.from(new Set(publisher_object.selection_domain_category));
              publisher_object.uid = "publisher_" + publisher_object.title;
              if (publisher_object.subsidiary_location_list) {
                publisher_object.subsidiary_location_dict = [];
                for (i = 0; i < publisher_object.subsidiary_location_list.length; i += 1) {
                  publisher_object.subsidiary_location_list[i] = publisher_object.subsidiary_location_list[i].toLowerCase();
                  publisher_object.subsidiary_location_dict.push({
                    "country_code": publisher_object.subsidiary_location_list[i],
                    "country": window.country_data[publisher_object.subsidiary_location_list[i]]
                  });
                }
              }
              return gadget.jio_put(publisher_object.uid, publisher_object);
            });
        }

        publisher_id_list = all_data.data.rows;
        promise_list = publisher_id_list.map(setPortalTypeOnPublisher);

        return new RSVP.Queue()
          .push(function() {
            return RSVP.all(promise_list);
          })
          .push(function() {
            return gadget.jio_put("kpi_dict", {
              portal_type: "kpi",
              data: GLOBAL_KPI_DICT
            });
          });
      })

      .push(function() {
        return gadget.jio_allDocs({
          select_list: ['title', 'solution_list', 'website_url', 'location', 'created', 'type'],
          query: 'portal_type: "publisher"'
        });
      })
      .push(function(publisher_list) {
        var save_software_promise_list,
          publishers,
          promise_list;

        function saveSoftwareListFromPublisher(j) {
          var publisher = j.value.title,
            solution_list = j.value.solution_list,
            website = j.value.website_url;

          function saveSoftwareDocument(software) {
            var i;
            software.portal_type = "solution";
            software.publisher = publisher;
            software.publisher_id = j.id;
            software.publisher_website = website;
            software.uid = "software_" + software.title.replace(/\?/g, '.');
            // For filter
            software.selection_domain_category = software.category_list;
            if (software.similar_solution_list) {
              software.selection_domain_similar_solution = software.similar_solution_list.map(data => data.title);
            } else {
              software.selection_domain_similar_solution = [];
            }
            software.selection_domain_type = [j.value.type];
            software.selection_domain_publisher = [publisher];
            software.selection_domain_country = [j.value.location.country];
            software.selection_domain_licence = software.licence_list;
            software.selection_domain_commercial_support_available = software.commercial_support_available ? 'Yes' : 'No';
            software.selection_domain_floss_software = software.floss_software ? 'Yes' : 'No';
            software.selection_domain_commercial_support_open_source_version = software.commercial_support_open_source_version ? 'Yes' : 'No';
            // put reference value on solution in order to search by reference
            software.selection_domain_reference_industry = [];
            software.selection_domain_reference_country = [];
            software.selection_domain_reference_industry_country_set = [];
            software.reference_list = software.reference_list.filter(reference => !(reference.country == "" && reference.industry == "" && reference.logo_url == "" && reference.title == ""));
            if (software.reference_list && software.reference_list.length > 0) {
              software.has_reference = true;
              for (i = 0; i < software.reference_list.length; i += 1) {
                software.reference_list[i].country_code = software.reference_list[i].country.toLowerCase();
                if (window.country_data.hasOwnProperty(software.reference_list[i].country_code)) {
                  software.reference_list[i].country = window.country_data[software.reference_list[i].country_code];
                }
                software.selection_domain_reference_industry.push(software.reference_list[i].industry);
                software.selection_domain_reference_country.push(software.reference_list[i].country);
                software.selection_domain_reference_industry_country_set.push([software.reference_list[i].industry, software.reference_list[i].country]);
              }
            } else {
              software.has_reference = false;
            }

            if (software.success_case_list && software.success_case_list.length > 0) {
              for (i = 0; i < software.success_case_list.length; i += 1) {
                if (software.success_case_list[i].country) {
                  software.success_case_list[i].country_code = software.success_case_list[i].country.toLowerCase();
                  if (window.country_data.hasOwnProperty(software.success_case_list[i].country_code)) {
                    software.success_case_list[i].country = window.country_data[software.success_case_list[i].country_code];
                  }
                } else {
                  software.success_case_list[i].country = '';
                  software.success_case_list[i].country_code = '';
                }
                if(!software.success_case_list[i].industry) {
                  software.success_case_list[i].industry = '';
                }
              }
            }
            software.modification_date = j.value.created;

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

      .push(function() {
        // category, publisher, similar solution, date
        // industry, country, , client,
        return gadget.jio_allDocs({
          select_list: [
            'title',
            'selection_domain_category',
            'publisher',
            'publisher_id',
            'selection_domain_similar_solution',
            'selection_domain_country',
            'selection_domain_floss_software',
            'modification_date',
            'success_case_list',
            'reference_list'
          ],
          query: 'portal_type: "solution"'
        });
      })
      /////////////////////////////////////////////////////////////////
      // Make Success Case datasheets
      /////////////////////////////////////////////////////////////////
      .push(function(software_list) {
        var softwares,
          promise_list;
        //success case
        function saveSuccessCaseListFromSoftware(softwareObject) {
          var software = softwareObject.value,
            success_case_list = software.success_case_list,
            save_success_case_promise_list;


          function addProperties(success_case) {
            success_case.portal_type = "success_case";
            success_case.software = software.title;
            success_case.software_id = softwareObject.id;
            success_case.publisher = software.publisher;
            success_case.selection_domain_publisher_country = software.selection_domain_country;
            success_case.publisher_id = software.publisher_id;
            success_case.selection_domain_category = software.selection_domain_category;
            success_case.selection_domain_floss_software = software.selection_domain_floss_software;
            success_case.selection_domain_industry = [success_case.industry]
            success_case.selection_domain_country = [success_case.country]
            success_case.selection_domain_publisher = [software.publisher];
            success_case.selection_domain_similar_solution = software.selection_domain_similar_solution
            success_case.modification_date = software.modification_date;

            success_case.uid = "case_" + success_case.title.replace(/\?/g, '.');
            return gadget.jio_put(success_case.uid, success_case);
          }


          function isValid(success_case) {
            return (success_case !== "N/A" &&
              success_case !== "" &&
              success_case.title !== "" &&
              success_case.title !== "N/A");
          }
          save_success_case_promise_list = success_case_list.filter(isValid).map(addProperties);
          return RSVP.all(save_success_case_promise_list);
        }
        softwares = software_list.data.rows.filter(function(sw) {
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

    .ready(function(gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function(jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {
            jio_storage: jio_gadget,
            defer: RSVP.defer()
          };
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('createJio', function() {
      this.state_parameter_dict.jio_storage.createJio({
        check_local_modification: false,
        check_local_creation: false,
        check_local_deletion: false,
        parallel_operation_amount: 100,
        type: "replicate",
        local_sub_storage: {
          type: "query",
          sub_storage: {
            type: "memory"
          }
        },
        remote_sub_storage: {
          type: "query",
          sub_storage: {
            type: "publisher_storage",
            url: "/"
          }
        }
      });
      return this.createDataBase();
    })

    .declareMethod('allDocs', function(options) {
      var gadget = this;
      return new RSVP.Queue(gadget.state_parameter_dict.defer.promise)
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.allDocs(options);
        });
    })
    .declareMethod('getAttachment', function(id, view) {
      var gadget = this;
      return new RSVP.Queue(gadget.state_parameter_dict.defer.promise)
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.getAttachment(id, view);
        });
    })
    .declareMethod('get', function(id) {
      var gadget = this;
      return new RSVP.Queue(gadget.state_parameter_dict.defer.promise)
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.get(id);
        });
    })
    .declareMethod('put', function(object1, object2) {
      var gadget = this;
      return new RSVP.Queue(gadget.state_parameter_dict.defer.promise)
        .push(function () {
          return gadget.state_parameter_dict.jio_storage.put(object1, object2);
        });
    })
    .declareJob('createDataBase', function () {
       var gadget = this;
       return gadget.state_parameter_dict.jio_storage.repair()
         .push(function () {
           return createDataSheets(gadget);
         })
         .push(function () {
           return gadget.state_parameter_dict.defer.resolve('data base created');
         });
    });
}(window, rJS, RSVP, Object, Intl, encodeURIComponent));