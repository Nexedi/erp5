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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function (options) {
      var page_gadget = this,
          sycn_method;
      page_gadget.options = options;
      if(page_gadget.options.doc.sync_flag==1){
        
       sycn_method="Ready To Sync"; 
      }else{
        
       sycn_method="Do Not Sync"; 
        
      }
      
      var state=translateString(getWorkflowState(page_gadget.options.doc.portal_type, page_gadget.options.jio_key, page_gadget.options.doc.sync_flag, page_gadget.options.doc.local_validation, page_gadget.options.doc.local_state));

return  page_gadget.getDeclaredGadget("erp5_form")
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
        
               "sale_price": {
                "description": "",
                "title": "",
                "default":"Sale price of a specific product to a specific customer",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 1,
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
                "editable": 1,
                "key": "username",
                "hidden": 0,
                "type": "StringField"
              },
              "state": {
                "description": "",
                "title": "State",
                "default": state,
                "css_class": "",
                "required": 1,
                "editable": 1,
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
                "editable": 1,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "client": {
                "description": "",
                "title": "Client",
                "default": page_gadget.options.doc.nextowner,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "client",
                "hidden": 0,
                "type": "StringField"
              },
              "organisation": {
                "description": "",
                "title": "Sales Organisation",
                "default": page_gadget.options.doc.previousowner,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "organisation",
                "hidden": 0,
                "type": "StringField"
              },
              "warehouse": {
                "description": "",
                "title": "Sender Warehouse",
                "default": page_gadget.options.doc.previouslocation,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "warehouse",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": page_gadget.options.doc.base_price,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "price",
                "hidden": 0,
                "type": "StringField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": page_gadget.options.doc.price_currency,
                "items":[["RMB","currency_module/CNY"],
                         ["Euro","currency_module/EUR"],
                         ["Hong Kong Dollar","currency_module/HKG"],
                         ["Rupee","currency_module/IDR"],
                         ["Ringgit","currency_module/MYR"],
                         ["Singapore Dollar","currency_module/SGD"],
                         ["Thai Baht","currency_module/THB"],
                         ["US Dollar","currency_module/USD"]
                        ],
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "currency",
                "hidden": 0,
                "type": "ListField"
              },
              "priced_quantity": {
                "description": "",
                "title": "Priced Quantity",
                "default": page_gadget.options.doc.priced_quantity,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "priced_quantity",
                "hidden": 0,
                "type": "StringField"
              },
               "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": page_gadget.options.doc.quantity_unit,
                "items":[["Weight","weight"],
                         ["Weight/Kilogram","weight/kg"],
                         ["Weight/Ton","weight/ton"],
                        ],
                "css_class": "",
                "required": 1,
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
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
                "editable": 1,
                "key": "sync_method",
                "hidden": 0,
                "type": "RadioField"
              },
              "client_head": {
                "description": "",
                "title": "",
                "default": "Client",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 1,
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
                "editable": 1,
                "key": "client",
                "hidden": 0,
                "type": "StringField"
              },
              "client_reference": {
                "description": "",
                "title": "Client Reference",
                "default": page_gadget.options.doc.nextowner_reference,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "client_reference",
                "hidden": 0,
                "type": "StringField"
              },
              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default": page_gadget.options.doc.default_telephone_coordinate_text,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "telephone",
                "hidden": 0,
                "type": "StringField"
              },
              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": page_gadget.options.doc.default_address_city,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "address_city",
                "hidden": 0,
                "type": "StringField"
              },
              "region": {
                "description": "",
                "title": "Region",
                "default": page_gadget.options.doc.default_address_region,
                "items":[["Africa","africa"],
                         ["America","america"],
                         ["Asia","asia"],
                         ["Asia/Cambodia","asia/cambodia"],
                         ["Asia/Singapore-Malaysia-Indonesia","asia/sin_mal_ind"],
                         ["Asia/Singapore-Malaysia-Indonesia/Indonesia","asia/sin_mal_ind/indonesia"],
                         ["Asia/Singapore-Malaysia-Indonesia/Malaysia","asia/sin_mal_ind/malaysia"],
                         ["Asia/Thailand","asia/thailand"],
                         ["China","china"],
                         ["China/Dongbei","china/dongbei"],
                         ["China/Guangdong","china/guangdong"],
                         ["China/Hainan","china/hainan"],
                         ["China/Huabei","china/huabei"],
                         ["China/Huadong","china/huadong"],
                         ["China/Huanan","china/huanan"],
                         ["China/Huazhong","china/huazhong"],
                         ["China/Other","china/other"],
                         ["China/Shandong","china/shandong"],
                         ["China/Xibei","china/xibei"],
                         ["China/Xinan","china/xinan"],
                         ["China/Yunnan","china/yunnan"],
                         ["Europe","europe"],
                         ["Rest of the world","row"],
                        ],
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "region",
                "hidden": 0,
                "type": "ListField"
              },
              "address_street": {
                "description": "",
                "title": "Default Address",
                "default": page_gadget.options.doc.default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "address_street",
                "hidden": 0,
                "type": "StringField"
              },
              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default": page_gadget.options.doc.default_address_zip_code,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "postal_code",
                "hidden": 0,
                "type": "StringField"
              },
              "email": {
                "description": "",
                "title": "Email",
                "default": page_gadget.options.doc.default_email_coordinate_text,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "email",
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
                ["client"], ["organisation"], ["warehouse"],
                ["price"], ["currency"], ["priced_quantity"],
                ["quantity_unit"],["total_dry_quantity"], ["total_amount_price"], 
                ["date"],["contract_no"], ["batch"], 
                ["comment"],["sync_method"]]],
                
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
