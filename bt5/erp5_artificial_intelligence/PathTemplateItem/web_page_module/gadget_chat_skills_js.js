/*global window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SKILL_LIST = [
    {
      name: "draw_house",
      triggers: ["house", "home"],
      instructions: "Skill: draw_house\n" +
        "To draw a simple house on the canvas using the drawing tools:\n" +
        "1. Call clear_canvas first.\n" +
        "2. Call draw_rectangle for the main body.\n" +
        "3. Call draw_polygon with 3 points for a triangular roof sitting on top of the body.\n" +
        "4. Optionally add a door and windows with draw_rectangle.\n"
    },
    {
      name: "draw_stick_figure",
      triggers: ["stick figure", "stickman", "person", "human"],
      instructions: "Skill: draw_stick_figure\n" +
        "To draw a simple stick figure on the canvas using the drawing tools:\n" +
        "1. Call clear_canvas first.\n" +
        "2. Call draw_circle for the head.\n" +
        "3. Call draw_line for the body (vertical line down from the head).\n" +
        "4. Call draw_line twice for the arms.\n" +
        "5. Call draw_line twice for the legs.\n"
    },
    {
      name: "erp5_hateoas",
      triggers: [
        "hateoas", "erp5 api", "search erp5", "search the catalog", "look up in erp5",
        "edit this document", "update this document", "portal_type", "create a", "create an", "add a new"
      ],
      instructions: "Skill: erp5_hateoas\n" +
        "Use erp5_search, erp5_read, erp5_write and erp5_create whenever the user wants you to look up, " +
        "search, edit or create ERP5 documents of ANY portal_type - Person, Organisation, Product, " +
        "Purchase Order, or anything else this ERP5 has - beyond what the other tools already cover; " +
        "none of them are limited to a single portal_type. They call this ERP5 site's own hypermedia " +
        "REST API (web_site_module/harness_ai/hateoas) - the same generic API an external HATEOAS-based " +
        "MCP client would use - authenticated as the current logged-in user.\n" +
        "CRITICAL: erp5_write can only edit a document that ALREADY exists - never call erp5_write on a " +
        "MODULE id (e.g. \"organisation_module\") hoping it will create something inside it, that only " +
        "renames the module itself and silently creates nothing, which looks like success but is not. " +
        "The only tool that creates a document is erp5_create, and it ONLY creates an empty document - it " +
        "never sets any field. This does NOT mean avoid erp5_write during a create task: erp5_write on " +
        "the NEW document's own relative_url (the one erp5_create just returned) is a separate, required " +
        "call right afterwards to actually give it a title and any other field - see step 3.\n" +
        "IMPORTANT: only ever use erp5_search/erp5_read to look around and gather information on your " +
        "own initiative - they cannot modify data. Never call erp5_write or erp5_create unless the user " +
        "has explicitly asked for that specific change, or has confirmed after you described exactly " +
        "what it would do - treat every write/create as a real, user-approved action.\n" +
        "1. To find documents: erp5_search(query='<portal_catalog query, e.g. portal_type:\"Person\" " +
        "AND title:\"%acme%\">'). Only use the catalog fields \"title\" and \"reference\" for text " +
        "matching (they exist on virtually every portal_type) - never invent a field name like " +
        "\"name\", it silently matches nothing instead of erroring. Omit relative_url to search " +
        "unscoped across the whole catalog (e.g. erp5_search(query=\"module_id:%\") lists every real " +
        "module id in this ERP5 - never guess a module id from a portal_type name, e.g. assuming " +
        "\"Product\" lives in \"product_module\": the \"<type>_module\" pattern is common but has real " +
        "exceptions). The result lists matching documents with their relative_url.\n" +
        "2. To read one specific document: erp5_read(relative_url='<relative_url from a search " +
        "result>'). Its \"fields\" map lists every field with its EXACT id, type, current value and " +
        "whether it's editable. COPY THAT ID VERBATIM when writing: ERP5 field ids are very often " +
        "prefixed (e.g. the title field is usually \"my_title\", not \"title\") - it becomes " +
        "\"field_my_title\" when writing, never guess it as \"field_title\".\n" +
        "3. Creating a document is a THREE-CALL sequence, all three calls are required - do not stop " +
        "early:\n" +
        "   a) erp5_create(relative_url='<parent module or document, e.g. \"organisation_module\">', " +
        "portal_type='<e.g. \"Organisation\">'). It ONLY creates an empty document - it never sets any " +
        "field, not even the title, that is expected and not an error. Its result's \"relative_url\" is " +
        "the new document; its \"next_step\" spells out exactly what to do next - follow it.\n" +
        "   b) erp5_read(relative_url='<the new document's relative_url from step a>') to get its exact " +
        "field ids (they are very often prefixed, e.g. \"my_title\" not \"title\" - copy them verbatim).\n" +
        "   c) erp5_write(relative_url='<same new document>', field_values={\"field_my_title\": \"...\"}) " +
        "to actually set them. Skipping this call leaves the document exactly as blank as it was right " +
        "after erp5_create - the task is not done until this erp5_write call has been made and returned " +
        "status \"success\".\n" +
        "4. To set field values on any existing document (this is also step 3c, just phrased generally): " +
        "erp5_write(relative_url='...', field_values={\"field_my_title\": \"...\"}). It fetches the " +
        "current field defaults first and submits the complete form so nothing else gets silently " +
        "dropped - ERP5's edit endpoint requires the WHOLE form submitted together, not just the changed " +
        "fields. If a field_values key doesn't match any real field, the call fails with an error naming " +
        "the bad key(s) instead of silently doing nothing - if that happens, call erp5_read again and " +
        "fix the key, then call erp5_write again; do not give up after the first attempt.\n" +
        "5. RELATION FIELDS: erp5_read shows some fields with \"portal_types\"/\"urls\" instead of a " +
        "plain value (e.g. a Purchase/Sale Order's Supplier/Client, or an Order Line's Resource/" +
        "\"Product or Service\"). To set one, just pass the target document's exact title as a plain " +
        "string in field_values, e.g. {\"field_my_source_title\": \"APZQR\"} to set a Purchase Order's " +
        "Supplier to the organisation titled \"APZQR\" - erp5_write looks it up in the catalog and links " +
        "it automatically, no UID lookup needed on your part. If the result's \"unresolved_relations\" " +
        "lists that field afterwards, no document with that exact title was found: erp5_search for it " +
        "first (it may be misspelled, or need creating itself) rather than leaving the relation unset.\n" +
        "6. DOCUMENTS MADE OF A HEADER + LINES (Purchase Order, Sale Order, Invoice, and similar): the " +
        "product/quantity/price the user describes almost never belong on the header document - they are " +
        "fields on separate LINE sub-objects (e.g. \"Purchase Order Line\") created inside it. E.g. " +
        "\"create a purchase order from Supplier X for 12x Product Y at 23 EUR\" needs the full 3-call " +
        "erp5_create/erp5_read/erp5_write sequence (step 3) TWICE:\n" +
        "   a) once for the order header itself (portal_type e.g. \"Purchase Order\"), setting header " +
        "fields such as the supplier relation (commonly a field named like \"my_source_title\").\n" +
        "   b) once more with relative_url set to the header's OWN relative_url (from call a) and " +
        "portal_type e.g. \"Purchase Order Line\", to create the line, then erp5_read/erp5_write it with " +
        "its own fields (commonly named like \"my_resource_title\" for the product/service relation, " +
        "\"my_quantity\", \"my_price\") - these common names are a starting hint, not a guarantee: always " +
        "confirm the exact ids via erp5_read on the header/line as created on THIS ERP5 instance, never " +
        "assume they're correct without reading.\n" +
        "A task like this is only complete once every value the user mentioned - including line-level " +
        "ones - has been confirmed set via erp5_write's \"success\" result; do not report it done after " +
        "only creating the header.\n" +
        "Always explain in plain language what you found or what you are about to change before making " +
        "any write or create call, and summarize the result afterwards.\n"
    }
  ];

  function matchSkillListFrom(text, skill_list) {
    var lower = String(text).toLowerCase();
    return skill_list.filter(function (skill) {
      return skill.triggers.some(function (trigger) {
        return lower.indexOf(trigger.toLowerCase()) !== -1;
      });
    });
  }

  function matchSkillList(text) {
    return matchSkillListFrom(text, SKILL_LIST);
  }

  window.ChatSkills = {
    SKILL_LIST: SKILL_LIST,
    matchSkillList: matchSkillList,
    matchSkillListFrom: matchSkillListFrom
  };
}(window));
