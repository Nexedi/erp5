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
  function clearResults(my_gadget, my_override_tag) {
    var props = my_gadget.property_dict;

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
            props.plane.href = "#";
            props.plane.className += " ui-disabled";
          } else {
            my_parent.removeChild(child);
          }
        }
      }
    }

    // always clear autocomplete results (UL), the create new record input (DIV)
    // will only be removed on new searches, while the plane (A) is disabled
    dump(props.wrapper, "UL");
    dump(props.wrapper, my_override_tag || "DIV");
    dump(my_gadget.element, my_override_tag || "A");
  }

  // creates a tag indicating the value entered will be added as new object
  // of displayed type when the form is submitted. Clicking the tag will
  // reset the field, because otherwise accidentially typing something always
  // requires to reselect and manually backspace the value. Click to reset is
  // much easier/faster
  function createNewTag(my_gadget) {
    var props = my_gadget.property_dict,
      field_json = props.field_json,
      tag,
      group,
      controls,
      subfield,
      info,
      link,
      default_subfield;

    // unique values only... changes ERP5 ["foo", "foo"] to ["foo"] to "foo"
    info = field_json.portal_types.filter(function (item, pos, self) {
      return self.indexOf(item) === pos;
    }).join("");

    link = document.createElement("a");
    link.setAttribute("href", "#");
    link.className = "ui-first-child ui-last-child ui-btn ui-corner-all " +
      "ui-btn-inherit ui-btn-active ui-btn-icon-right ui-icon-delete";
    link.textContent = "Create: " + info;

    subfield = document.createElement("input");
    subfield.setAttribute("type", "hidden");
    subfield.setAttribute("name", field_json.relation_field_id);
    subfield.setAttribute("value", "_newContent_" + info);

    default_subfield = document.createElement("input");
    default_subfield.setAttribute("type", "hidden");
    default_subfield.setAttribute(
      "name",
      "default_subfield_" + field_json.key + "_relation:int"
    );
    default_subfield.setAttribute("value", 0);

    controls = document.createElement("div");
    controls.className = "ui-controlgroup-controls";
    controls.appendChild(link);
    controls.appendChild(subfield);
    controls.appendChild(default_subfield);

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

  // set the link to jump to
  function setRelationJump(my_gadget, my_initial_call, my_selected_value) {
    var props = my_gadget.property_dict,
      field_json = props.field_json,
      target_url = false,
      is_init = my_initial_call === true;

    if (my_selected_value) {
      target_url = my_selected_value;
    } else {
      if (field_json.relation_item_relative_url) {
        target_url = field_json.relation_item_relative_url[0];
      }
    }
    if (target_url && field_json.allow_jump) {
      return new RSVP.Queue()
        .push(function () {
          return my_gadget.getUrlFor({
            command: 'index',
            options: {
              jio_key: target_url,
              query: 'relative_url:"' + target_url + '"'
            }
          });
        })
        .push(function (my_url) {
          var plane = props.plane;
          plane.href = my_url;
          plane.className = "ui-btn ui-corner-all ui-btn-icon-notext " +
            "ui-icon-plane ui-shadow-inset ui-btn-inline";
          if (is_init === false) {
            return notifyChange(my_gadget);
          }
        });
    }
  }

  // trigger autocomplete for field value, on render() with value only sets link
  function triggerAutocomplete(my_gadget, my_value) {
    var props = my_gadget.property_dict,
      field_json = props.field_json,
      index = field_json.catalog_index,
      begin_from = props.begin_from || 0,
      lines = field_json.lines || 11,
      select_list = [index, "uid"],
      query_string = " AND (" + index + ':"' + my_value + '")',
      result_dict,
      no_results;

    delete props.selected_uid;

    return new RSVP.Queue()
      .push(function () {

        // new search, clear all, show spinner. set last_value to catch dups
        clearResults(my_gadget);
        props.last_value = my_value;
        props.spinner.className = "ui-btn ui-corner-all ui-btn-icon-notext" +
          " ui-input-clear ui-icon-spinner ui-icon-spin";

        return my_gadget.jio_allDocs({
          "query": new URI(field_json.query).query(true).query + query_string,
          "limit": [begin_from, begin_from + lines],
          "select_list": select_list
        });
      }).push(function (my_result) {
        result_dict = my_result.data;
        props.spinner.className = "ui-hidden-accessible";
        no_results = result_dict.total_rows === 0;

        // show "new" tag, clicking it will remove it and reset the field!
        // XXX Not active - reset should be handled by a generic reset method!
        if (no_results && field_json.allow_creation) {
          return new RSVP.Queue()
            .push(function () {
              props.wrapper.appendChild(createNewTag(my_gadget));
              my_gadget.property_dict.valid = true;
              return notifyChange(my_gadget);
            })
            .push(function () {
              var tag = props.wrapper.querySelector(".ui-tag-list .ui-btn");
              return RSVP.any([
                promiseEventListener(tag, "click", true),
                promiseEventListener(tag, "tap", true)
              ]);
            })
            .push(function (my_event_to_clear) {
              var wrapper,
                tag_list,
                original_value;

              my_event_to_clear.preventDefault();
              original_value = field_json.value || field_json.default || "";
              wrapper = props.wrapper;
              wrapper.querySelector("input").value = original_value;
              tag_list = wrapper.querySelector(".ui-tag-list");
              tag_list.parentNode.removeChild(tag_list);
              return setRelationJump(my_gadget, undefined);
            });
        }
        // default autocomplete
        return new RSVP.Queue()
          .push(function () {
            var list;

            if (no_results === false) {
              props.wrapper.appendChild(createResults(result_dict.rows, index));
              list = props.wrapper.querySelector("ul");

              return RSVP.any([
                promiseEventListener(list, "click", true),
                promiseEventListener(list, "touchend", true)
              ]);
            }
          });

      }).push(undefined, function (my_error) {
        if (my_error instanceof RSVP.CancellationError) {
          props.spinner.className = "ui-hidden-accessible";
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
          props.selected_uid = element.getAttribute("name");
          props.valid = true;
          props.wrapper.querySelector("input").value = element.textContent;
          clearResults(my_gadget, "skip");

          return setRelationJump(my_gadget, undefined, jump_url);
        }
      });
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (my_gadget) {
      my_gadget.property_dict = {};
    })

    .ready(function (my_gadget) {
      return my_gadget.getElement()
        .push(function (element) {
          my_gadget.element = element;
          my_gadget.property_dict.wrapper =
            element.querySelector("div.ui-input-text");
          my_gadget.property_dict.spinner = element.querySelector("a");
          my_gadget.property_dict.plane = element.querySelectorAll("a")[1];
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
      var field_gadget = this,
        input = field_gadget.element.querySelector('input'),
        field_json = options.field_json || {},
        value;

      if (field_json.relation_item_relative_url) {
        value = field_json.value || field_json.default;
      }
      // expose field_json and keep last value to prevent trigger on no-change
      field_gadget.property_dict.field_json = field_json;
      field_gadget.property_dict.last_value = value || "";
      field_gadget.property_dict.valid = true;

      input.setAttribute('value', value || "");
      input.setAttribute('name', field_json.key);
      input.setAttribute('title', field_json.title);

      if (field_json.required === 1) {
        input.setAttribute('required', 'required');
      }
      if (field_json.editable !== 1) {
        input.setAttribute('readonly', 'readonly');
        field_gadget.property_dict.wrapper.className += ' ui-state-readonly '
        // input.setAttribute('data-wrapper-class', 'ui-state-readonly');
        // input.setAttribute('disabled', 'disabled');
      }

      if (field_json.relation_item_relative_url) {
        return setRelationJump(field_gadget, true);
      }
    })

    // get content (needs hidden fields, too, when creating new records)
    .declareMethod('getContent', function () {
      var input_list = this.element.querySelectorAll('input'),
        result = {},
        i,
        i_len,
        input;

      for (i = 0, i_len = input_list.length; i < i_len; i += 1) {
        input = input_list[i];
        result[input.getAttribute('name')] = input.value;
      }

      // Always return the document UID if value has been modified
      if (this.property_dict.selected_uid !== undefined) {
        result[this.property_dict.field_json.relation_field_id] =
          this.property_dict.selected_uid;
      }
      return result;
    })
    .declareMethod('checkValidity', function () {
      var result;
      result = (this.element.querySelector('input').checkValidity()) &&
        (this.property_dict.valid);
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var field_gadget = this,
        props = field_gadget.property_dict,
        element = field_gadget.element.querySelector('input');

      // prevent unselecting on focus
      function stop(e) {
        e.preventDefault();
        return false;
      }

      // trigger autocomplete
      function handler(my_event) {
        var value = my_event.target.value,
          pending_promise;

        // field value unchanged (tab-bing)
        if (props.last_value === value) {
          return;
        }

        // empty value, do nothing but notify
        if (value === "") {
          field_gadget.property_dict.valid = true;
          return notifyChange(field_gadget);
        }

        field_gadget.property_dict.valid = false;

        // replace existing promise in case it has not triggered
        pending_promise = props.pending_promise;
        if (pending_promise) {
          pending_promise.cancel();
        }

        // create a new queue, expose it to replace it with trailing events
        pending_promise = new RSVP.Queue()
          .push(function () {
            return RSVP.delay(200);
          })
          .push(function () {
            return triggerAutocomplete(field_gadget, value);
          });

        field_gadget.property_dict.pending_promise = pending_promise;
        return pending_promise;
      }

      // Listen to all necessary events (blur not needed currently)
      return RSVP.all([
        loopEventListener(element, 'onmouseout', false, stop),
        loopEventListener(element, 'keyup', false, handler),
        loopEventListener(element, 'input', false, handler)
      ]);
    })

    .declareService(function () {
      var field_gadget = this;

      function notifyInvalid(evt) {
        return field_gadget.notifyInvalid(evt.target.validationMessage);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('input'),
        'invalid',
        false,
        notifyInvalid
      );
    });

}(window, document, rJS, RSVP, URI, loopEventListener, promiseEventListener));


/*
  Todos
  - OK trigger with delay on input/keyup
  - OK autocomplete makes portal catalog query instead of notifyloading
  - OK too many events triggering
  - OK 10 results shown, 
  - OK delete optionlist on focusout!
  - OK use icon in optionlist
  - OK user can pick one, whose value will be set to field
  - OK existing selected entry should allow to plane if option is set
  - OK loading with a preset value should query and activate plane if allowed
  - OK no hardcoded "title" use anywhere, make generic
  - OK remove plane on new search, don't make airport
  - OK add results info
  - OK non existing entry should allow to create new if option set
  - OK selecting from options clears taglist, too
  - OK update query
  - OK fix broken links
  - OK remove % from query syntax... ui downgrade, %% works, too
  - OK don't trigger on tab-through of existing and new values
  - OK don't autocomplete on empty string, clear values, too
  - OK loader and planes tabindex =-1
  - OK save custom entry
  - OK should not work when not in editable mode, seems ok now
  - OK fix CSS form spacing ---> not trivial
  - OK implement deactivated plane icon until set, never hide icon!
  - OK prevent multiple autocomplete elements when keyboard searching
  - OK either add some functionality to "create element" or delete on click
  - OK fix double trigger, multiple list
  - OK fix value settings should notifychange!
  - OK fix plane positioning in FF
  - OK fix CSS element theming
  - OK create button should rest when clicked in case user triggered to fast
  - OK fix double list because not clearing what previous chain appended to DOM
  - OK cleanup
  - OK fix textinput css, not generic enough
  - OK reimplement setting link without calling allDocs
  - on small displays JQM will toggle headers, find way to prevent!
  - fix broken promise chain
  - ok test
  - keyboard speed test
  - add generic text and translations
  - do multiRelationfield
  - find way to digest response of erp5? submit should clean input
  - add column_list parameter to pass more than title = "John Smith", render?
 
 
  
*/
