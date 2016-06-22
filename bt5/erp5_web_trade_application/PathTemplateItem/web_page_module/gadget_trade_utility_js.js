function normalizeTitle(title){
  var result = new Array();
  for(var i=0; i<title.length; i++){
    var code = title.charCodeAt(i);
    if (code >= 0xff01 && code <= 0xff5e){
      code = code - 0xfee0;
    }else if (code == 0x3000){
      code = 0x20;
    }
    if (!((code >= 0x20 && code <= 0x24) || (code >= 0x26 && code <= 0x27) || (code >= 0x2a && code <= 0x2f) || (code >= 0x3a && code <= 0x40) || (code >= 0x5b && code <=0x60) || (code >= 0x7b && code <= 0x7e))){
      result[result.length] = String.fromCharCode(code)
    }
  }
  return result.join('').replace(/\s+/g, '');
}

function multiLoopEventListener(jquery_wrapped_set_target, type, useCapture, callback) {
  jquery_wrapped_set_target.each(function(){
    loopEventListener(this, type, useCapture, callback)
  })
}

function createOptions(select, option_array, selected_value){
  var option
  for(var i=0; i < option_array.length; i++){
    var option = document.createElement("option");
    option.text = option_array[i].text
    option.value = option_array[i].value
    select.appendChild(option);
  }
  if(selected_value){
    select.value = selected_value
  }
  $(select).selectmenu('refresh')
}

function getSequentialID(gadget,record_type_prefix){
  var prefix;
  
          return gadget.getSetting("last_sequential_id")
        .push(function (result) {
          if (result === undefined){
           last_sequential_id = 0;
         }else{
           last_sequential_id = Number(result);
       }
           last_sequential_id++;
           return gadget.setSetting("last_sequential_id", last_sequential_id); 
          })
        .push(function () {
          return gadget.getSetting("sequential_id_prefix");
          })
        .push(function (result) {
          if (result === undefined){
            prefix = getRandomPrefixForID();
            return gadget.setSetting("sequential_id_prefix", prefix); 
          } else{
            prefix = result;
            }
          })
          .push(function () {
           var date = new Date();
           var date_text = date.getFullYear()+('0'+(date.getMonth()+1)).slice(-2)+('0'+date.getDate()).slice(-2)
           return record_type_prefix + '-' + date_text + '-' + prefix + ('0000'+last_sequential_id).slice(-5)
          })
 
}

function getRandomPrefixForID(){
  function random(){
    return 65 + Math.floor( Math.random() * 26 );
  }
  return String.fromCharCode(random())+String.fromCharCode(random())+String.fromCharCode(random());
}

var my_price_currency = undefined;
var my_currency_option_array = new Array();
function createPriceCurrencySelection(gadget, selected){
  if (my_price_currency !== undefined && my_currency_option_array.length != 0){
    createOptions(gadget.props.element.querySelector('select[name=price_currency]'), my_currency_option_array, selected);
  }else{
    gadget.allDocs({
      query: 'portal_type: "Currency" AND validation_state: "validated"',
      select_list: ["title", "logical_path", "relative_url"],
      limit: [0, 1234567890]
    })
    .then(function(result){
      for (i = 0; i < result.data.total_rows; i += 1) {
        my_currency_option_array[i] = {text:result.data.rows[i].value.title,
                                       value:result.data.rows[i].value.relative_url};
      }
    })
    .then(function(){
      gadget.allDocs({
        query: 'portal_type:"Organisation" AND is_my_main_organisation:1',
        select_list:["price_currency"],
        limit:[0,2]})
      .then(function(result){
        if (result !== undefined && result.data.total_rows == 1){
          gadget.get(result.data.rows[0].id)
          .then(function(doc){
            my_price_currency = doc.price_currency
            if (selected === undefined){
              selected = my_price_currency;
            }
            createOptions(gadget.props.element.querySelector('select[name=price_currency]'), my_currency_option_array, selected);

          })
        }
      })
    })
  }
}

var my_input_user_name = undefined;
function fillMyInputUserName(gadget){
  var element;
  if (my_input_user_name !== undefined){
    element = gadget.props.element.querySelector('input[name=inputusername]');
    if (!element.value){
      element.value = my_input_user_name;
    }
  }else{
    return gadget.allDocs({
      query: 'portal_type: "Person"',
      select_list: ["title"],
      limit: [0, 1]
    })
    .then(function(result){
      if(result.data.total_rows > 0){
        my_input_user_name = result.data.rows[0].value.title;
        element = gadget.props.element.querySelector('input[name=inputusername]');
        if (!element.value){
          element.value = my_input_user_name;
        }
      }
    })
  }
}

function translateString(string) {
 // var language = Cookies.get('language');
 var language = 'en';

  if (language == undefined){
    language = 'zh'
  }
  return translation_data[language][string] || string;
}

function getWorkflowState(portal_type, id, sync_flag, local_validation, local_state){
  var sync_state;
  var validation_state;
  if(id.indexOf("_module/") > 0){
    sync_state = "Synced"
  }else if(sync_flag){
    sync_state = "Not Synced"
  }else{
    sync_state = "Not Ready To Sync"
  }

  if(['Purchase Record', 'Purchase Record Temp', 'Sale Record', 'Sale Record Temp'].indexOf(portal_type) >= 0){
    validation_state = ""
  }
  else if (local_validation == "no"){
    validation_state = local_state || "Waiting For HQ Validation"
  }else if (local_validation){
    validation_state = "Locally Validated"
  }else{
    validation_state = ""
  }

  var result = sync_state;
  if (validation_state){
    result = validation_state + " " + sync_state;
  }
  return translateString(result)
}

function addTemporarySupplier(gadget){
  var create_temporary_flag = false;
  var element = gadget.props.element.querySelector('input[name=previousowner_title]');
  if(element.value){
    return gadget.allDocs({
      query: 'portal_type: ("Organisation" OR "Organisation Temp") AND title_lowercase:"' + element.value.toLowerCase() + '"',
      limit: [0, 99999],
      select_list:['portal_type']
      })
      .then(function(result){
        var promise_list = [];
        if(result.data.total_rows > 0){
          for(var i=0; i < result.data.total_rows; i++){
            if(result.data.rows[i].value.portal_type=='Organisation Temp'){
              promise_list.push(gadget.jio_remove(result.data.rows[i].id))
              create_temporary_flag = true;
            }
          }
        }else{
          create_temporary_flag = true;
        }
        return RSVP.all(promise_list);
      })
      .then(function(){
        if(create_temporary_flag){
          var doc = {
            portal_type:"Organisation Temp",
            title: gadget.props.element.querySelector('input[name=previousowner_title]').value,
            title_lowercase: gadget.props.element.querySelector('input[name=previousowner_title]').value.toLowerCase(),
            reference: gadget.props.element.querySelector('input[name=previousowner_reference]').value,
            default_telephone_coordinate_text: gadget.props.element.querySelector('input[name=default_telephone_coordinate_text]').value,
            default_address_city: gadget.props.element.querySelector('input[name=default_address_city]').value,
            default_address_region: gadget.props.element.querySelector('select[name=default_address_region]').value,
            default_address_street_address: gadget.props.element.querySelector('textarea[name=default_address_street_address]').value,
            default_address_zip_code: gadget.props.element.querySelector('input[name=default_address_zip_code]').value,
            default_email_coordinate_text: gadget.props.element.querySelector('input[name=default_email_coordinate_text]').value
          };
          gadget.post(doc);
        }
      })
  }
}

function addTemporaryCustomer(gadget){
  var create_temporary_flag = false;
  var element = gadget.props.element.querySelector('input[name=nextowner_title]');
  if(element.value){
    return gadget.allDocs({
      query: 'portal_type: ("Organisation" OR "Organisation Temp") AND title_lowercase:"' + element.value.toLowerCase() + '"',
      limit: [0, 99999],
      select_list:['portal_type']
      })
      .then(function(result){
        var promise_list = [];
        if(result.data.total_rows > 0){
          for(var i=0; i < result.data.total_rows; i++){
            if(result.data.rows[i].value.portal_type=='Organisation Temp'){
              promise_list.push(gadget.jio_remove(result.data.rows[i].id))
              create_temporary_flag = true;
            }
          }
        }else{
          create_temporary_flag = true;
        }
        return RSVP.all(promise_list);
      })
      .then(function(){
        if(create_temporary_flag){
          var doc = {
            portal_type:"Organisation Temp",
            title: gadget.props.element.querySelector('input[name=nextowner_title]').value,
            title_lowercase: gadget.props.element.querySelector('input[name=nextowner_title]').value.toLowerCase(),
            reference: gadget.props.element.querySelector('input[name=nextowner_reference]').value,
            default_telephone_coordinate_text: gadget.props.element.querySelector('input[name=default_telephone_coordinate_text]').value,
            default_address_city: gadget.props.element.querySelector('input[name=default_address_city]').value,
            default_address_region: gadget.props.element.querySelector('select[name=default_address_region]').value,
            default_address_street_address: gadget.props.element.querySelector('input[name=default_address_street_address]').value,
            default_address_zip_code: gadget.props.element.querySelector('input[name=default_address_zip_code]').value,
            default_email_coordinate_text: gadget.props.element.querySelector('input[name=default_email_coordinate_text]').value
          };
          gadget.jio_post(doc);
        }
      })
  }
}

function addTemporaryProduct(gadget){
  var create_temporary_flag = false;
  var element = gadget.props.element.querySelector('input[name=product_title]');
  if(element.value){
    return gadget.allDocs({
      query: 'portal_type: "Product" AND title_lowercase:"' + element.value.toLowerCase() + '"',
      limit: [0, 99999],
      select_list:['portal_type']
      })
      .then(function(result){
        var promise_list = [];
        if(result.data.total_rows > 0){
          for(var i=0; i < result.data.total_rows; i++){
            if(result.data.rows[i].value.portal_type=='Product Temp'){
              promise_list.push(gadget.jio_remove(result.data.rows[i].id))
              create_temporary_flag = true;
            }
          }
        }else{
          create_temporary_flag = true;
        }
        return RSVP.all(promise_list);
      })
      .then(function(){
        if(create_temporary_flag){
          var doc = {
            portal_type:"Product Temp",
            title: gadget.props.element.querySelector('input[name=product_title]').value,
            title_lowercase: gadget.props.element.querySelector('input[name=product_title]').value.toLowerCase(),
            reference: gadget.props.element.querySelector('input[name=product_reference]').value,
            product_line: gadget.props.element.querySelector('select[name=product_line]').value
          };
          gadget.jio_post(doc);
        }
      })
  }
}

function removeTemporaryBaseData(gadget){
  var temp_organisation_list = [];
  var organisation_list = [];
  var temp_product_list = [];
  var product_list = [];
  return gadget.allDocs(
    {query: 'portal_type: ("Organisation" OR "Organisation Temp" OR "Product" OR "Product Temp")',
     limit: [0, 99999],
     select_list: ['title_lowercase', 'portal_type']
     })
     .then(function(result){
       for(var i=0; i<result.data.total_rows; i++){
         if(result.data.rows[i].value.portal_type == 'Organisation Temp'){
           temp_organisation_list.push({title_lowercase:result.data.rows[i].value.title_lowercase, id:result.data.rows[i].id})
         }else if(result.data.rows[i].value.portal_type == 'Organisation'){
           organisation_list.push(result.data.rows[i].value.title_lowercase)
         }else if(result.data.rows[i].value.portal_type == 'Product Temp'){
           temp_product_list.push({title_lowercase:result.data.rows[i].value.title_lowercase, id:result.data.rows[i].id})
         }else if(result.data.rows[i].value.portal_type == 'Product'){
           product_list.push(result.data.rows[i].value.title_lowercase)
         }
       }
     })
     .then(function(){
       var promise_list = [];
       for(var i=0; i<temp_organisation_list.length; i++){
         if(organisation_list.indexOf(temp_organisation_list[i].title_lowercase)>=0){
           promise_list.push(gadget.remove(temp_organisation_list[i].id))
         }
       }
       for(var i=0; i<temp_product_list.length; i++){
         if(product_list.indexOf(temp_product_list[i].title_lowercase)>=0){
           promise_list.push(gadget.remove(temp_product_list[i].id))
         }
       }
       return RSVP.all(promise_list)
     })
}

function fillDryWetDrc(evt, dry_element, wet_element, drc_element){
  var dry = Number(dry_element.value) || 0;
  var wet = Number(wet_element.value) || 0;
  var drc = Number(drc_element.value) || 0;
  drc_element.value = drc;
  if (evt.target == wet_element || evt.target == drc_element){
    dry = wet * drc / 100;
    dry = Math.round(dry * 100000000) / 100000000;
    if (isNaN(dry)){
      dry = 0;
    }
    dry_element.value = dry;
    if (!wet){
      wet_element.value = 0;
    }
    else if (wet_element.value != String(wet)){
      wet_element.value = wet;
    }
  }else{
    wet = dry / drc * 100;
    wet = Math.round(wet * 100000000) / 100000000;
    if (isNaN(wet)){
      wet = 0;
    }
    wet_element.value = wet;
    if(!dry){
      dry_element.value = 0;
    }
    else if (dry_element.value != String(dry)){
      dry_element.value = dry;
    }
  }
}
