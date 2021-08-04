/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document*/
(function (window, rJS, RSVP, document) {
  'use strict';

  /**
* Prepare a ui-schema from the conventions of SlapOS instance parameters schema.
* This does the following:
*  - remove `default` from schema. In SlapOS schemas we use `default` as a documentation
*    and we don't expect to pre-fill the form data with default.
*    TODO: we don't always want to remove default (maybe we never want ?)
*  - support textearea, like we have with SlapOS parameter editor
*
*  TODO: if this is really needed - if we use a theme this is probably not, don't mutate
*  arguments like this but return new copies instead.
*  Also, this does not support cyclic schemas (like for example https://json-schema.org/draft-07/schema )
*
*  @param {{ properties: any; }} schema
*  @param {{ [x: string]: any; }} uiSchema
*  @param {Set<any>} visited
*/
function makeUiSchema(schema, uiSchema, visited) {
    if (visited.has(schema)) {
      return
    }
    visited.add(schema)
    if (schema.properties) {
      for (const [key, value] of Object.entries(schema.properties)) {
        uiSchema[key] = {};
        if (value.default) {
          if (key == 'tcpv4-port') {
            console.log(key, value);
          }
          /** XXX value.const ... isn't it a bug in ERP5 SR schema ? */
          if (value?.type === 'string' && value.const === undefined) {
            uiSchema[key]['ui:placeholder'] = value.default;
          } else {
            // XXX seems ugly
            // uiSchema[key]['ui:help'] = `Default value: ${value.default}`
          }
          if (value.const === undefined) {
            delete value.default;
          }
        }
        // This is something used in SlapOS schemas
        if (value.textarea) {
          uiSchema[key]["ui:widget"] = "textarea"
        }
        if (value?.type === 'object') {
          makeUiSchema(value, uiSchema[key], visited);
        }
        for (const oneOf of value.oneOf || []) {
          makeUiSchema(oneOf, uiSchema[key], visited);
        }
        for (const allOf of value.allOf || []) {
          makeUiSchema(allOf, uiSchema[key], visited);
        }
        for (const anyOf of value.anyOf || []) {
          makeUiSchema(anyOf, uiSchema[key], visited);
        }
      }
    }
  }

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        data: {},
        value: options.value,
        key: options.key,
        schema_url: options.schema,
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (modification_dict.schema_url) {
        return $RefParser
          .dereference(modification_dict.schema_url)
          .then(function (schema) {
            let uiSchema = {};
            // TODO: wouldn't using mergeAllOf here solve the problem of 
            // ERP5's kumofs default port
            schema = JSONSchemaForm.utils.retrieveSchema(schema);
            
            makeUiSchema(schema, uiSchema, new Set())
            console.log('after simplification', schema, uiSchema);

            const log = (type) => console.log.bind(console, type);

            ReactDOM.render(
              // XXX we can use withTheme here if we want a theme
              React.createElement(JSONSchemaForm.withTheme({}), {
                schema: schema,
                uiSchema: uiSchema,
                // XXX don't make a <form> by default
                tagName: 'div',
                // TODO: handle malformed json
                formData: JSON.parse(modification_dict.value),
                // TODO: change state in a job to keep promise chain
                onChange: (state) =>
                  gadget.changeState({
                    data: state.formData,
                    errors: state.errors,
                  }),
                //     onSubmit: log('submitted'),
                onError: log('errors'),
              }),
              gadget.element
            );
          });
      }
      console.log(this.element, modification_dict);
    })

    .declareMethod(
      'getContent',
      function () {
        var result = {};
        result[this.state.key] = JSON.stringify(this.state.data, null, '  ');
        return result;
      },
      { mutex: 'changestate' }
    )

    .declareMethod('checkValidity', function () {
      // TODO
      return true;
    });
})(window, rJS, RSVP, document);
