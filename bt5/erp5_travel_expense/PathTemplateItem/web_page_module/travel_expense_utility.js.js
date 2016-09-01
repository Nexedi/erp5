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

function getSequentialID(record_type_prefix){
  var last_sequential_id = Cookies.get('last_sequential_id');
  if (last_sequential_id == undefined){
    last_sequential_id = 0;
  }else{
    last_sequential_id = Number(last_sequential_id);
  }
  last_sequential_id++;
  Cookies.set('last_sequential_id', last_sequential_id, {expires:36500, path:'/', secure:true});

  var prefix = Cookies.get('sequential_id_prefix');
  if (prefix == undefined){
    prefix = getRandomPrefixForID();
    Cookies.set('sequential_id_prefix', prefix, {expires:36500, path:'/', secure:true});
  }
  var date = new Date();
  var date_text = date.getFullYear()+('0'+(date.getMonth()+1)).slice(-2)+('0'+date.getDate()).slice(-2)
  return record_type_prefix + '-' + date_text + '-' + prefix + ('0000'+last_sequential_id).slice(-5)
}

function getRandomPrefixForID(){
  function random(){
    return 65 + Math.floor( Math.random() * 26 );
  }
  return String.fromCharCode(random())+String.fromCharCode(random())+String.fromCharCode(random());
}

var my_resource = undefined;
var my_currency_option_array = new Array();
function createResourceSelection(gadget, selected){
  if (my_resource !== undefined && my_currency_option_array.length != 0){
    createOptions(gadget.props.element.querySelector('select[name=resource]'), my_currency_option_array, selected);
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
      createOptions(gadget.props.element.querySelector('select[name=resource]'), my_currency_option_array, selected);
    });
  }
}

function translateString(string) {
  var language = Cookies.get('language');
  if (language == undefined){
    language = 'en'
  }
  return translation_data[language][string] || string;
}

function getWorkflowState(portal_type, id, sync_flag){
  var sync_state;
  if(id.indexOf("_module/") > 0){
    sync_state = "Synced"
  }else if(sync_flag){
    sync_state = "Not Synced"
  }else{
    sync_state = "Not Ready To Sync"
  }
  return translateString(sync_state)
}