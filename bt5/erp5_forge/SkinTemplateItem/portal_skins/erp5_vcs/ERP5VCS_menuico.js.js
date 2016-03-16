  function CreateToolBarMenu(colBackground, colLight, colShadow, colFlash, style, height, width) {
    this.nb=0;
    this.colBackground=colBackground;
    this.colLight=colLight;
    this.colShadow=colShadow;
    this.colFlash=colFlash;
    this.height=height;
    this.width=width;
    this.style=style;
    this.Index=-1;
    this.NbFlash=0;
    this.Add=AddMenuToolBar;
    this.Display=DisplayToolBarMenu;
  }
  
  function AddMenuToolBar(imgOff, imgOn, text, url, js) {
    var link=new Object();
    link.imgOff=imgOff;
    link.imgOn=imgOn;
    link.text=text;
    link.url=url;
    link.js=js;
    this[this.nb]=link;
    this.nb++;
  }
  
  function DisplayToolBarMenu() {
          var Z;
          var i=0;
          if (document.getElementById || document.all) {
                  Z="<div style='text:align: center;'><table cellpadding='1' cellspacing='1' style='border:0;margin-left:auto; margin-right:auto;'><tr>";
                  for (i=0; i<this.nb; i++) {
                          Z+="<td onMouseOver='DisplayToolBarMenuOver(this,"+i+")' onMouseOut='DisplayToolBarMenuOut(this,"+i+")' onMouseDown='DisplayToolBarMenuDown(this,"+i+")' onClick='DisplayToolBarMenuClick(this,"+i+")' style='border-style:solid;border-width:1px;border-color:"+this.colBackground+";"+this.style+";cursor:pointer'><img name='MenuToolBarIMG"+i+"' src='"+this[i].imgOff+"' border=0 width="+this.width+" height="+this.height+" align=top>&nbsp;"+this[i].text+"</TD>";
                  }
                  Z+="</tr></table></div";
          } else {
                  Z="| &nbsp;";
                  for (i=0; i<this.nb; i++) {
                          Z+="<a href='"+this[i].url+"' style='"+this.style+"'><img name='MenuToolBarIMG"+i+"' src=\""+this[i].imgOff+"\" border=0 width="+this.width+" height="+this.height+" align=top>&nbsp;"+this[i].text+"</a>&nbsp;|&nbsp;";
                  }
          }
          document.write(Z);
  }
  function DisplayToolBarMenuOver(obj,ind) {
    obj.style.borderTopColor=MenuToolBar.colLight;	
    obj.style.borderLeftColor=MenuToolBar.colLight;	
    obj.style.borderBottomColor=MenuToolBar.colShadow;	
    obj.style.borderRightColor=MenuToolBar.colShadow;	
    document.images['MenuToolBarIMG'+ind].src=MenuToolBar[ind].imgOn;
  }
  
  function DisplayToolBarMenuOut(obj,ind) {
    obj.style.borderTopColor=MenuToolBar.colBackground;	
    obj.style.borderBottomColor=MenuToolBar.colBackground;	
    obj.style.borderLeftColor=MenuToolBar.colBackground;	
    obj.style.borderRightColor=MenuToolBar.colBackground;	
    document.images['MenuToolBarIMG'+ind].src=MenuToolBar[ind].imgOff;
  }
  
  
  function DisplayToolBarMenuDown(obj,ind) {
    obj.style.borderTopColor=MenuToolBar.colShadow;
    obj.style.borderLeftColor=MenuToolBar.colShadow;	
    obj.style.borderBottomColor=MenuToolBar.colLight;	
    obj.style.borderRightColor=MenuToolBar.colLight;
  }
  
  function DisplayToolBarMenuClick(obj,ind) {
    MenuToolBar.Index=ind;
    MenuToolBar.obj=obj;
    MenuToolBar.NbFlash=0;
    MenuToolBarFlash();
  }
  
  function MenuToolBarFlash() {
          MenuToolBar.NbFlash++;
          if (Math.round(MenuToolBar.NbFlash/2) != MenuToolBar.NbFlash/2) {
                  MenuToolBar.obj.style.backgroundColor=MenuToolBar.colFlash;
          } else {
                  MenuToolBar.obj.style.backgroundColor=MenuToolBar.colBackground;
          }
          if (MenuToolBar.NbFlash < 8) {
                  setTimeout('MenuToolBarFlash()',50-5*MenuToolBar.NbFlash);
          } else {
                  eval(MenuToolBar[MenuToolBar.Index].js);
                  //window.location=MenuToolBar[MenuToolBar.Index].url;
          }
  }
  
