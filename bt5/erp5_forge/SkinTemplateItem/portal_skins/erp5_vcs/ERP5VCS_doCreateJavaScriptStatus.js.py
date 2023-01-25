return '''
    var tree = null;
    var business_template;
    var is_expanded=false;
    var is_showing_unmodified=false;
    var ie  = document.all;
    var ns6 = document.getElementById&&!document.all;
    var isMenu  = false ;
    var menuSelObj = null ;
    var overpopupmenu = false;
    var curHeight = 300;

    // This script is intended for use with a minimum of Netscape 4 or IE 4.
    if(document.getElementById) {
      var upLevel = true;
    } else if(document.layers) {
      var ns4 = true;
    } else if(document.all) {
      var ie4 = true;
    }

    function showObject() {
      var splash;
      if (ns4) {
        splash = document.splashScreen;
	splash.visibility = "visible";
      }
      if (ie4) {
        splash = document.all.splashScreen;
	splash.style.visibility = "visible";
      }
      if (upLevel){
        splash = document.getElementById("splashScreen");
        splash.style.visibility = "visible";
      }
    }

     function hideObject() {
       var splash;
       if (ns4) {
         splash = document.splashScreen;
	 splash.visibility = "hide";
       }
       if (ie4) {
         splash = document.all.splashScreen;
	 splash.style.visibility = "hidden";
       }
       if (upLevel){
         splash = document.getElementById("splashScreen");
         splash.style.visibility = "hidden";
       }
     }

    function preLoadImages(){
      var imSrcAr = new
      Array('document.png','iconCheckAll.gif','line2.gif','minus2.gif','minus5.gif','plus2.gif','plus5.gif','folder_open.png','iconCheckGray.gif','line3.gif','minus3.gif','minus_ar.gif','plus3.gif','plus_ar.gif','folder.png','line1.gif','line4.gif','minus4.gif','minus.gif','plus4.gif','plus.gif','iconUnCheckAll.gif', 'blank.gif');
      var imAr = new Array(0);
      for(var i=0;i<imSrcAr.length;i++){
              imAr[imAr.length] = new Image();
              imAr[imAr.length-1].src = 'ERP5VCS_imgs/'+imSrcAr[i];
      }
    }

    function doOnLoad(){
      preLoadImages();

      tree=new dhtmlXTreeObject(document.getElementById('treebox1'),'100%%','100%%',0);
      tree.setImagePath('ERP5VCS_imgs/');
      tree.setDragHandler();
      tree.enableCheckBoxes(true);
      tree.enableThreeStateCheckboxes(true);
      tree.enableDragAndDrop(false);
      tree.loadXML('tree.xml?bt_id=%(btId)s&do_extract:int=' + do_extract, hideObject);
      tree.setOnClickHandler(showMenu);
    }

    function expandCollapse(){
      if(! is_expanded){
        tree.openAllItems(0);
        is_expanded=true;
      }else{
        tree.closeAllItems(0);
        is_expanded=false;
      }
    }

    function showNormalFiles(){
      showObject();
      is_expanded = false;
      is_showing_unmodified = 1 - is_showing_unmodified;
      tree.loadXML('tree.xml?bt_id=%(btId)s&do_extract:int=0&show_unmodified:int='+ is_showing_unmodified, hideObject);
      tree.refreshItem(0);
    }

    function commit(popup, form){
      nbModified=0;
      nbAdded=0;
      nbRemoved=0;
      FilesRemovedArray=[];
      FilesAddedArray=[];
      FilesModifiedArray=[];
      if(popup == 1){
        //hide popup
        document.getElementById('menudiv').style.display = "none";
        filesCheckedArray = [tree.getSelectedItemId()];
        filesCheckedArray=filesCheckedArray.concat(tree.getAllSubItems(filesCheckedArray[0]).split(','));
      }else{
        filesCheckedArray=tree.getAllChecked().split(',');
      }

      for(i=0;i<filesCheckedArray.length; ++i){
        if(tree.getItemColor(filesCheckedArray[i])=='red'){
          nbRemoved = nbRemoved+1;
          FilesRemovedArray[nbRemoved]=filesCheckedArray[i];
        }else{
          if(tree.getItemColor(filesCheckedArray[i])=='green'){
            nbAdded = nbAdded+1;
            FilesAddedArray[nbAdded]=filesCheckedArray[i];
          }else
          if(tree.getItemColor(filesCheckedArray[i])=='orange'){
            nbModified = nbModified+1;
            FilesModifiedArray[nbModified]=filesCheckedArray[i];
          }
        }
      }
      if(popup==1){
        filesPartiallyCheckedArray=tree.getAllParentsIds(tree.getSelectedItemId()).split(',');
      }else{
        filesPartiallyCheckedArray=tree.getAllPartiallyChecked().split(',');
      }
      for(i=0;i<filesPartiallyCheckedArray.length; ++i){
        // useless for removed directories
        if(tree.getItemColor(filesPartiallyCheckedArray[i])=='green'){
          nbAdded = nbAdded+1;
          FilesAddedArray[nbAdded]=filesPartiallyCheckedArray[i];
        }else
        if(tree.getItemColor(filesPartiallyCheckedArray[i])=='orange'){
          nbModified = nbModified+1;
          FilesModifiedArray[nbModified]=filesPartiallyCheckedArray[i];
        }
      }
      if(nbModified!==0){
        filesModified=FilesModifiedArray.join(',');
      }else{
        filesModified='none';
      }
      form.modified.value=filesModified;
      if(nbAdded!==0){
        filesAdded=FilesAddedArray.join(',');
      }else{
        filesAdded='none';
      }
      form.added.value=filesAdded;
      if(nbRemoved!==0){
        filesRemoved=FilesRemovedArray.reverse().join(',');
      }else{
        filesRemoved='none';
      }
      form.removed.value=filesRemoved;
      if (nbRemoved===0 && nbAdded===0 && nbModified===0) {
        alert('Nothing to commit !');
      } else {
        submitAction(form,'BusinessTemplate_doVcsCommit');
      }
    }


    function revert(popup,form){
      nbModified=0;
      nbAdded=0;
      nbRemoved=0;
      FilesRemovedArray=[];
      FilesAddedArray=[];
      FilesModifiedArray=[];
      if(popup == 1){
        //hide popup
        document.getElementById('menudiv').style.display = "none";
        filesCheckedArray = [tree.getSelectedItemId()];
        filesCheckedArray=filesCheckedArray.concat(tree.getAllSubItems(filesCheckedArray[0]).split(','));
      }else{
        filesCheckedArray=tree.getAllChecked().split(',');
      }
      for(i=0;i<filesCheckedArray.length; ++i){
        if(tree.getItemColor(filesCheckedArray[i])=='red'){
          nbRemoved = nbRemoved+1;
          FilesRemovedArray[nbRemoved]=filesCheckedArray[i];
        }else{
          if(tree.getItemColor(filesCheckedArray[i])=='green'){
            nbAdded = nbAdded+1;
            FilesAddedArray[nbAdded]=filesCheckedArray[i];
          }else
          if(tree.getItemColor(filesCheckedArray[i])=='orange'){
            nbModified = nbModified+1;
            FilesModifiedArray[nbModified]=filesCheckedArray[i];
          }
        }
      }
      if(nbModified!==0){
        filesModified=FilesModifiedArray.join(',');
      }else{
        filesModified='none';
      }
      form.modified.value=filesModified;
      if(nbAdded!==0){
        filesAdded=FilesAddedArray.join(',');
      }else{
        filesAdded='none';
      }
      form.added.value=filesAdded;
      if(nbRemoved!==0){
        filesRemoved=FilesRemovedArray.join(',');
      }else{
        filesRemoved='none';
      }
      form.removed.value=filesRemoved;
      if (nbRemoved===0 && nbAdded===0 && nbModified===0) {
        alert("Nothing to revert !");
      } else {
        if(confirm('Are you sure you want to revert changes?')){
          submitAction(form,'BusinessTemplate_doVcsRevert');
        }
      }
    }

    function viewDiff(popup, form){
      nbModified=0;
      nbAdded=0;
      nbRemoved=0;
      FilesRemovedArray=[];
      FilesAddedArray=[];
      FilesModifiedArray=[];
      if(popup == 1){
        //hide popup
        document.getElementById('menudiv').style.display = "none";
        filesCheckedArray = [tree.getSelectedItemId()];
        filesCheckedArray=filesCheckedArray.concat(tree.getAllSubItems(filesCheckedArray[0]).split(','));
      }else{
        filesCheckedArray=tree.getAllChecked().split(',');
      }
      for(i=0;i<filesCheckedArray.length; ++i){
        if(tree.getItemColor(filesCheckedArray[i])=='red'){
          nbRemoved = nbRemoved+1;
          FilesRemovedArray[nbRemoved]=filesCheckedArray[i];
        }else{
          if(tree.getItemColor(filesCheckedArray[i])=='green'){
            nbAdded = nbAdded+1;
            FilesAddedArray[nbAdded]=filesCheckedArray[i];
          }else
          if(tree.getItemColor(filesCheckedArray[i])=='orange'){
            nbModified = nbModified+1;
            FilesModifiedArray[nbModified]=filesCheckedArray[i];
          }
        }
      }
      if(nbModified!==0){
        filesModified=FilesModifiedArray.join(',');
      }else{
        filesModified='none';
      }
      form.modified.value=filesModified;
      if(nbAdded!==0){
        filesAdded=FilesAddedArray.join(',');
      }else{
        filesAdded='none';
      }
      form.added.value=filesAdded;
      if(nbRemoved!==0){
        filesRemoved=FilesRemovedArray.join(',');
      }else{
        filesRemoved='none';
      }
      form.removed.value=filesRemoved;
      if (nbRemoved===0 && nbAdded===0 && nbModified===0) {
        alert('Nothing to diff !');
      } else {
        submitAction(form,'BusinessTemplate_viewVcsDiff');
      }
    }

    function mouseSelect(e)
    {
      var obj = ns6 ? e.target.parentNode : event.srcElement.parentElement;
      if( isMenu )
      {
        if( overpopupmenu === false )
        {
          isMenu = false ;
          overpopupmenu = false;
          document.getElementById('menudiv').style.display = "none" ;
        }
      }
      return true;
    }

    function  showMenu()
    {
      document.getElementById('menudiv').style.left = mouseX;
      document.getElementById('menudiv').style.top = mouseY;
      document.getElementById('menudiv').style.display = "";
      document.getElementById('item1').style.backgroundColor='#FFFFFF';
      document.getElementById('item2').style.backgroundColor='#FFFFFF';
      document.getElementById('item3').style.backgroundColor='#FFFFFF';
      isMenu = true;
      return false ;
    }

    function getMouse(e)
    {
      if(overpopupmenu){
        document.body.style.cursor = 'default';
      }
      if (ns6)
      {
        mouseX = e.clientX+window.pageXOffset+'px';
        mouseY = e.clientY+window.pageYOffset+'px';
      } else
      {
        mouseX = event.clientX+document.body.scrollLeft+'px';
        mouseY = event.clientY+document.body.scrollTop+'px';
      }
      return true;
    }

    document.onmousedown  = mouseSelect;
    document.onmousemove = getMouse;

    function update(){
      open('BusinessTemplate_doVcsUpdate', '_self');
    }

    function infos(){
      open('BusinessTemplate_doVcsInfo', '_self');
    }

    function cleanup(){
      open('BusinessTemplate_doVcsCleanup', '_self');
    }

    function log(){
      //hide popup
      document.getElementById('menudiv').style.display = "none";
      open('BusinessTemplate_viewVcsLogDialog?added='+tree.getSelectedItemId(), '_self');
    }

   function treeTaller(){
     if(curHeight < 1000){
       curHeight += 100;
       document.getElementById('treebox1').style.height = curHeight+"px";
     }
   }

   function treeShorter(){
     if(curHeight > 200){
       curHeight -= 100;
       document.getElementById('treebox1').style.height = curHeight+"px";
     }
   }
'''% {'btId' : context.getId()}
