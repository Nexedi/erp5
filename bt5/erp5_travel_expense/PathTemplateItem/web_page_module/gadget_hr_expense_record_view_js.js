/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener, promiseEventListener, alertify) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-expense-record-template")
                              .innerHTML,
    template = Handlebars.compile(source),

    relation_listview_source = gadget_klass.__template_element
                         .getElementById("relation-listview-template")
                         .innerHTML,
    relation_listview_template = Handlebars.compile(relation_listview_source),

    searching = "animation ui-btn ui-corner-all ui-btn-icon-notext" +
        " ui-input-clear ui-icon-spinner ui-icon-spin",
    searched = "animation ui-hidden-accessible",
    jump_on = "animation ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-plane ui-shadow-inset ui-input-clear",
    jump_off = jump_on +  " ui-disabled",
    jump_unknown = "animation ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-warning ui-shadow-inset ui-input-clear ui-disabled";



  function getData(gadget) {
    var form = gadget.props.element.querySelector('form');
    return getSequentialID(gadget, 'EXP')
      .push(function (source_reference) {
        var i,
          doc = {
            parent_relative_url: "expense_record_module",
            portal_type: "Expense Record Temp",
            source_reference: source_reference,
            visible_in_html5_app_flag: 1,
            record_revision: (gadget.options.doc.record_revision || 1),
            photo_data: gadget.options.doc.photo_data || "",
            modification_date: new Date().toISOString()
          };
        for (i = 0; i < form.length; i += 1) {
            // XXX Should check input type instead
          if (form[i].name && form[i].type != "submit") {
            if ((form[i].type == "radio" || form[i].type == "checkbox") && !form[i].checked){
              continue;
             }
            if (form[i].name === "photo") {
              continue;
            }
            if (form[i].nodeName === "SELECT"){
              doc[form[i].name] = form[i].value;
              doc[form[i].name + "_title"] =
                form[i].options[form[i].selectedIndex].text;
            }
            doc[form[i].name] = form[i].value;
          }
        }
        if (doc.sync_flag === "1"){
          doc.simulation_state = 'draft';
          doc.portal_type = 'Expense Record'; // For to avoid sync
        }
      doc.related_mission_url = gadget.props.related_mission_url;
      return doc;
      });  
  }
  function getWorkflowState(id, sync_flag)  {
    var sync_state;
    if(id.indexOf("_module/") > 0){
      sync_state = "Synced";
    }else if(sync_flag){
      sync_state = "Not Synced";
    }else{
      sync_state = "Not Ready To Sync";
    }
    return sync_state;
  }

  function getTypeSelectList(gadget, doc) {
    return new RSVP.Queue()
      .push(function (){
        return gadget.allDocs({
          query: 'portal_type:"Service" AND use:"hr/expense_validation_request%"',
          select_list: ['relative_url', 'title'],
          limit: [0, 100]
        });
      })
      .push(function (result) {
        var i = 0,
          tmp,
          ops,
          select_options = [];
        for (i = 0; i < result.data.total_rows; i += 1) {
          tmp = {
            title: result.data.rows[i].value.title,
            value: result.data.rows[i].value.relative_url
          };
          if (doc.type === result.data.rows[i].value.relative_url) {
            tmp.is_selected = true;
          }
          select_options.push(tmp);
        }
        return select_options;
      });
  }

  function geoLocationPromise() {
    return new Promise(function (resolve, reject) {
      var err;
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (result) {
          resolve(result);
        }, function (error) {
          switch(error.code) {
            case error.PERMISSION_DENIED:
              err = new Error("User denied the request for Geolocation");
              break;
            case error.POSITION_UNAVAILABLE:
              err =  new Error("Location information is unavailable");
              break;
            case error.TIMEOUT:
              err = new Error("The request to get user location timed out");
              break;
            default:
              err = new Error("An unknown error occurred");
              break;
          }
          reject(err);
        },
        {maximumAge:60000, timeout:20000});
      } else {
        reject(new Error("Geolocation is not supported by this browser"));
    }
    });
  }
  function getSequentialID(gadget, record_type_prefix){
    var last_sequential_id,
      prefix,
      date = new Date(),
      date_text = date.getFullYear()+('0'+(date.getMonth()+1)).slice(-2)+('0'+date.getDate()).slice(-2);
    return new RSVP.Queue()
      .push(function () {
        if (gadget.options.doc.source_reference) {
          return gadget.options.doc.source_reference;
        } else {
          return new RSVP.Queue()
            .push(function () {
              return new RSVP.all([
                gadget.getSetting('last_sequential_id'),
                gadget.getSetting('sequential_id_prefix')
              ]);
            })
           .push(function (result_list) {
             if (result_list[0]) {
              last_sequential_id = Number(result_list[0]);
             } else {
              last_sequential_id = 0;
             }
            last_sequential_id += 1;
            if (result_list[1]) {
              prefix = result_list[1];
            } else {
             prefix = getRandomPrefixForID();
            }
            return RSVP.all([
              gadget.setSetting('last_sequential_id', last_sequential_id),
              gadget.setSetting('sequential_id_prefix', prefix)
            ]);
           })
          .push(function () {
           return record_type_prefix + '-' + date_text + '-' + prefix + ('0000'+last_sequential_id).slice(-5);
          });
        }
      });
  }

  function getRandomPrefixForID(){
    function random(){
      return 65 + Math.floor( Math.random() * 26 );
    }
    return String.fromCharCode(random())+String.fromCharCode(random())+String.fromCharCode(random());
  }

  gadget_klass
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          alertify.set({ delay: 1500 });
          g.props = {};
          g.props.element = element;
          g.props.deferred = RSVP.defer();
          g.props.deferred1 = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('jio_remove', 'jio_remove')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('setSetting', 'setSetting')
    .declareAcquiredMethod("repair", "jio_repair")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    
    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this,
       sync_checked,
       sync_state = getWorkflowState(options.jio_key, options.doc.sync_flag),
       geoLocation,
       related_mission_class,
       related_mission_url,
       related_mission,
       not_sync_checked;
      gadget.options = options;

      return new RSVP.Queue()
        .push(function () {
          if(options.came_from_jio_key) {
           gadget.props.related_mission_url = options.came_from_jio_key;
           return gadget.get(options.came_from_jio_key)
             .push(function (data) {
               related_mission_class = jump_on;
               related_mission = data.title;
               options.doc.related_mission = related_mission;
               options.doc.related_mission_url = gadget.props.related_mission_url;
               //saved when return from listbox
               return gadget.put(gadget.options.jio_key, options.doc);
             })
             .push(function () {
               return gadget.getUrlFor({jio_key: options.came_from_jio_key, page: 'view'});
             });
          } else {
            related_mission = options.doc.related_mission;
            if (options.doc.related_mission_url) {
              related_mission_class = jump_on;
              gadget.props.related_mission_url = options.doc.related_mission_url;
              return gadget.getUrlFor({jio_key: options.doc.related_mission_url, page: 'view'});
            } else {
              if (related_mission) {
                related_mission_class = jump_unknown;
              } else {
                related_mission_class = jump_off;
              }
              return;
            }
          }
        })
        .push (function (url) {
          related_mission_url = url;
          if (sync_state === 'Synced') {
            geoLocation= {coords: {latitude: options.doc.latitude, longitude: options.doc.longitude}};
          } else {
            geoLocation = {coords: {latitude: "", longitude: ""}};
          }
          gadget.props.geoLocation = geoLocation;
          return RSVP.all([
            gadget.allDocs({
              query: 'portal_type:"Currency"',
              select_list: ['relative_url', 'title'],
              limit: [0, 100]
            }),
            getTypeSelectList(gadget, options.doc)
          ]);
        })
        .push(function (result_list) {
          var i = 0,
            tmp,
            ops,
            select_options = [],
            result = result_list[0];
          if (options.doc.resource === undefined) {
            options.doc.resource = "currency_module/2";            
          }
          for (i = 0; i < result.data.total_rows; i += 1) {
            tmp = {
              title: result.data.rows[i].value.title,
              value: result.data.rows[i].value.relative_url
            };
            if (options.doc.resource === result.data.rows[i].value.relative_url) {
              tmp.is_selected = true;
            }
            select_options.push(tmp);
          }
          if (options.doc.sync_flag === '1') {
            sync_checked = 'checked';
          } else {
            not_sync_checked = 'checked';
          }
          ops = {
            state: options.doc.state || sync_state,
            preview: options.doc.photo_data,
            quantity: options.doc.quantity,
            date: options.doc.date || new Date().toISOString().slice(0,10),
            comment: options.doc.comment,
            sync_checked:  sync_checked,
            not_sync_checked: not_sync_checked,
            select_options: select_options,
            type_options: result_list[1],
            longitude: geoLocation.coords.longitude || "",
            latitude: geoLocation.coords.latitude || "",
            related_mission_url: related_mission_url || "",
            related_mission_class: related_mission_class,
            related_mission: related_mission
          };
          if (sync_state !== 'Synced') {
            ops.not_readonly = true;
          }
          return template(ops);
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          
          return gadget.updateHeader({
            title: gadget.options.jio_key + " " + (gadget.options.doc.record_revision || 1),
            save_action: sync_state === 'Synced'? false: true
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // New version of the the Expense Record
    /////////////////////////////////////////
    .declareService(function () {
      /*
      var gadget = this,
        cloned_doc,
        current_doc,
        new_id;

      if(gadget.props.element.querySelector('input[type=button][name=create_new_version]') == null){
        return;
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('input[type=button][name=create_new_version]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.get(gadget.options.jio_key);
        })
        .push(function (result) {
          current_doc = result;
          cloned_doc = JSON.parse(JSON.stringify(result));

          // Do not sync the cloned document
          cloned_doc.copy_of = gadget.options.jio_key;
          cloned_doc.visible_in_html5_app_flag = 1;
          delete cloned_doc.sync_flag;
          cloned_doc.portal_type = 'Expense Record Temp';
          cloned_doc.record_revision = (cloned_doc.record_revision || 1) + 1;

          current_doc.visible_in_html5_app_flag = 0;

          return gadget.post(cloned_doc);
        })
        .push(function (id) {
          new_id = id;
          // Hide the document at the end in order to still view it in case of issue
          // Better have 2 docs than none visible
          return gadget.put(gadget.options.jio_key, current_doc);
        })
        .push(function (response) {
          return gadget.redirect({
            jio_key: new_id,
            page: "view"
          });
        });*/
    })


    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
       state = getWorkflowState(gadget.options.jio_key, gadget.options.doc.sync_flag);
      if (state === 'Synced') {
        gadget.props.deferred1.resolve();
        return;
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          alertify.log('searching GPS');
          return geoLocationPromise();
        })
        .push(function(result) {
          alertify.success('GPS found');
          return result;
        }, function(err) {
          alertify.error("GPS Localization Stopped");
          console.log(err);
          return  {coords: {latitude: "", longitude: ""}};
        })
        .push(function (result) {
          gadget.props.element.querySelector('input[name="longitude"]').value = result.coords.longitude;
          gadget.props.element.querySelector('input[name="latitude"]').value = result.coords.latitude;
          gadget.props.geoLocation = result;
          gadget.props.deferred1.resolve();
        });
      
      
    })
    .declareService(function () {
      var gadget = this,
        sync,
        form = gadget.props.element.querySelector('form.view-expense-record-form');
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            form,
            'submit',
            false,
            function () {
              return getData(gadget)
                .push(function (doc) {
                  if (doc.sync_flag === '1') {
                    sync = 1;
                  }
                  return gadget.put(gadget.options.jio_key, doc);
                })
                .push(function () {
                  if (sync) {
                  return gadget.repair()
                   .push(function () {
                     return gadget.redirect({page: 'expense_record_list'});
                   })
                   .push(function () {
                     alertify.success("Saved");
                   });
                  } else {
                    alertify.success("Saved");
                  }
                });
            }
          )
        })
    })
    .declareService(function () {
      var gadget = this,
       canvas = document.createElement('canvas'),
       img,
       ctx,
       preview = gadget.props.element.querySelector('img[name="preview"]');

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('input[name="photo"]'),
            "change",
            false,
            function (evt) {
              if (evt.target.files.length) {
                return new RSVP.Queue()
                  .push(function () {
                    return jIO.util.readBlobAsDataURL(evt.target.files[0]);
                  })
                  .push(function (result) {
                    img = new Image();
                    img.src = result.target.result;
                    
                    return RSVP.all([
                      gadget.props.deferred1.promise,
                      promiseEventListener(img, 'load', false)
                      ]);
                  })
                  .push(function () {
                    /*
                    ctx = canvas.getContext("2d");
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0, img.width, img.height);
                    ctx.font = (canvas.width * 70 / 2000) + 'px sans-serif';
                    ctx.fillText('Longitude: ' + gadget.props.geoLocation.coords.longitude +" Latitude: " + gadget.props.geoLocation.coords.latitude, 0, canvas.height - 20);
                    gadget.options.doc.photo_data = canvas.toDataURL();
                    */
                    gadget.options.doc.photo_data = img.src;
                    preview.src = gadget.options.doc.photo_data;
                  });
              }
            }
          );
        });
    })
    
    /*
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          if (gadget.options.doc.sync_flag == "1"){
            var element = gadget.props.element.querySelector("input[name='sync_flag'][value='1']");
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }else{
            var element = gadget.props.element.querySelector("input[name='sync_flag'][value='']");
            element.setAttribute('checked', 'checked');
            $(element).checkboxradio('refresh');
          }
        })
    })
*/
    /////////////////////////////////////////
    // Preview clicked.
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        img =  gadget.props.element.querySelector('img[name="preview"]'),
        modal = gadget.props.element.querySelector('.modal'),
        modalImg =  gadget.props.element.querySelector('img[name="img01"]'),
        span = gadget.props.element.querySelector('.close');

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            img,
            "click",
            false,
            function (evt) {
              modal.style.display = "block";
              modalImg.src = evt.target.src;
              return new RSVP.Queue()
                .push(function () {
                  return promiseEventListener(span, 'click', false);
                })
                .push(function () {
                    modal.style.display = "none";
                });
            }
          );
        });
    })
     .declareService(function () {
      var gadget = this,
        my_value,
        props = gadget.props,
        input = gadget.props.element.querySelector('.relation_input'),
        ul = gadget.props.element.querySelector(".search_ul"),
        animation = gadget.props.element.querySelector('.animation');

      function generateList(event) {
        my_value = event.target.value;
        ul.innerHTML = "";
        gadget.props.related_mission_url = '';
        if (my_value === "") {
          animation.className = searched;
          return;
        }
        animation.className = searching;
        return new RSVP.Queue()
          .push(function () {
            return gadget.allDocs({
              "query": 'portal_type: "Travel Request Record" AND state: "Accepted" AND title: %' + my_value + '%',
              "limit": [0, 11],
              "select_list": ['title']
            });
          })
          .push(function (result) {
            var list = [],
              i,
              html;
            for (i = 0; i < result.data.rows.length; i += 1) {
              list.push({
                id: result.data.rows[i].id,
                value: result.data.rows[i].value['title']
              });
            }
            animation.className = searched;
            html =  relation_listview_template({
              list: list,
              value: my_value
            });
            $(ul).toggle();
            ul.innerHTML = html;
            $(ul).toggle();
          });
      }
      function setSelectedElement(event) {
        var element = event.target,
          jump_url = element.getAttribute("data-relative-url");
        ul.innerHTML = "";
        if (jump_url) {
          input.value = element.textContent;
          return gadget.getUrlFor({jio_key: jump_url, page: 'view'})
          .push(function (url) {
              gadget.props.related_mission_url = jump_url;
              animation.href = url;
              animation.className = jump_on;
          });
        } else {
           return getData(gadget)
             .push(function (doc) {
               doc.sync_flag = "0";
               doc.portal_type = 'Expense Record Temp';
               return gadget.put(gadget.options.jio_key, doc);
             })
             .push(function () {
               return gadget.redirect({
                 page: 'travel_request_record_list',
                 came_from_jio_key: gadget.options.jio_key,
                 search: my_value
               });
          });
        }
      }

      return RSVP.all([
        loopEventListener(input, 'input', false, generateList),
        loopEventListener(input, 'blur', false, function () {
          return new RSVP.Queue()
            .push(function () {
              return RSVP.any([
                RSVP.delay(200),
                promiseEventListener(ul, "click", true)
              ]);
            })
            .push(function (event) {
              if (event) {
                return setSelectedElement(event);
              }
              if (ul.innerHTML) {
                ul.innerHTML = "";
                animation.className = jump_unknown;
              }
            });
        })]
        );
    });

}(window, document, RSVP, rJS, Handlebars, loopEventListener, promiseEventListener, alertify));
