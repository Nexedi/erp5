/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document*/
(function (window, rJS, RSVP, document) {
  'use strict';

  const e = React.createElement;;

  const ERP5Theme = {}
  /*
    ArrayFieldTemplatex: (props) => {
      return React.createElement(
        'div',
        {
          className: props.className,
        },
        props.items &&
          props.items.map((element) =>
            React.createElement(
              'div',
              {
                key: element.key,
                className: element.className,
              },
              React.createElement('div', null, element.children),
              React.createElement(
                'button',
                {
                  onClick: element.onDropIndexClick(element.index),
                },
                'Delete'
              ),
              React.createElement('hr', null)
            )
          ),
        props.canAdd &&
          React.createElement(
            'div',
            {
              className: 'row',
            },
            React.createElement(
              'p',
              {
                className: 'col-xs-3 col-xs-offset-9 array-item-add text-right',
              },
              React.createElement(
                'button',
                {
                  onClick: props.onAddClick,
                  type: 'button',
                },
                'Add'
              )
            )
          )
      );
    },
  };
  */

  /**
   * Prepare a ui-schema from the conventions of SlapOS instance parameters schema.
   * This does the following:
   *  - remove `default` from schema. In SlapOS schemas we use `default` as a documentation
   *    and we don't expect to pre-fill the form data with default.
   *    TODO: we don't always want to remove default (maybe we never want ?)
   *  - TODO something with textarea
   *
   * TODO: if this is really needed - if we use a theme this is probably not, don't mutate
   * arguments like this but return new copies instead.
   */
  function makeUiSchema(schema, uiSchema) {
    if (schema.properties) {
      for (const [key, value] of Object.entries(schema.properties)) {
        uiSchema[key] = {};
        if (value.default) {
          /** XXX value.const ... isn't it a bug in ERP5 SR schema ? */
          if (value?.type === 'string' && value.const === undefined) {
            uiSchema[key]['ui:placeholder'] = value.default;
          } else {
            // XXX seems ugly
            // uiSchema[key]['ui:help'] = `Default value: ${value.default}`
          }
          if (value.const === undefined) {
            value.default = undefined;
          }
        }
        if (value?.type === 'object') {
          makeUiSchema(value, uiSchema[key]);
        }
        for (const oneOf of value.oneOf || []) {
          makeUiSchema(oneOf, uiSchema[key]);
        }
        for (const allOf of value.allOf || []) {
          makeUiSchema(allOf, uiSchema[key]);
        }
        for (const anyOf of value.anyOf || []) {
          makeUiSchema(anyOf, uiSchema[key]);
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
            makeUiSchema(schema, uiSchema);
            console.log('after simplification', schema, uiSchema);

            const log = (type) => console.log.bind(console, type);

            ReactDOM.render(
              React.createElement(JSONSchemaForm.withTheme(ERP5Theme), {
                schema: schema,
                uiSchema: uiSchema,
                // XXX don't make a <form> by default
                tagName: 'div',
                // TODO: handle malformed json
                formData: JSON.parse(modification_dict.value),
                // TODO: keep promise chain
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
      if (!this.initialized) {
      }
      if (modification_dict.schema) {
        console.log(modification_dict);
      }
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
      return true;
    });
})(window, rJS, RSVP, document);
