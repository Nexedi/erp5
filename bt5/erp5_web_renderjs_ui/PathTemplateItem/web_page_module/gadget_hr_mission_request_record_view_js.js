/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener, promiseEventListener, alertify) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-expense-record-template")
                              .innerHTML,
    template = Handlebars.compile(source),
    resource_type = {
      1: {title: "Occasionnelle", relative_url: "1"},
      2: {title: "Urgence", relative_url: "2"},
      3: {title: "Marketing", relative_url: "3"},
    };

  function getResouceSelectList(gadget, doc) {
    return new RSVP.Queue()
      .push(function (){
        return gadget.allDocs({
          query: 'portal_type:"Service" AND use:"hr/travel_request%"',
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
          if (doc.resource === result.data.rows[i].value.relative_url) {
            tmp.is_selected = true;
          }
          select_options.push(tmp);
        }
        return select_options;
      });
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

    
    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this,
       sync_checked,
       state = getWorkflowState(options),
       not_sync_checked;
      gadget.options = options;

      return new RSVP.Queue()
        .push (function () {
          return getResouceSelectList(gadget, options.doc);
        })
        .push(function (select_options) {
          var ops;
          if (options.doc.sync_flag === '1') {
            sync_checked = 'checked';
          } else {
            not_sync_checked = 'checked';
          }

          ops = {
            select_options: select_options,
            title: options.doc.title,
            destination_node_title: options.doc.destination_node_title,
            site: options.doc.site,
            is_synced: state.sync_state === "Synced",
            start_date: options.doc.start_date|| new Date().toISOString().slice(0,10),
            stop_date: options.doc.stop_date|| new Date().toISOString().slice(0,10),
            quantity: options.doc.quantity,
            comment: options.doc.comment,
            sync_checked:  sync_checked,
            not_sync_checked: not_sync_checked,
            not_readonly: !state.readonly
          };
          if (state.sync_state === 'Synced') {
            ops.state = options.doc.state || state.sync_state;
          } else {
            ops.state = state.sync_state;
          }
          return gadget.translateHtml(template(ops));
        })
        .push(function (html) {
          var discussion_div;
          gadget.props.element.innerHTML = html;
          discussion_div = gadget.props.element.querySelector('.discussion');
          return gadget.declareGadget('gadget_officejs_jio_text_post.html', {element: discussion_div})
            .push(function (discussion_gadget) {
              options.page = 'travel_request_record_list';
              if (["Closed", "Suspended"].indexOf(options.doc.state) !== -1) {
                options.can_add_discussion = true;
              }
              return discussion_gadget.render(options);
            });
        })
        .push(function () {
          return gadget.updateHeader({
            title: gadget.options.jio_key + " " + (gadget.options.doc.record_revision || 1),
            save_action: !state.readonly
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // New version of the the Expense Record
    /////////////////////////////////////////
      /*
    .declareService(function () {
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
        });
    })*/


    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    /*.declareService(function () {
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
          alertify.error(err);
          return  {coords: {latitude: "", longitude: ""}};
        })
        .push(function (result) {
          gadget.props.element.querySelector('input[name="longitude"]').value = result.coords.longitude;
          gadget.props.element.querySelector('input[name="latitude"]').value = result.coords.latitude;
          gadget.props.geoLocation = result;
          gadget.props.deferred1.resolve();
        });
      
      
    })*/
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
            function (submit_event) {
              return getSequentialID(gadget, 'TRR')
                .push(function (source_reference) {
                  var i,
                    doc = {
                      parent_relative_url: "record_module",
                      portal_type: "Travel Request Record",
                      source_reference: source_reference,
                      visible_in_html5_app_flag: 1,
                      record_revision: (gadget.options.doc.record_revision || 1),
                      modification_date: new Date().toISOString()
                    };
                  for (i = 0; i < submit_event.target.length; i += 1) {
                    // XXX Should check input type instead
                    if (submit_event.target[i].name && submit_event.target[i].type != "submit") {
                      if ((submit_event.target[i].type == "radio" || submit_event.target[i].type == "checkbox") && !submit_event.target[i].checked){
                        continue
                      }
                      if (submit_event.target[i].nodeName === "SELECT"){
                        doc[submit_event.target[i].name] = submit_event.target[i].value;
                        doc[submit_event.target[i].name + "_title"] =
                          submit_event.target[i].options[submit_event.target[i].selectedIndex].text;
                      }
                      if (submit_event.target[i].name === "photo") {
                        continue
                      }
                      doc[submit_event.target[i].name] = submit_event.target[i].value;
                    }
                  }
                  if (doc.sync_flag === "1"){
                    sync = 1;
                    doc.simulation_state = 'draft';
                  }
                  return gadget.put(gadget.options.jio_key, doc);
                })
                .push(function () {
                  alertify.success("Saved");
                  if (sync) {
                    return gadget.redirect();
                  }
                });
            }
          )
        })
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
    /*.declareService(function () {
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
    })*/;

}(window, document, RSVP, rJS, Handlebars, loopEventListener, promiseEventListener, alertify));
