/*global window, rJS, btoa, Handlebars, $, Rusha */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, btoa, Handlebars, $, Rusha) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    parameters_widget_template = Handlebars.compile(
      templater.getElementById("parameters-widget-template").innerHTML
    ),
    instance_widget_template = Handlebars.compile(
      templater.getElementById("instance-details-widget-overview").innerHTML
    ),
    rusha = new Rusha();

  function generateHash(str) {
    return rusha.digestFromString(str);
  }

  function getInstanceDict(gadget, monitor_dict) {
    var private_url = monitor_dict._links.private_url.href.replace("jio_private", "private"),
      public_url = monitor_dict._links.public_url.href.replace("jio_public", "public"),
      pass_url = "https://" + atob(gadget.state.opml.basic_login) +
              "@" + private_url.split("//")[1];

    return {
      key: monitor_dict.reference,
      title: monitor_dict.title,
      date: monitor_dict.date,
      status: monitor_dict.status,
      instance: monitor_dict._embedded.instance || '',
      public_url: public_url,
      private_url: pass_url,
      rss_url: monitor_dict._links.rss_url.href || '',
      resource_url: "#page=resource_view&key=" + monitor_dict.parent_id,
      process_url: "#page=process_view&key=" + monitor_dict.parent_id,
      instance_url: "#page=software_instance_view&key=" + monitor_dict.reference,
      parameters: monitor_dict.parameters,
      warning: (monitor_dict.status.toUpperCase() === "WARNING") ? true : false
    };
  }

  gadget_klass
    .setState({
      render_deferred: "",
      opml: "",
      instance_list: ""
    })
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.changeState({"render_deferred": RSVP.defer()});
    })
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;
      return gadget.updateHeader({
          title: 'Hosting Subscriptions View'
        })
        .push(function () {
          return gadget.jio_get(options.key);
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc});
        })
        .push(function () {
          return gadget.jio_allDocs({
              query: '(portal_type:"opml-outline") AND (parent_id:"' +
                generateHash(options.key) + '")'
          });
        })
        .push(function (ouline_list) {
          var j,
            promise_list = [];
          for (j = 0; j < ouline_list.data.total_rows; j += 1) {
            // fetch all instances
            promise_list.push(
              gadget.jio_allDocs({
                select_list: [
                  "reference",
                  "parent_id",
                  "status",
                  "date",
                  "_embedded",
                  "_links",
                  "parameters",
                  "title"],
                query: '(portal_type:"global") AND (parent_id:"' +
                  ouline_list.data.rows[j].id + '")'
              })
            );
          }
          return RSVP.all(promise_list);
        })
        .push(function (document_list) {
          var parameter_content,
            instance_list = [],
            parameter_list = [],
            status_url = '',
            i,
            instance_content;

          gadget.element.querySelector('.hosting-block .overview-title span')
            .textContent = gadget.state.opml.title;

          for (i = 0; i < document_list.length; i += 1) {
            // Only one instance per opml-outline
            if (document_list[i].data.total_rows === 1) {
              instance_list.push(
                getInstanceDict(gadget, document_list[i].data.rows[0].value)
              );
              if (document_list[i].data.rows[0].value.hasOwnProperty('parameters')) {
                parameter_list.push({
                  title: document_list[i].data.rows[0].value.title,
                  parameters: document_list[i].data.rows[0].value.parameters,
                  base_url: document_list[i].data.rows[0].value
                    ._links.private_url.href || '',
                  index: i
                });
              }
            }
          }
          status_url = "#page=status_list&search=" + gadget.state.opml.title
            + "&reset_filter=1";
          parameter_content = parameters_widget_template({
            parameter_list: parameter_list
          });
          instance_content = instance_widget_template({
            instance_list: instance_list,
            status_list_url: status_url
          });

          gadget.element.querySelector('.hosting-block .instances-parameters')
            .innerHTML = parameter_content;
          gadget.element.querySelector('.hosting-block .instances-status')
            .innerHTML = instance_content;
          return gadget.changeState({instance_list: instance_list});
        })
        .push(function () {
          return gadget.state.render_deferred.resolve();
        })
        .push(function () {
          $(".hosting-block .signal").addClass("ui-content-hidden");
          return $(gadget.element.querySelectorAll('.hosting-block .ui-listview-outer')).listview().listview("refresh");
        });
    })

    .declareService(function () {
      var gadget = this;

      function bindOnClick(element) {
        var fieldset = $(element.parentNode.querySelector('.ui-collapse-content')),
            line = $(element);
        if (line.hasClass('ui-icon-plus')) {
          line.removeClass('ui-icon-plus');
          line.addClass('ui-icon-minus');
        } else {
          line.removeClass('ui-icon-minus');
          line.addClass('ui-icon-plus');
        }
        if (fieldset !== undefined) {
          fieldset.toggleClass('ui-content-hidden');
        }
        return false;
      }

      function updateParameterBox(parameter_list, title) {
        var element = gadget.element.querySelector('table[title="' + title + '"]'),
        tmp,
          i;
    
        if (!element) {
          return;
        }
        for (i = 0; i < parameter_list.length; i += 1) {
          if (!parameter_list[i].key) {
            continue;
          }
          element.querySelector('.v-' + parameter_list[i].key).textContent = parameter_list[i].value;
        }
      }

      function editMonitorProps (element) {
        var index = parseInt($(element).attr('rel'), 10),
          promise_list = [];
    
        if (isNaN(index) || gadget.state.instance_list.length < index) {
          return;
        }
        
        return new RSVP.Queue()
          .push(function () {
            if (gadget.props.config_gadget) {
              return gadget.dropGadget('config_gadget');
            }
            return false;
          })
          .push(function () {
            gadget.props.config_gadget = null;
            return gadget.declareGadget("gadget_monitoring_document_edit.html",
              {
                element: gadget.element,
                scope: 'config_gadget',
                sandbox: "public"
              }
            );
          })
          .push(function (config_gadget) {
            gadget.props.config_gadget = config_gadget;
            return gadget.props.config_gadget.popupEdit({
              url: gadget.state.instance_list._links.private_url.href,
              parameters: gadget.state.instance_list[index].parameters,
              title: gadget.state.instance_list[index].title,
              root_title: gadget.state.instance_list[index]['hosting-title'],
              page_options: gadget.props.options,
              path: 'config',
              key: 'config.tmp'
            }, function (data) {
              var update_promise = [],
                i,
                monitor_user = '',
                monitor_password = '';
    
              // Try to save monitor credential if they are pres
              for (i = 0; i < data.length; i += 1) {
                if (data[i].key === 'monitor-password') {
                  monitor_password = data[i].value;
                }
                if ((data[i].key || data[i].title) === 'monitor-user') {
                  monitor_user = data[i].value;
                }
              }
              gadget.state.instance_list[index].parameters = data;
              updateParameterBox(data, gadget.props.document_list[index].title);
              $(gadget.element.querySelector('.alert-info'))
                .removeClass('ui-content-hidden');
              return RSVP.all(update_promise);
            });
          });
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.state.render_deferred.promise;
        })
        .push(function () {
          var promise_list = [],
            element_list = gadget.element.querySelectorAll('.hosting-block .ui-listview-container li > a'),
            edit_list = gadget.element.querySelectorAll('.hosting-block .prop-edit'),
            i;
          for (i = 0; i < element_list.length; i += 1) {
            promise_list.push(loopEventListener(
              element_list[i],
              'click',
              false,
              bindOnClick.bind(gadget, element_list[i])
            ));
          }
          for (i = 0; i < edit_list.length; i += 1) {
            promise_list.push(loopEventListener(
              edit_list[i],
              'click',
              false,
              editMonitorProps.bind(gadget, edit_list[i])
            ));
          }
          return RSVP.all(promise_list);
        });
    });

}(window, rJS, btoa, Handlebars, $, Rusha));