return '''function doCommit(form){
      submitAction(form,'BusinessTemplate_doVcsCommit');
  }

  function goBack(){
    open('BusinessTemplate_viewVcsStatus?do_extract:int=0', '_self');
  }'''
