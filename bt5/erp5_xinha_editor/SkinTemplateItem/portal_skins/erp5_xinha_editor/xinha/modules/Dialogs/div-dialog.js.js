
  /*--------------------------------------:noTabs=true:tabSize=2:indentSize=2:--
    --  Xinha (is not htmlArea) - http://xinha.gogo.co.nz/
    --
    --  Use of Xinha is granted by the terms of the htmlArea License (based on
    --  BSD license)  please read license.txt in this package for details.
    --
    --  Xinha was originally based on work by Mihai Bazon which is:
    --      Copyright (c) 2003-2004 dynarch.com.
    --      Copyright (c) 2002-2003 interactivetools.com, inc.
    --      This copyright notice MUST stay intact for use.
    --
    --  $HeadURL: http://svn.xinha.webfactional.com/trunk/modules/Dialogs/inline-dialog.js $
    --  $LastChangedDate: 2007-01-24 03:26:04 +1300 (Wed, 24 Jan 2007) $
    --  $LastChangedRevision: 694 $
    --  $LastChangedBy: gogo $
    --------------------------------------------------------------------------*/
 
/** The DivDialog is used as a semi-independant means of using a Plugin outside of 
 *  Xinha, it does not depend on having a Xinha editor available - not that of of course
 *  Plugins themselves may (and very likely do) require an editor.
 *
 *  @param Div into which the dialog will draw itself.
 *
 *  @param HTML for the dialog, with the special subtitutions...
 *    id="[someidhere]" will assign a unique id to the element in question
 *        and this can be retrieved with yourDialog.getElementById('someidhere')   
 *    _(Some Text Here) will localize the text, this is used for within attributes
 *    <l10n>Some Text Here</l10n> will localize the text, this is used outside attributes
 *
 *  @param A function which can take a native (english) string and return a localized version,
 *   OR;   A "context" to be used with the standard Xinha._lc() method,
 *   OR;   Null - no localization will happen, only native strings will be used.
 *
 */
   
Xinha.DivDialog = function(rootElem, html, localizer)
{
  this.id    = { };
  this.r_id  = { }; // reverse lookup id
  this.document = document;
  
  this.rootElem = rootElem;
  this.rootElem.className += ' dialog';
  this.rootElem.style.display  = 'none';
    
  this.width  =  this.rootElem.offsetWidth + 'px';
  this.height =  this.rootElem.offsetHeight + 'px';
  
  this.setLocalizer(localizer);
  this.rootElem.innerHTML = this.translateHtml(html);  
}

Xinha.extend(Xinha.DivDialog, Xinha.Dialog);

Xinha.DivDialog.prototype.show = function(values)
{  
  if(typeof values != 'undefined')
  {
    this.setValues(values);
  }
  
  this.rootElem.style.display   = '';
};

Xinha.DivDialog.prototype.hide = function()
{
  this.rootElem.style.display         = 'none';
  return this.getValues();
};
