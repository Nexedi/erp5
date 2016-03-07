/*global window, document, rJS, RSVP, URI, loopEventListener,
promiseEventListener */
/*jslint indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, URI, loopEventListener,
  promiseEventListener) {
  "use strict";

  ////////////////////////////////////
  // Some methods
  ////////////////////////////////////

  // XXX: re-factor.
  // clear the autocomplete options, reset the plane tag and remove the create
  // new tag. Since plane and new tag sometimes need to stay, "override_tag"
  // can be set to something arbitrary to prevent removal of the respective
  // element.

  function clearResults(wrapper, my_override_tag) {
    function dump(my_parent, my_tag_name) {
      var child_list = my_parent.children,
        i,
        i_len,
        child;

      // XXX: now that link ("A") stays, rewrite the whole element clearing!
      for (i = 0, i_len = child_list.length; i < i_len; i += 1) {
        child = child_list[i];
        if (child && child.tagName === my_tag_name) {
          if (my_tag_name === "A") {
            child.className += " ui-disabled";
          } else {
            my_parent.removeChild(child);
          }
        }
      }
    }

    // always clear autocomplete results (UL), the create new record input (DIV)
    // will only be removed on new searches, while the plane (A) is disabled
    dump(wrapper, "UL");
    dump(wrapper, my_override_tag || "DIV");
    dump(wrapper.parentElement, my_override_tag || "A");
  }

  // creates a tag indicating the value entered will be added as new object
  // of displayed type when the form is submitted. Clicking the tag will
  // reset the field, because otherwise accidentially typing something always
  // requires to reselect and manually backspace the value. Click to reset is
  // much easier/faster
  function createNewTag(my_gadget, i) {
    var props = my_gadget.props,
      field_json = props.field_json,
      tag,
      group,
      controls,
      info,
      link;

    info = field_json.portal_types.filter(function (item, pos, self) {
      return self.indexOf(item) === pos;
    }).join("");

    link = document.createElement("a");
    link.setAttribute("href", "#");
    link.className = "ui-first-child ui-last-child ui-btn ui-corner-all " +
      "ui-btn-inherit ui-btn-active ui-btn-icon-right ui-icon-delete";
    link.textContent = "Create: " + info;
    my_gadget.props.select_uid_list[i] = "_newContent_" + info;

    controls = document.createElement("div");
    controls.className = "ui-controlgroup-controls";
    controls.appendChild(link);


    group = document.createElement("div");
    group.className = "ui-controlgroup ui-controlgroup-horizontal " +
      "ui-corner-all";
    group.appendChild(controls);

    tag = document.createElement("div");
    tag.className = "ui-tag-list ui-tag-list-inset";
    tag.appendChild(group);

    return tag;
  }

  // creates a set of autocomplete suggestings. Currently this is only a plain
  // list of elements. The list will display the number of results (>10 or 
  // exact). Clicking on an option will set this option as field value
  function createResults(my_result_list, index) {
    var list = document.createElement("ul"),
      head = document.createElement("li"),
      str = "ui-li-static ui-body-inherit ui-icon-mail-forward " +
        "ui-btn-icon-right",
      len = my_result_list.length,
      prefix = "",
      item,
      value_dict,
      result,
      i;

    if (len === 11) {
      prefix = ">";
      len = 10;
    }

    head.className = "ui-autocomplete ui-li ui-li-divider ui-bar-inherit";
    head.setAttribute("role", "heading");
    head.textContent = prefix + " " + len + " Result(s)";
    list.appendChild(head);

    for (i = 0; i < len; i += 1) {
      result = my_result_list[i];
      value_dict = result.value;
      item = document.createElement("li");
      item.className = str;

      // NOTE: gadget does not properties it gets here, so just concat
      // NOTE: if doing more complex UI, beware the textContent value won't
      // work, because currently it's used to retrieve the link from
      // the last autocomplete query results!
      item.textContent = value_dict[index];
      item.setAttribute("data-relative-url", result.id);
      item.setAttribute("name", value_dict.uid);
      list.appendChild(item);
    }

    list.className = "ui-listview ui-corner-all";
    list.firstChild.className += " ui-first-child";
    list.lastChild.className += " ui-last-child";

    return list;
  }

  ////////////////////////////////////
  // Promise methods
  ////////////////////////////////////

  // notify change of field value, done here, since called from multiple sources
  function notifyChange(my_gadget) {
    return RSVP.all([
      my_gadget.checkValidity(),
      my_gadget.notifyChange()
    ]);
  }




  function createSingleRelationField(gadget, i, allow_jump) {
    var div_input = document.createElement("div"),
      wrapper = document.createElement("div"),
      fieldset = document.createElement("fieldset"),
      a1 = document.createElement("a"),
      a2 = document.createElement("a"),
      field_json = gadget.props.field_json,
      value = field_json.value || field_json.default,
      input = document.createElement("input");
    //create element
    wrapper.setAttribute("class", "sub" + field_json.key + "_" + i);
    div_input.setAttribute("class", "ui-input-text ui-body-inherit ui-corner-all ui-shadow-inset ui-input-has-clear ui-input-has-icon");
    input.setAttribute("type", "text");
    input.setAttribute("autocomplete", "off");
    input.setAttribute("data-enhanced", "true");
    a1.setAttribute("herf", "#");
    a1.setAttribute("tabindex", "-1");
    a1.setAttribute("class", "ui-hidden-accessible");
    a1.innerText = "&nbsp;";

    a2.setAttribute("herf", "#");
    a2.setAttribute("tabindex", "-1");
    a2.setAttribute("class", "ui-btn ui-corner-all ui-btn-icon-notext ui-icon-plane ui-shadow-inset ui-btn-inline ui-disabled");
    a2.innerText = "Jump to this document";

    div_input.appendChild(input);
    div_input.appendChild(a1);
    wrapper.appendChild(div_input);
    wrapper.appendChild(a2);
    fieldset.appendChild(wrapper);
    gadget.props.element.querySelector(".div_field").appendChild(fieldset);

    //initialize
    input.setAttribute('value', value[i] || "");
    input.setAttribute('name', "sub" + field_json.key + "_" + i);
    if (field_json.editable !== 1) {
      input.setAttribute('readonly', 'readonly');
      div_input.className += ' ui-state-readonly ';
    }
    if (field_json.allow_jump && allow_jump) {
      return new RSVP.Queue()
        .push(function () {
          return gadget.getUrlFor({
            command: 'index',
            options: {
              jio_key: field_json.relation_item_relative_url[i]
            }
          });
        })
        .push(function (my_url) {
          a2.href = my_url;
          a2.className = "ui-btn ui-corner-all ui-btn-icon-notext " +
            "ui-icon-plane ui-shadow-inset ui-btn-inline";
        });
    }
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (my_gadget) {
      return my_gadget.getElement()
        .push(function (element) {
          my_gadget.props = {};
          my_gadget.props.pending_promise_list = [];
          my_gadget.props.select_uid_list = [];
          my_gadget.props.element = element;
        });
    })
    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        i,
        url_list = options.field_json.relation_item_relative_url,
        value_list = options.field_json.value || options.field_json.default;
      gadget.props.field_json = options.field_json || {};
      for (i = 0; i < value_list.length && url_list !== undefined && url_list[i] !== undefined; i += 1) {
        gadget.props.select_uid_list[i] = options.field_json.relation_item_uid[i];
        createSingleRelationField(gadget, i, true);
      }
      if (options.field_json.editable === 1) {
        createSingleRelationField(gadget, i, false);
        gadget.props.relation_field_number = i;
      }
    })
    // get content (needs hidden fields, too, when creating new records)
    .declareMethod('checkValidity', function () {
      return true;
    })
    .declareMethod('getContent', function () {
      var field_json = this.props.field_json,
        input_list = this.props.element.querySelectorAll('input'),
        result = {},
        i,
        value = "",
        i_len,
        input;

      for (i = 0, i_len = input_list.length; i < i_len; i += 1) {
        input = input_list[i];
        if (input.value !== "") {
          value = value + input.value + "\n";
          result[this.props.field_json.relation_field_id + "_" + i] = this.props.select_uid_list[i];
        }
      }
      result[field_json.key] = value;
      return result;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        i,
        index_list,
        createEmptyField,
        triggerAutocomplete,
        stop,
        handler,
        element_list = gadget.props.element.querySelectorAll('input');

       // trigger autocomplete for field value, on render() with value only sets link
      triggerAutocomplete = function (my_gadget, my_event, i) {
        var props = my_gadget.props,
          field_json = props.field_json,
          index = field_json.catalog_index,
          begin_from = props.begin_from || 0,
          lines = field_json.lines || 11,
          select_list = [index, "uid"],
          query_string = " AND (" + index + ':"' + my_event.target.value + '")',
          result_dict,
          tag_list,
          spin,
          target_div = my_gadget.props.element.querySelector("." + my_event.target.name),
          wrapper = target_div.querySelector("div.ui-input-text"),
          no_results;

        spin = target_div.querySelector(".ui-hidden-accessible");
        return new RSVP.Queue()
          .push(function () {
            clearResults(wrapper);
            spin.className = "ui-btn ui-corner-all ui-btn-icon-notext" +
              " ui-input-clear ui-icon-spinner ui-icon-spin";
            return my_gadget.jio_allDocs({
              "query": new URI(field_json.query).query(true).query + query_string,
              "limit": [begin_from, begin_from + lines],
              "select_list": select_list
            });
          }).push(function (my_result) {
            result_dict = my_result.data;
            spin.className = "ui-hidden-accessible";
            no_results = result_dict.total_rows === 0;

            // show "new" tag, clicking it will remove it and reset the field!
            // XXX Not active - reset should be handled by a generic reset method!
            if (no_results && field_json.allow_creation) {
              return new RSVP.Queue()
                .push(function () {
                  wrapper.appendChild(createNewTag(my_gadget, i));
                  return notifyChange(my_gadget);
                })
                .push(function () {
                  var tag = wrapper.querySelector(".ui-tag-list .ui-btn");
                  if (i === gadget.props.relation_field_number) {
                    createEmptyField();
                  }
                  return RSVP.any([
                    promiseEventListener(tag, "click", true),
                    promiseEventListener(tag, "tap", true)
                  ]);
                })
                .push(function (my_event_to_clear) {
                  my_event_to_clear.preventDefault();
                  wrapper.querySelector("input").value = my_event.target.defaultValue;
                  tag_list = wrapper.querySelector(".ui-tag-list");
                  tag_list.parentNode.removeChild(tag_list);
                  if (my_event.target.defaultValue !== "") {
                    wrapper.parentElement.lastChild.className = "ui-btn ui-corner-all ui-btn-icon-notext " +
                      "ui-icon-plane ui-shadow-inset ui-btn-inline";
                  }
                });
            }
            // have element
            return new RSVP.Queue()
              .push(function () {
                var list;

                if (no_results === false) {
                  wrapper.appendChild(createResults(result_dict.rows, index));
                  list = wrapper.querySelector("ul");

                  return RSVP.any([
                    promiseEventListener(list, "click", true),
                    promiseEventListener(list, "touchend", true)
                  ]);
                }
              });

          }).push(undefined, function (my_error) {
            if (my_error instanceof RSVP.CancellationError) {
              spin.className = "ui-hidden-accessible";
              clearResults(my_gadget, "skip");
            }
            throw my_error;
          }).push(function (my_selection_event) {
            var element,
              jump_url;

            // take entered text, set to input and clear list options
            if (my_selection_event && my_selection_event.target) {
              element = my_selection_event.target;
              jump_url = element.getAttribute("data-relative-url");
              props.select_uid_list[i] = element.getAttribute("name");
              wrapper.querySelector("input").value = element.textContent;
              clearResults(wrapper, "skip");
              return my_gadget.getUrlFor({
                command: 'index',
                options: {
                  jio_key: jump_url
                }
              });
            }
          }).push(function (my_url) {
            if (my_url !== undefined) {
              wrapper.parentElement.lastChild.href = my_url;
              wrapper.parentElement.lastChild.className = "ui-btn ui-corner-all ui-btn-icon-notext " +
                "ui-icon-plane ui-shadow-inset ui-btn-inline";
              if (i === gadget.props.relation_field_number) {
                createEmptyField();
              }
            }
          });
      };

      stop = function (e) {
        e.preventDefault();
        return false;
      };

      handler = function (my_event) {
        var value = my_event.target.value,
          pending_promise;

        // field value unchanged (tab-bing)
        if (my_event.target.defaultValue === value) {
          return;
        }

        // empty value, do nothing but notify
        if (value === "") {
          return notifyChange(gadget);
        }
        index_list = my_event.target.name.split("_");
        i = parseInt(index_list[index_list.length - 1], 10);
        // replace existing promise in case it has not triggered
        pending_promise = gadget.props.pending_promise_list[i];
        if (pending_promise) {
          pending_promise.cancel();
        }

        // create a new queue, expose it to replace it with trailing events
        pending_promise = new RSVP.Queue()
          .push(function () {
            return RSVP.delay(200);
          })
          .push(function () {
            return triggerAutocomplete(gadget, my_event, i);
          });

        gadget.props.pending_promise_list[i] = pending_promise;
        return pending_promise;
      };

      createEmptyField = function () {
        var new_input;
        gadget.props.relation_field_number += 1;
        createSingleRelationField(gadget, gadget.props.relation_field_number, false);
        element_list = gadget.props.element.querySelectorAll('input');
        new_input = element_list[element_list.length - 1];
        loopEventListener(new_input, 'onmouseout', false, stop);
        loopEventListener(new_input, 'keyup', false, handler);
        loopEventListener(new_input, 'input', false, handler);
      };

      // Listen to all necessary events (blur not needed currently)
      for (i = 0; i < element_list.length; i += 1) {
        loopEventListener(element_list[i], 'onmouseout', false, stop);
        loopEventListener(element_list[i], 'keyup', false, handler);
        loopEventListener(element_list[i], 'input', false, handler);
      }
    });
}(window, document, rJS, RSVP, URI, loopEventListener, promiseEventListener));