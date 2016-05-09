/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  
  
  
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.region=[];
      g.props.quantity_unit=[];
      g.props.currency=[];
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function (options) {
      var page_gadget = this,
          gadget,
          sycn_method,
          title,
          relative_url,
          element,
          textNode;
      page_gadget.options = options;
      if(page_gadget.options.doc.sync_flag==1){
        
       sycn_method="Ready To Sync"; 
      }else{
        
       sycn_method="Do Not Sync"; 
        
      }
      
      var state=translateString(getWorkflowState(page_gadget.options.doc.portal_type, page_gadget.options.jio_key, page_gadget.options.doc.sync_flag,   page_gadget.options.doc.local_validation, page_gadget.options.doc.local_state));
    
     return new RSVP.Queue()
        
       .push(function () {
      
          return RSVP.all([

           page_gadget.allDocs({
            query: 'portal_type: "Currency" AND validation_state: "validated"',
            select_list: ["title", "logical_path", "relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          }),
      
           page_gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "quantity_unit/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          }),
      
      
      
           page_gadget.allDocs({
            query: 'portal_type: "Category" AND relative_url: "region/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          })
      
      
          ]);
            })
        .push(function (allresult) {
            var i,j;
            for (i = 0; i < allresult[0].data.total_rows; i += 1) {
              title=allresult[0].data.rows[i].value.title;
              relative_url=allresult[0].data.rows[i].value.relative_url;
              page_gadget.props.currency.push([title,relative_url]);
             }

      
      
            for (i = 0; i < allresult[1].data.total_rows; i += 1) {
              title= allresult[1].data.rows[i].value.logical_path || allresult[1].data.rows[i].value.title;
              relative_url=allresult[1].data.rows[i].value.category_relative_url;
              page_gadget.props.quantity_unit.push([title,relative_url]);
  
            
            }
      
      
            for (i = 0; i < allresult[2].data.total_rows; i += 1) {
              title=allresult[2].data.rows[i].value.logical_path || allresult[2].data.rows[i].value.title;
              relative_url=allresult[2].data.rows[i].value.category_relative_url;
              page_gadget.props.region.push([title,relative_url]);

            
           }
      
          return;
      
      })
       .push(function () {

          return  page_gadget.getDeclaredGadget("erp5_form")
      })
        .push(function (form_gadget) {
          gadget=form_gadget;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
        
               "sale_price": {
                "description": "",
                "title": "",
                "default":"Sale price of a specific product to a specific customer",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 0,
                "key": "sale_price",
                "hidden": 0,
                "type": "ReadonlyField"
              },
        
              "username": {
                "description": "",
                "title": "Input User Name",
                "default": page_gadget.options.doc.inputusername,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "inputusername",
                "hidden": 0,
                "type": "StringField"
              },
              "state": {
                "description": "",
                "title": "State",
                "default": state,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "state",
                "hidden": 0,
                "type": "ReadonlyField"
              },
              "product": {
                "description": "",
                "title": "Product Title",
                "default": page_gadget.options.doc.product,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "nextowner": {
                "description": "",
                "title": "Client",
                "default": page_gadget.options.doc.nextowner,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "nextowner",
                "hidden": 0,
                "type": "StringField"
              },
              "organisation": {
                "description": "",
                "title": "Sales Organisation",
                "default": page_gadget.options.doc.previousowner,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "previousowner",
                "hidden": 0,
                "type": "StringField"
              },
              "warehouse": {
                "description": "",
                "title": "Sender Warehouse",
                "default": page_gadget.options.doc.previouslocation,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "previouslocation",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": page_gadget.options.doc.base_price,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "base_price",
                "hidden": 0,
                "type": "StringField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": page_gadget.options.doc.price_currency,
                "items":page_gadget.props.currency,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "price_currency",
                "hidden": 0,
                "type": "ListField"
              },
              "priced_quantity": {
                "description": "",
                "title": "Priced Quantity",
                "default": page_gadget.options.doc.priced_quantity,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "priced_quantity",
                "hidden": 0,
                "type": "StringField"
              },
               "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": page_gadget.options.doc.quantity_unit,
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "total_dry_quantity": {
                "description": "",
                "title": "Quantity",
                "default": page_gadget.options.doc.total_dry_quantity,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "total_dry_quantity",
                "hidden": 0,
                "type": "StringField"
              },
              "total_amount_price": {
                "description": "",
                "title": "Total Price",
                "default": page_gadget.options.doc.total_amount_price,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "total_amount_price",
                "hidden": 0,
                "type": "StringField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": page_gadget.options.doc.date,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "date",
                "hidden": 0,
                "type": "StringField"
              },
              "contract_no": {
                "description": "",
                "title": "Contract No",
                "default": page_gadget.options.doc.contract_no,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "contract_no",
                "hidden": 0,
                "type": "StringField"
              },
              "batch": {
                "description": "",
                "title": "Batch",
                "default": page_gadget.options.doc.batch,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "batch",
                "hidden": 0,
                "type": "TextAreaField"
              },
              "comment": {
                "description": "",
                "title": "Comment",
                "default": page_gadget.options.doc.comment,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "comment",
                "hidden": 0,
                "type": "StringField"
              },
              "sync_method": {
                "description": "",
                "title": "Sync Method",
                "default": sycn_method,
                "items":[["Ready To Sync","Ready To Sync"],
                         ["Do Not Sync","Do Not Sync"],
                        ],
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "sync_flag",
                "hidden": 0,
                "type": "RadioField"
              },
              "client_head": {
                "description": "",
                "title": "",
                "default": "Client",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 0,
                "key": "client_head",
                "hidden": 0,
                "type": "ReadonlyField"
              },
              
              
              
              "client": {
                "description": "",
                "title": "Client",
                "default": page_gadget.options.doc.nextowner_title,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "nextowner_title",
                "hidden": 0,
                "type": "StringField"
              },
              "client_reference": {
                "description": "",
                "title": "Client Reference",
                "default": page_gadget.options.doc.nextowner_reference,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "nextowner_reference",
                "hidden": 0,
                "type": "StringField"
              },
              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default": page_gadget.options.doc.default_telephone_coordinate_text,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              },
              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": page_gadget.options.doc.default_address_city,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField"
              },
              "region": {
                "description": "",
                "title": "Region",
                "default": page_gadget.options.doc.default_address_region,
                "items":page_gadget.props.region,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField"
              },
              "address_street": {
                "description": "",
                "title": "Default Address",
                "default": page_gadget.options.doc.default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField"
              },
              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default": page_gadget.options.doc.default_address_zip_code,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_address_zip_code",
                "hidden": 0,
                "type": "StringField"
              },
              "email": {
                "description": "",
                "title": "Email",
                "default": page_gadget.options.doc.default_email_coordinate_text,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              }
         
            }}},
            form_definition: {
              group_list: [
                
                
                [
                 "left",
                [["sale_price"],
                  ["username"], ["state"], ["product"],
                ["nextowner"], ["organisation"], ["warehouse"],
                ["price"], ["currency"], ["priced_quantity"],
                ["quantity_unit"],["total_dry_quantity"], ["total_amount_price"], 
                ["date"],["contract_no"], ["batch"], 
                ["comment"],["sync_method"]]
                ],
                
                [
                "right",
                [["client_head"],
                ["client"], ["client_reference"], ["telephone"],
                ["address_city"], ["region"], ["address_street"],
                ["postal_code"], ["email"]]
                ]
                 
              ]
   
            }
          });
        })


        .push(function () {
                  /*  gadget.props.element.querySelector('[name="inputusername"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="product"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="nextowner"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="previousowner"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="previouslocation"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="base_price"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="priced_quantity"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="price_currency"]').setAttribute('disabled', 'disabled');
                    gadget.props.element.querySelector('[name="quantity_unit"]').setAttribute('disabled', 'disabled');
                    gadget.props.element.querySelector('[name="total_dry_quantity"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="total_amount_price"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="date"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="contract_no"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="batch"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="comment"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="sync_flag"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="nextowner_title"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="nextowner_reference"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_telephone_coordinate_text"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_city"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_region"]').setAttribute('disabled', 'disabled');
                    gadget.props.element.querySelector('[name="default_address_street_address"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_address_zip_code"]').setAttribute('readOnly', 'readOnly');
                    gadget.props.element.querySelector('[name="default_email_coordinate_text"]').setAttribute('readOnly', 'readOnly');
  
  
                    element = document.createElement('h3');
                    textNode= document.createTextNode('Sale price of a specific product to a specific customer');
                    element.setAttribute("class", "ui-content-header-inline");
                    element.setAttribute('data-i18n', "Sale price of a specific product to a specific customer");
                    element.appendChild(textNode);
                    //.prepend(element);
                    $( ".left" ).prepend(element);*/

        });






    })

   /* .declareService(function () {
      var form_gadget = this;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("erp5_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (content_dict) {
            return form_gadget.jio_put(
              'CONNECTION',
              content_dict
            );
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display', options: {page: 'contact'}})
            ]);
          })
          .push(undefined, function (error) {
            return form_gadget.notifySubmitted()
              .push(function () {
                form_gadget.props.element.querySelector('pre').textContent = error;
              });
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });*/



}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
