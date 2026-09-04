/*global window, document, fetch, URLSearchParams, Interpreter */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document) {
  "use strict";

  var CANVAS_NOTE = "Canvas origin (0,0) is top-left, x grows right, y grows down.",
    CANVAS_ID = "drawing-canvas",
    EXECUTE_JAVASCRIPT_MAX_STEPS = 1000000;

  function getCanvasContext(element) {
    var canvas = element.querySelector("#" + CANVAS_ID);
    if (!canvas) {
      canvas = document.createElement("canvas");
      canvas.id = CANVAS_ID;
      canvas.width = 500;
      canvas.height = 400;
      element.appendChild(canvas);
    }
    return canvas.getContext("2d");
  }

  function appendParam(usp, key, value) {
    var i;
    if (Array.isArray(value)) {
      // ERP5Document_getHateoas expects repeated keys for multi-valued
      // params (e.g. several select_list=<field> entries), not one
      // JSON-encoded value.
      for (i = 0; i < value.length; i += 1) {
        appendParam(usp, key, value[i]);
      }
      return;
    }
    usp.append(key, typeof value === "string" ? value : JSON.stringify(value));
  }

  function withQuery(url, query) {
    var usp, key;
    if (query && Object.keys(query).length) {
      usp = new URLSearchParams();
      for (key in query) {
        if (query.hasOwnProperty(key)) {
          appendParam(usp, key, query[key]);
        }
      }
      url += (url.indexOf("?") === -1 ? "?" : "&") + usp.toString();
    }
    return url;
  }

  // ---------------------------------------------------------------------
  // Shared ERP5 HATEOAS primitives - same URL-construction rule throughout:
  // the script name ("ERP5Document_getHateoas"/"Base_edit") is always
  // hardcoded here in code, never built by the model from a portal_type or
  // relative_url (that was the root cause of an earlier bug where the model
  // hallucinated e.g. "Organisation_getHateoas" when it had to build a path
  // itself). See erp5-mcp-hateoas's own _hateoas_url() for the same trick.
  // ---------------------------------------------------------------------

  var SKIP_VIEW_KEY = { _links: 1, _embedded: 1, _actions: 1, form_id: 1 };

  function scriptUrl(hateoas_url) {
    return hateoas_url.replace(/\/$/, "") + "/ERP5Document_getHateoas";
  }

  function webSiteBaseUrl(hateoas_url) {
    return hateoas_url.replace(/\/$/, "").replace(/\/[^\/]+$/, "");
  }

  function browserUrl(hateoas_url, relative_url) {
    return webSiteBaseUrl(hateoas_url) + "/#/" + relative_url;
  }

  function decodeHtmlEntitiesText(text) {
    var div = document.createElement("div");
    div.innerHTML = text;
    return div.textContent || div.innerText || "";
  }

  function stripHtml(text) {
    if (!text) { return ""; }
    var clean = String(text)
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<p[^>]*>/gi, "\n")
      .replace(/<\/p>/gi, "");
    clean = clean.replace(/<[^>]+>/g, "");
    clean = decodeHtmlEntitiesText(clean);
    clean = clean.replace(/[^\S\n]+/g, " ");
    return clean.trim();
  }

  function isListboxKey(key, view) {
    if (key === "listbox") { return true; }
    var def = view[key];
    return Boolean(def && typeof def === "object" && def.list_method_template);
  }

  // Catalog/listbox ROW extractor (flat {field: value}), used by erp5_search.
  function extractRow(item, hateoas_url) {
    var row = {}, key, val, self_href, relative_url;
    self_href = item._links && item._links.self && item._links.self.href;
    relative_url = self_href ? self_href.replace(/^urn:jio:get:/, "") : undefined;
    if (relative_url !== undefined) {
      row.relative_url = relative_url;
      row.url = browserUrl(hateoas_url, relative_url);
    }
    for (key in item) {
      if (item.hasOwnProperty(key) && key.charAt(0) !== "_" && key !== "listbox_uid:list") {
        val = item[key];
        if (val && typeof val === "object" && val.field_gadget_param) {
          row[key] = val.field_gadget_param["default"];
        } else if (typeof val === "string" && /<[a-z\/]/i.test(val)) {
          row[key] = stripHtml(val);
        } else {
          row[key] = val;
        }
      }
    }
    return row;
  }

  function isEmptyFieldValue(value) {
    var keys;
    if (value === null || value === undefined || value === "") { return true; }
    if (Array.isArray(value)) { return value.length === 0; }
    if (value && typeof value === "object") {
      if (value.hasOwnProperty("portal_types") && value.hasOwnProperty("urls")) {
        var v = value.value,
          vEmpty = Array.isArray(v) ? v.every(function (x) { return !x; }) : !v;
        return vEmpty && (!value.urls || value.urls.length === 0);
      }
      if (value.hasOwnProperty("matrix_data")) {
        return !value.matrix_data || value.matrix_data.length === 0;
      }
      keys = Object.keys(value);
      if (!keys.length) { return true; }
      if (keys.every(function (k) {
        return value[k] && typeof value[k] === "object" && value[k].hasOwnProperty("value");
      })) {
        return keys.every(function (k) { return isEmptyFieldValue(value[k].value); });
      }
      return false;
    }
    return false; // 0, 0.0, false are meaningful ERP5 values, not "empty"
  }

  // Document FIELD extractor ({field: {title, value, editable, type}}),
  // used by erp5_read/erp5_write - distinct from extractRow (catalog rows).
  function extractFieldValue(fieldDef, includeChoices) {
    if (!fieldDef || typeof fieldDef !== "object") { return fieldDef; }
    if (fieldDef.field_gadget_param) { return fieldDef.field_gadget_param["default"]; }
    var type = fieldDef.type,
      items,
      subView,
      out,
      key;
    if (type === "RelationStringField" || type === "MultiRelationStringField") {
      return {
        value: fieldDef["default"],
        portal_types: fieldDef.portal_types || [],
        urls: fieldDef.relation_item_relative_url || []
      };
    }
    if (type === "ListField" || type === "ParallelListField") {
      if (!includeChoices) { return fieldDef["default"]; }
      items = fieldDef.items || [];
      return {
        value: fieldDef["default"],
        valid_choices: items.filter(function (item) { return item[1]; })
          .map(function (item) { return { label: item[0], value: item[1] }; })
      };
    }
    if (type === "MatrixBox") {
      return { matrix_data: fieldDef.data || [], template_field_dict: fieldDef.template_field_dict || {} };
    }
    if (type === "FormBox") {
      subView = fieldDef._embedded && fieldDef._embedded._view;
      if (!subView) { return { note: "FormBox with no embedded view" }; }
      out = {};
      for (key in subView) {
        if (subView.hasOwnProperty(key) && key.charAt(0) !== "_" && !subView[key].hidden) {
          out[key] = {
            title: subView[key].title || key,
            value: subView[key]["default"],
            editable: Boolean(subView[key].editable),
            type: subView[key].type || "unknown"
          };
        }
      }
      return out;
    }
    return fieldDef["default"];
  }

  function simplifyDocument(view, includeChoices) {
    var result = {}, key, fieldDef;
    for (key in view) {
      if (view.hasOwnProperty(key) && key.charAt(0) !== "_" && !SKIP_VIEW_KEY[key] && !isListboxKey(key, view)) {
        fieldDef = view[key];
        if (!fieldDef || typeof fieldDef !== "object") { continue; }
        result[key] = {
          title: fieldDef.title || key,
          value: extractFieldValue(fieldDef, includeChoices),
          editable: Boolean(fieldDef.editable),
          type: fieldDef.type || "unknown"
        };
      }
    }
    return result;
  }

  // Hide empty NON-editable fields (view-only noise - workflow metadata,
  // computed totals, etc), but always keep empty EDITABLE fields: those are
  // exactly the ones a caller most needs to see right after erp5_create,
  // e.g. a fresh document's still-unset Supplier/Resource relation - hiding
  // them here would make it impossible to even discover they exist to write to.
  function filterEmptyFields(fields) {
    var result = {}, key;
    for (key in fields) {
      if (fields.hasOwnProperty(key) && (fields[key].editable || !isEmptyFieldValue(fields[key].value))) {
        result[key] = fields[key];
      }
    }
    return result;
  }

  function filterEmptyRow(row) {
    var result = {}, key;
    for (key in row) {
      if (row.hasOwnProperty(key) && (key === "relative_url" || key === "url" || !isEmptyFieldValue(row[key]))) {
        result[key] = row[key];
      }
    }
    return result;
  }

  function normalizeLinkList(link) {
    if (!link) { return []; }
    var list = Array.isArray(link) ? link : [link];
    return list.map(function (item) { return { name: item.name, title: item.title || item.name }; });
  }

  function extractListboxMeta(listbox) {
    if (!listbox || typeof listbox !== "object") { return null; }
    var template = listbox.list_method_template || "",
      form_relative_url = "",
      match = /[?&]form_relative_url=([^&]*)/.exec(template),
      meta;
    if (match) {
      try { form_relative_url = decodeURIComponent(match[1]); } catch (ignore) { form_relative_url = match[1]; }
    }
    meta = {
      title: listbox.title || "",
      columns: listbox.column_list || [],
      portal_type: listbox.portal_type || [],
      default_sort: listbox.sort || []
    };
    if (form_relative_url) { meta.form_relative_url = form_relative_url; }
    return meta;
  }

  function extractAllListboxesMeta(view) {
    var result = {}, key, found = false;
    for (key in view) {
      if (view.hasOwnProperty(key) && isListboxKey(key, view)) {
        result[key] = extractListboxMeta(view[key]);
        found = true;
      }
    }
    return found ? result : null;
  }

  function handleApiError(err, response, bodyText) {
    var status = response ? response.status : null;
    if (status === 401) {
      return "Error: Authentication failed (HTTP 401). Your session may have expired - try reloading the page.";
    }
    if (status === 403) {
      return "Error: Permission denied (HTTP 403). The current user does not have access to this resource.";
    }
    if (status === 404) {
      return "Error: Resource not found (HTTP 404). The relative_url may be incorrect - use erp5_search to find valid document paths.";
    }
    if (status) {
      return "Error: HTTP " + status + " - " + String(bodyText || "").slice(0, 300);
    }
    return "Error: " + (err ? (err.message || String(err)) : "unknown error");
  }

  function errorMessage(err) {
    if (err && err.httpError) { return handleApiError(null, err.response, err.text); }
    return handleApiError(err, null, null);
  }

  function catchApiError(promise) {
    return promise.then(null, function (err) { return errorMessage(err); });
  }

  function getJSON(url) {
    return fetch(url, { credentials: "same-origin", method: "GET" }).then(function (response) {
      return response.text().then(function (text) {
        var err;
        if (!response.ok) {
          err = new Error("HTTP " + response.status);
          err.httpError = true;
          err.response = response;
          err.text = text;
          throw err;
        }
        try {
          return JSON.parse(text);
        } catch (parseErr) {
          err = new Error("Could not parse server response as JSON");
          err.httpError = true;
          err.response = response;
          err.text = text;
          throw err;
        }
      });
    });
  }

  // ERP5 form fields are very often prefixed ("my_title", "your_email", ...)
  // - real_key is the JSON view key (e.g. "my_title"); this returns the
  // unprefixed guess an LLM is likely to make instead ("title"), so a wrong
  // guess like field_values={"field_title": ...} still lands on the right
  // field instead of being silently dropped (see Base_edit.py: it only
  // applies a field whose raw id already starts with "my_").
  function stripFieldPrefix(real_key) {
    return real_key.replace(/^(my_|your_|default_)/, "");
  }

  var RELATION_FIELD_TYPE = { RelationStringField: 1, MultiRelationStringField: 1 };

  // RelationStringField/MultiRelationStringField (e.g. a Purchase Order's
  // Supplier, or an Order Line's Resource/"Product or Service") store a
  // human-readable title as their submitted value, but ERP5 actually keys
  // the relation off a companion hidden UID field (field_def.relation_field_id).
  // Submitting only the title with no UID leaves the relation unset. This
  // mirrors erp5-mcp-hateoas's _resolve_relation_uid: search the catalog for
  // a document of one of the field's allowed portal_types whose
  // catalog_index matches the given title, and reuse the field's current UID
  // if the value is unchanged. See ERP5Document_getHateoas.py's
  // RelationStringField branch for where catalog_index/portal_types/
  // relation_field_id/relation_item_uid come from.
  function resolveRelationUid(hateoas_url, field_def, new_value) {
    var current_default = field_def["default"],
      current_value = Array.isArray(current_default) ? current_default[0] : current_default,
      current_uid_list = field_def.relation_item_uid || [],
      portal_types = field_def.portal_types || [],
      catalog_index = field_def.catalog_index,
      portal_type_filter,
      query,
      search_url;
    if (new_value === current_value && current_uid_list.length) {
      return Promise.resolve(String(current_uid_list[0]));
    }
    if (!portal_types.length || !catalog_index) {
      return Promise.resolve(null);
    }
    portal_type_filter = "(" + portal_types.map(function (pt) {
      return "portal_type:\"" + pt + "\"";
    }).join(" OR ") + ")";
    query = portal_type_filter + " AND " + catalog_index + ":\"" + new_value + "\"";
    search_url = withQuery(scriptUrl(hateoas_url), {
      mode: "search",
      query: query,
      select_list: ["uid", catalog_index],
      limit: [0, 10]
    });
    return getJSON(search_url).then(function (data) {
      var contents = (data._embedded && data._embedded.contents) || [],
        exact_match = contents.filter(function (item) { return item[catalog_index] === new_value; })[0],
        item = exact_match || contents[0];
      return item && item.uid !== undefined && item.uid !== null ? String(item.uid) : null;
    }, function () { return null; });
  }

  // Shared by erp5_write: fetches the document's current field defaults
  // first, then submits the WHOLE form with field_values overlaid on top.
  // ERP5's Base_edit requires every field submitted together, not just the
  // changed ones, or the edit is silently ignored/partial.
  function writeFields(hateoas_url, relative_url, view_name, field_values) {
    return getJSON(withQuery(scriptUrl(hateoas_url), {
      mode: "traverse",
      relative_url: relative_url,
      view: view_name || "view"
    })).then(function (data) {
      var view = (data._embedded && data._embedded._view) || {},
        match_by_key = {},
        remaining_field_values = {},
        unmatched_key_list,
        unresolved_relation_list = [],
        relation_uid_promise_list = [],
        key,
        field_def,
        form_key,
        alias_key;
      for (key in field_values) {
        if (field_values.hasOwnProperty(key)) { remaining_field_values[key] = true; }
      }
      // Pass 1: match each field_values entry to its real field (with prefix
      // fallback), without submitting anything yet - relation fields need an
      // async UID lookup before the form can be built.
      for (key in view) {
        if (view.hasOwnProperty(key) && key.charAt(0) !== "_" && !SKIP_VIEW_KEY[key]) {
          field_def = view[key];
          if (!field_def || typeof field_def !== "object" || field_def.hidden === 1) { continue; }
          form_key = "field_" + key;
          alias_key = "field_" + stripFieldPrefix(key);
          if (field_values.hasOwnProperty(form_key)) {
            match_by_key[key] = { field_def: field_def, value: field_values[form_key] };
            delete remaining_field_values[form_key];
          } else if (alias_key !== form_key && field_values.hasOwnProperty(alias_key)) {
            // Tolerate a common wrong guess, e.g. field_values={"field_title": ...}
            // when the real ERP5 field id is prefixed ("my_title").
            match_by_key[key] = { field_def: field_def, value: field_values[alias_key] };
            delete remaining_field_values[alias_key];
          }
        }
      }
      unmatched_key_list = Object.keys(remaining_field_values);
      if (unmatched_key_list.length) {
        throw new Error(
          "write failed: field_values key(s) " + unmatched_key_list.join(", ") +
            " do not match any field on this document/view - call erp5_read first and use its exact " +
            "field ids (they are often prefixed, e.g. \"my_title\" rather than \"title\")."
        );
      }
      for (key in match_by_key) {
        if (match_by_key.hasOwnProperty(key) && RELATION_FIELD_TYPE[match_by_key[key].field_def.type]) {
          relation_uid_promise_list.push(
            resolveRelationUid(hateoas_url, match_by_key[key].field_def, match_by_key[key].value)
              .then(function (matched_key, uid) {
                if (uid) {
                  match_by_key[matched_key].uid = uid;
                } else {
                  unresolved_relation_list.push(matched_key);
                }
              }.bind(null, key))
          );
        }
      }
      return Promise.all(relation_uid_promise_list).then(function () {
        var form_data = new URLSearchParams(),
          edit_url = hateoas_url.replace(/\/$/, "") + "/" + String(relative_url).replace(/^\//, "") + "/Base_edit",
          applied_field_list = [],
          match,
          value;
        for (key in view) {
          if (view.hasOwnProperty(key) && key.charAt(0) !== "_" && !SKIP_VIEW_KEY[key]) {
            field_def = view[key];
            if (!field_def || typeof field_def !== "object") { continue; }
            if (field_def.hidden === 1) {
              appendParam(form_data, field_def.key || key, field_def["default"] || "");
            } else {
              form_key = "field_" + key;
              match = match_by_key[key];
              value = match ? match.value : field_def["default"];
              appendParam(form_data, form_key, value === undefined || value === null ? "" : value);
              if (match) {
                applied_field_list.push(form_key);
                if (RELATION_FIELD_TYPE[field_def.type] && field_def.relation_field_id) {
                  // Companion hidden UID field - this is what ERP5 actually
                  // uses to resolve the relation; the title text above is
                  // only for display.
                  appendParam(form_data, field_def.relation_field_id, match.uid || (field_def.relation_item_uid || [])[0] || "");
                }
              }
            }
          }
        }
        if (view.form_id && typeof view.form_id === "object") {
          appendParam(form_data, "form_id", view.form_id["default"] || "");
        }
        return fetch(edit_url, { credentials: "same-origin", method: "POST", body: form_data })
          .then(function (response) {
            return response.text().then(function (text) {
              var data2 = null, err;
              try { data2 = JSON.parse(text); } catch (ignore) { data2 = null; }
              if (data2 && data2.portal_status_message && !response.ok) {
                throw new Error("write failed: " + data2.portal_status_message);
              }
              if (data2 && data2._notification && data2._notification.status === "error") {
                throw new Error("write failed: " + data2._notification.message);
              }
              if (!response.ok) {
                err = new Error("HTTP " + response.status);
                err.httpError = true;
                err.response = response;
                err.text = text;
                throw err;
              }
              return {
                relative_url: relative_url,
                fields_set: applied_field_list,
                unresolved_relations: unresolved_relation_list.length ? unresolved_relation_list : undefined
              };
            });
          });
      });
    });
  }

  function createSearchTool(hateoas_url) {
    var script_url = scriptUrl(hateoas_url);
    return {
      definition: {
        name: "erp5_search",
        description: "Search for ERP5 documents via the portal_catalog, of ANY portal_type (Person, " +
          "Organisation, Product, Purchase Order, or anything else this ERP5 has). USE THIS WHEN: you " +
          "want to find specific documents by title, reference, portal_type, state, etc, or you need to " +
          "discover a module's real id before erp5_read/erp5_write on a document inside it (search " +
          "query=\"module_id:%\" with no relative_url lists every real module id in this ERP5 - never " +
          "guess a module id from a portal_type name, e.g. assuming \"Product\" lives in " +
          "\"product_module\": the \"<type>_module\" pattern is common but has real exceptions). DO NOT " +
          "USE THIS WHEN: you already have a document's relative_url (use erp5_read directly).",
        parameters: {
          type: "object",
          properties: {
            relative_url: {
              type: "string",
              description: "Module id to search in, e.g. \"person_module\", \"sale_order_module\". Omit to search the whole catalog unscoped (e.g. for the module_id:% discovery trick)."
            },
            query: {
              type: "string",
              description: "ERP5 catalog query (not SQL LIKE). Text: '\"South\" AND \"Africa\"'. Field filter: 'simulation_state:\"draft\"'. Portal type: 'portal_type:\"Person\"'. Combine with AND/OR. Use \"title\"/\"reference\" for text matching - never invent a field name like \"name\", it silently matches nothing instead of erroring."
            },
            select_list: {
              type: "array",
              items: { type: "string" },
              description: "Columns to return, e.g. [\"title\",\"reference\",\"simulation_state\"]. Defaults to title/reference if omitted."
            },
            sort_on: {
              type: "string",
              description: "JSON-encoded sort spec, e.g. '[[\"creation_date\",\"descending\"]]'."
            },
            limit: {
              type: "number",
              description: "Max results, default 20."
            }
          }
        }
      },
      execute: function (args) {
        var query_dict = {
          mode: "search",
          query: args.query || "",
          limit: [0, args.limit || 20]
        };
        if (args.relative_url) { query_dict.relative_url = args.relative_url; }
        if (args.select_list) { query_dict.select_list = args.select_list; }
        if (args.sort_on) { query_dict.sort_on = args.sort_on; }
        return catchApiError(
          getJSON(withQuery(script_url, query_dict)).then(function (data) {
            var embedded = data._embedded || {},
              contents = embedded.contents || [];
            return {
              total_count: embedded.count || contents.length,
              returned_count: contents.length,
              items: contents.map(function (item) { return filterEmptyRow(extractRow(item, hateoas_url)); })
            };
          })
        );
      }
    };
  }

  function createReadTool(hateoas_url) {
    var script_url = scriptUrl(hateoas_url);
    return {
      definition: {
        name: "erp5_read",
        description: "Read one ERP5 document of ANY portal_type: fields, workflows, actions, views, " +
          "listbox metadata. USE THIS WHEN: you need full details of one document; to check editable " +
          "fields before erp5_write; or to discover workflow/action names. DO NOT USE THIS WHEN: you " +
          "don't have a relative_url yet (use erp5_search first).",
        parameters: {
          type: "object",
          properties: {
            relative_url: { type: "string", description: "The document's relative_url." },
            view: { type: "string", description: "View/form to read, default \"view\"." }
          },
          required: ["relative_url"]
        }
      },
      execute: function (args) {
        var view_name = args.view || "view";
        return catchApiError(
          getJSON(withQuery(script_url, { mode: "traverse", relative_url: args.relative_url, view: view_name }))
            .then(function (data) {
              var links = data._links || {},
                view = (data._embedded && data._embedded._view) || {},
                resolved_url = (links.traversed_document && links.traversed_document.name) || args.relative_url;
              return {
                title: data.title || "",
                portal_type: (links.type && links.type.name) || "",
                relative_url: resolved_url,
                url: browserUrl(hateoas_url, resolved_url),
                parent: (links.parent && links.parent.name) || "",
                fields: filterEmptyFields(simplifyDocument(view, false)),
                workflows: normalizeLinkList(links.action_workflow),
                actions: normalizeLinkList(links.action_object_jio_action),
                views: normalizeLinkList(links.action_object_view),
                exchanges: normalizeLinkList(links.action_object_jio_exchange),
                prints: normalizeLinkList(links.action_object_jio_print),
                all_listboxes: extractAllListboxesMeta(view),
                has_create_action: Boolean(links.action_object_new_content_action)
              };
            })
        );
      }
    };
  }

  function createWriteTool(hateoas_url) {
    return {
      definition: {
        name: "erp5_write",
        description: "Update field values on an EXISTING ERP5 document of ANY portal_type. Reads the " +
          "document's current field defaults first, overlays the field_values you give it, and submits " +
          "the complete form in one request - ERP5's edit endpoint requires the WHOLE form, not just " +
          "changed fields, or the edit silently drops everything else (this is exactly why a document " +
          "can otherwise come back with no title set after being created). USE THIS WHEN: you need to " +
          "update one or more fields on a document that already exists, including right after creating " +
          "one with erp5_create. DO NOT USE THIS WHEN: the document does not exist yet (use erp5_create - " +
          "pointing erp5_write at a MODULE will NOT create a new document inside it, it will only rename " +
          "the module itself, which is never what the user wants); or when you don't yet know the exact " +
          "field ids (call erp5_read first and copy its \"fields\" map keys VERBATIM - ERP5 field ids are " +
          "very often prefixed, e.g. \"my_title\" rather than \"title\", so \"my_title\" becomes " +
          "\"field_my_title\" here, NOT \"field_title\" - never strip or guess the prefix). If a key you " +
          "pass doesn't match any real field, the call fails with an error naming the bad key(s) rather " +
          "than silently doing nothing. RELATION FIELDS (erp5_read shows these with \"portal_types\"/" +
          "\"urls\" instead of a plain value, e.g. a Purchase Order's Supplier, or an Order Line's " +
          "Resource/\"Product or Service\"): just pass the target document's exact title as a plain " +
          "string, e.g. {\"field_my_source\": \"APZQR\"} - this tool looks it up in the catalog and links " +
          "it automatically. If the result's \"unresolved_relations\" lists that field, no document with " +
          "that exact title/reference was found (check spelling, or erp5_search for the exact title " +
          "first) and the relation was left unset.",
        parameters: {
          type: "object",
          properties: {
            relative_url: { type: "string", description: "The document's relative_url." },
            view: { type: "string", description: "The form/view to read current field defaults from, default \"view\"." },
            field_values: { type: "object", description: "Values to set, keyed by the exact field id from erp5_read prefixed with field_, e.g. {\"field_my_title\": \"SMAL\"} when erp5_read reported the field as \"my_title\". For relation fields, the value is the target document's title (not a UID) - it is resolved automatically." }
          },
          required: ["relative_url", "field_values"]
        }
      },
      execute: function (args) {
        return catchApiError(
          writeFields(hateoas_url, args.relative_url, args.view, args.field_values || {})
            .then(function (result) {
              return {
                status: "success",
                relative_url: result.relative_url,
                url: browserUrl(hateoas_url, result.relative_url),
                fields_updated: result.fields_set,
                unresolved_relations: result.unresolved_relations
              };
            })
        );
      }
    };
  }

  function createCreateTool(hateoas_url) {
    var create_url = withQuery(scriptUrl(hateoas_url), { mode: "newContent" });
    return {
      definition: {
        name: "erp5_create",
        description: "Create a new, EMPTY ERP5 document of ANY portal_type, either top-level inside a " +
          "module (e.g. a new Organisation inside organisation_module) or as a sub-object of an existing " +
          "document (e.g. a Sale Order Line inside a Sale Order). USE THIS WHEN: the user asks to " +
          "create/add a new document - this is the ONLY tool that creates documents. erp5_write only " +
          "edits documents that already exist: pointing it at a module (or anything else) does NOT " +
          "create a new document inside it, it just edits that module/document's own fields. This tool " +
          "ONLY creates the document - it does NOT set any field on it (not even the title), that always " +
          "requires a SEPARATE erp5_write call afterwards on the relative_url this returns; the task is " +
          "not finished until that erp5_write call has been made. DO NOT USE THIS WHEN: the document " +
          "already exists (use erp5_write). PREREQUISITE: use erp5_search (query=\"module_id:%\") or " +
          "erp5_read to confirm the real parent relative_url and the exact portal_type name first.",
        parameters: {
          type: "object",
          properties: {
            relative_url: {
              type: "string",
              description: "The parent to create the new document in: a module id (e.g. \"organisation_module\") for a top-level document, or an existing document's relative_url for a sub-object."
            },
            portal_type: {
              type: "string",
              description: "The portal type of the new document, e.g. \"Organisation\", \"Person\", \"Sale Order Line\"."
            }
          },
          required: ["relative_url", "portal_type"]
        }
      },
      execute: function (args) {
        var form_data = new URLSearchParams();
        form_data.append("portal_type", args.portal_type);
        form_data.append("parent_relative_url", args.relative_url);
        return catchApiError(
          fetch(create_url, { credentials: "same-origin", method: "POST", body: form_data })
            .then(function (response) {
              var location = response.headers.get("X-Location") || "",
                new_relative_url = location.indexOf("urn:jio:get:") !== -1 ?
                    location.split("urn:jio:get:").pop() : null,
                err;
              if (response.status !== 201 || !new_relative_url) {
                return response.text().then(function (text) {
                  err = new Error("HTTP " + response.status);
                  err.httpError = true;
                  err.response = response;
                  err.text = text;
                  throw err;
                });
              }
              return {
                status: "success",
                portal_type: args.portal_type,
                parent: args.relative_url,
                relative_url: new_relative_url,
                url: browserUrl(hateoas_url, new_relative_url),
                next_step: "Call erp5_read(relative_url=\"" + new_relative_url + "\") to get its field " +
                  "ids, then erp5_write to set them - this document has no fields set yet."
              };
            })
        );
      }
    };
  }

  function createExecuteJavascriptTool() {
    return {
      definition: {
        name: "execute_javascript",
        description: "Execute a snippet of JavaScript in a sandboxed interpreter and return its result. " +
          "The sandbox has no access to the page, network, cookies, or any other tool's state - it is " +
          "for computation only. The code runs as the body of a plain (synchronous, ES5) function: use " +
          "\"return <value>;\" to produce a result (only JSON-serializable values are usable). Errors " +
          "thrown by the code, and code that loops for too long, are reported back as an error message. " +
          "USE THIS WHEN: you need custom computation or to reshape/combine data you already have (e.g. " +
          "a previous tool's result) that's easier to do in code than by hand. DO NOT USE THIS WHEN: an " +
          "existing tool (erp5_search, erp5_read, erp5_write, erp5_create, draw_*) already does what you " +
          "need, or you need network/DOM access - this sandbox cannot reach either.",
        parameters: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "JavaScript source to run as a function body, e.g. \"return 1 + 1;\" or " +
                "\"var total = 0; for (var i = 0; i < 10; i++) { total += i; } return total;\"."
            }
          },
          required: ["code"]
        }
      },
      execute: function (args) {
        var interpreter = new Interpreter(
            "(function () {\n" + String(args.code || "") + "\n})()"
          ),
          steps = 0;
        while (interpreter.step()) {
          steps += 1;
          if (steps > EXECUTE_JAVASCRIPT_MAX_STEPS) {
            throw new Error("execute_javascript: exceeded " + EXECUTE_JAVASCRIPT_MAX_STEPS +
              " execution steps (possible infinite loop)");
          }
        }
        return interpreter.pseudoToNative(interpreter.value);
      }
    };
  }

  function createToolList(element, hateoas_url) {
    return [
      createSearchTool(hateoas_url),
      createReadTool(hateoas_url),
      createWriteTool(hateoas_url),
      createCreateTool(hateoas_url),
      createExecuteJavascriptTool(),
      {
        definition: {
          name: "clear_canvas",
          description: "Clear the drawing canvas. " + CANVAS_NOTE + " Call this before starting a new drawing.",
          parameters: { type: "object", properties: {} }
        },
        execute: function () {
          var ctx = getCanvasContext(element);
          ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
          return { cleared: true };
        }
      },
      {
        definition: {
          name: "draw_rectangle",
          description: "Draw a rectangle on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number", description: "left edge x" },
              y: { type: "number", description: "top edge y" },
              width: { type: "number" },
              height: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["x", "y", "width", "height"]
          }
        },
        execute: function (args) {
          var ctx = getCanvasContext(element),
            color = args.color || "black",
            fill = args.fill !== false;
          if (fill) {
            ctx.fillStyle = color;
            ctx.fillRect(args.x, args.y, args.width, args.height);
          } else {
            ctx.strokeStyle = color;
            ctx.strokeRect(args.x, args.y, args.width, args.height);
          }
          return { drawn: "rectangle", x: args.x, y: args.y, width: args.width, height: args.height, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_circle",
          description: "Draw a circle on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number", description: "center x" },
              y: { type: "number", description: "center y" },
              radius: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["x", "y", "radius"]
          }
        },
        execute: function (args) {
          var ctx = getCanvasContext(element),
            color = args.color || "black",
            fill = args.fill !== false;
          ctx.beginPath();
          ctx.arc(args.x, args.y, args.radius, 0, Math.PI * 2);
          if (fill) {
            ctx.fillStyle = color;
            ctx.fill();
          } else {
            ctx.strokeStyle = color;
            ctx.stroke();
          }
          return { drawn: "circle", x: args.x, y: args.y, radius: args.radius, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_line",
          description: "Draw a straight line segment on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x1: { type: "number" },
              y1: { type: "number" },
              x2: { type: "number" },
              y2: { type: "number" },
              color: { type: "string", description: "CSS color, default 'black'" },
              lineWidth: { type: "number", description: "stroke width in px, default 1" }
            },
            required: ["x1", "y1", "x2", "y2"]
          }
        },
        execute: function (args) {
          var ctx = getCanvasContext(element),
            color = args.color || "black",
            lineWidth = args.lineWidth || 1;
          ctx.beginPath();
          ctx.moveTo(args.x1, args.y1);
          ctx.lineTo(args.x2, args.y2);
          ctx.strokeStyle = color;
          ctx.lineWidth = lineWidth;
          ctx.stroke();
          return { drawn: "line", x1: args.x1, y1: args.y1, x2: args.x2, y2: args.y2, color: color, lineWidth: lineWidth };
        }
      },
      {
        definition: {
          name: "draw_polygon",
          description: "Draw a closed polygon (e.g. a triangle, or any custom shape/'form') on the canvas from a list of points. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              points: {
                type: "array",
                description: "ordered vertices, e.g. [{x:10,y:10},{x:50,y:10},{x:30,y:60}] for a triangle",
                items: {
                  type: "object",
                  properties: {
                    x: { type: "number" },
                    y: { type: "number" }
                  },
                  required: ["x", "y"]
                }
              },
              color: { type: "string", description: "CSS color, default 'black'" },
              fill: { type: "boolean", description: "fill (true) or outline only (false), default true" }
            },
            required: ["points"]
          }
        },
        execute: function (args) {
          var ctx = getCanvasContext(element),
            color = args.color || "black",
            fill = args.fill !== false,
            points = args.points,
            i;
          if (!points || points.length < 3) {
            throw new Error("points must be an array of at least 3 {x,y} vertices");
          }
          ctx.beginPath();
          ctx.moveTo(points[0].x, points[0].y);
          for (i = 1; i < points.length; i += 1) {
            ctx.lineTo(points[i].x, points[i].y);
          }
          ctx.closePath();
          if (fill) {
            ctx.fillStyle = color;
            ctx.fill();
          } else {
            ctx.strokeStyle = color;
            ctx.stroke();
          }
          return { drawn: "polygon", points: points, color: color, fill: fill };
        }
      },
      {
        definition: {
          name: "draw_text",
          description: "Draw text on the canvas. " + CANVAS_NOTE,
          parameters: {
            type: "object",
            properties: {
              x: { type: "number" },
              y: { type: "number" },
              text: { type: "string" },
              color: { type: "string", description: "CSS color, default 'black'" },
              fontSize: { type: "number", description: "px, default 16" }
            },
            required: ["x", "y", "text"]
          }
        },
        execute: function (args) {
          var ctx = getCanvasContext(element),
            color = args.color || "black",
            fontSize = args.fontSize || 16;
          ctx.fillStyle = color;
          ctx.font = fontSize + "px sans-serif";
          ctx.fillText(args.text, args.x, args.y);
          return { drawn: "text", x: args.x, y: args.y, text: args.text, color: color, fontSize: fontSize };
        }
      }
    ];
  }

  window.ChatTools = { createToolList: createToolList };
}(window, document));
