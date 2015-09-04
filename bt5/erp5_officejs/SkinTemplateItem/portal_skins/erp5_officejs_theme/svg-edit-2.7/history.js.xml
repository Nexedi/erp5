<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.49</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>history.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgedit*/\n
/*jslint vars: true, eqeq: true, continue: true, forin: true*/\n
/**\n
 * Package: svedit.history\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) svgtransformlist.js\n
// 3) svgutils.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.history) {\n
\tsvgedit.history = {};\n
}\n
\n
// Group: Undo/Redo history management\n
svgedit.history.HistoryEventTypes = {\n
\tBEFORE_APPLY: \'before_apply\',\n
\tAFTER_APPLY: \'after_apply\',\n
\tBEFORE_UNAPPLY: \'before_unapply\',\n
\tAFTER_UNAPPLY: \'after_unapply\'\n
};\n
\n
var removedElements = {};\n
\n
/**\n
 * An interface that all command objects must implement.\n
 * @typedef svgedit.history.HistoryCommand\n
 * @type {object}\n
 *   void apply(svgedit.history.HistoryEventHandler);\n
 *   void unapply(svgedit.history.HistoryEventHandler);\n
 *   Element[] elements();\n
 *   String getText();\n
 *\n
 *   static String type();\n
 * }\n
 *\n
 * Interface: svgedit.history.HistoryEventHandler\n
 * An interface for objects that will handle history events.\n
 *\n
 * interface svgedit.history.HistoryEventHandler {\n
 *   void handleHistoryEvent(eventType, command);\n
 * }\n
 *\n
 * eventType is a string conforming to one of the HistoryEvent types.\n
 * command is an object fulfilling the HistoryCommand interface.\n
 */\n
\n
/**\n
 * @class svgedit.history.MoveElementCommand\n
 * @implements svgedit.history.HistoryCommand\n
 * History command for an element that had its DOM position changed\n
 * @param {Element} elem - The DOM element that was moved\n
 * @param {Element} oldNextSibling - The element\'s next sibling before it was moved\n
 * @param {Element} oldParent - The element\'s parent before it was moved\n
 * @param {string} [text] - An optional string visible to user related to this change\n
*/\n
svgedit.history.MoveElementCommand = function(elem, oldNextSibling, oldParent, text) {\n
\tthis.elem = elem;\n
\tthis.text = text ? ("Move " + elem.tagName + " to " + text) : ("Move " + elem.tagName);\n
\tthis.oldNextSibling = oldNextSibling;\n
\tthis.oldParent = oldParent;\n
\tthis.newNextSibling = elem.nextSibling;\n
\tthis.newParent = elem.parentNode;\n
};\n
svgedit.history.MoveElementCommand.type = function() { return \'svgedit.history.MoveElementCommand\'; };\n
svgedit.history.MoveElementCommand.prototype.type = svgedit.history.MoveElementCommand.type;\n
\n
svgedit.history.MoveElementCommand.prototype.getText = function() {\n
\treturn this.text;\n
};\n
\n
/**\n
 * Re-positions the element\n
 * @param {handleHistoryEvent: function}\n
*/\n
svgedit.history.MoveElementCommand.prototype.apply = function(handler) {\n
\t// TODO(codedread): Refactor this common event code into a base HistoryCommand class.\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_APPLY, this);\n
\t}\n
\n
\tthis.elem = this.newParent.insertBefore(this.elem, this.newNextSibling);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_APPLY, this);\n
\t}\n
};\n
\n
/**\n
 * Positions the element back to its original location\n
 * @param {handleHistoryEvent: function}\n
*/\n
svgedit.history.MoveElementCommand.prototype.unapply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_UNAPPLY, this);\n
\t}\n
\n
\tthis.elem = this.oldParent.insertBefore(this.elem, this.oldNextSibling);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_UNAPPLY, this);\n
\t}\n
};\n
\n
// Function: svgedit.history.MoveElementCommand.elements\n
// Returns array with element associated with this command\n
svgedit.history.MoveElementCommand.prototype.elements = function() {\n
\treturn [this.elem];\n
};\n
\n
\n
// Class: svgedit.history.InsertElementCommand\n
// implements svgedit.history.HistoryCommand\n
// History command for an element that was added to the DOM\n
//\n
// Parameters:\n
// elem - The newly added DOM element\n
// text - An optional string visible to user related to this change\n
svgedit.history.InsertElementCommand = function(elem, text) {\n
\tthis.elem = elem;\n
\tthis.text = text || ("Create " + elem.tagName);\n
\tthis.parent = elem.parentNode;\n
\tthis.nextSibling = this.elem.nextSibling;\n
};\n
svgedit.history.InsertElementCommand.type = function() { return \'svgedit.history.InsertElementCommand\'; };\n
svgedit.history.InsertElementCommand.prototype.type = svgedit.history.InsertElementCommand.type;\n
\n
// Function: svgedit.history.InsertElementCommand.getText\n
svgedit.history.InsertElementCommand.prototype.getText = function() {\n
\treturn this.text;\n
};\n
\n
// Function: svgedit.history.InsertElementCommand.apply\n
// Re-Inserts the new element\n
svgedit.history.InsertElementCommand.prototype.apply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_APPLY, this);\n
\t}\n
\n
\tthis.elem = this.parent.insertBefore(this.elem, this.nextSibling);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_APPLY, this);\n
\t}\n
};\n
\n
// Function: svgedit.history.InsertElementCommand.unapply\n
// Removes the element\n
svgedit.history.InsertElementCommand.prototype.unapply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_UNAPPLY, this);\n
\t}\n
\n
\tthis.parent = this.elem.parentNode;\n
\tthis.elem = this.elem.parentNode.removeChild(this.elem);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_UNAPPLY, this);\n
\t}\n
};\n
\n
// Function: svgedit.history.InsertElementCommand.elements\n
// Returns array with element associated with this command\n
svgedit.history.InsertElementCommand.prototype.elements = function() {\n
\treturn [this.elem];\n
};\n
\n
\n
// Class: svgedit.history.RemoveElementCommand\n
// implements svgedit.history.HistoryCommand\n
// History command for an element removed from the DOM\n
//\n
// Parameters:\n
// elem - The removed DOM element\n
// oldNextSibling - the DOM element\'s nextSibling when it was in the DOM\n
// oldParent - The DOM element\'s parent\n
// text - An optional string visible to user related to this change\n
svgedit.history.RemoveElementCommand = function(elem, oldNextSibling, oldParent, text) {\n
\tthis.elem = elem;\n
\tthis.text = text || ("Delete " + elem.tagName);\n
\tthis.nextSibling = oldNextSibling;\n
\tthis.parent = oldParent;\n
\n
\t// special hack for webkit: remove this element\'s entry in the svgTransformLists map\n
\tsvgedit.transformlist.removeElementFromListMap(elem);\n
};\n
svgedit.history.RemoveElementCommand.type = function() { return \'svgedit.history.RemoveElementCommand\'; };\n
svgedit.history.RemoveElementCommand.prototype.type = svgedit.history.RemoveElementCommand.type;\n
\n
// Function: svgedit.history.RemoveElementCommand.getText\n
svgedit.history.RemoveElementCommand.prototype.getText = function() {\n
\treturn this.text;\n
};\n
\n
// Function: RemoveElementCommand.apply\n
// Re-removes the new element\n
svgedit.history.RemoveElementCommand.prototype.apply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_APPLY, this);\n
\t}\n
\n
\tsvgedit.transformlist.removeElementFromListMap(this.elem);\n
\tthis.parent = this.elem.parentNode;\n
\tthis.elem = this.parent.removeChild(this.elem);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_APPLY, this);\n
\t}\n
};\n
\n
// Function: RemoveElementCommand.unapply\n
// Re-adds the new element\n
svgedit.history.RemoveElementCommand.prototype.unapply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_UNAPPLY, this);\n
\t}\n
\n
\tsvgedit.transformlist.removeElementFromListMap(this.elem);\n
\tif (this.nextSibling == null) {\n
\t\tif (window.console) {\n
            console.log(\'Error: reference element was lost\');\n
        }\n
\t}\n
\tthis.parent.insertBefore(this.elem, this.nextSibling);\n
\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_UNAPPLY, this);\n
\t}\n
};\n
\n
// Function: RemoveElementCommand.elements\n
// Returns array with element associated with this command\n
svgedit.history.RemoveElementCommand.prototype.elements = function() {\n
\treturn [this.elem];\n
};\n
\n
\n
// Class: svgedit.history.ChangeElementCommand\n
// implements svgedit.history.HistoryCommand\n
// History command to make a change to an element.\n
// Usually an attribute change, but can also be textcontent.\n
//\n
// Parameters:\n
// elem - The DOM element that was changed\n
// attrs - An object with the attributes to be changed and the values they had *before* the change\n
// text - An optional string visible to user related to this change\n
svgedit.history.ChangeElementCommand = function(elem, attrs, text) {\n
\tthis.elem = elem;\n
\tthis.text = text ? ("Change " + elem.tagName + " " + text) : ("Change " + elem.tagName);\n
\tthis.newValues = {};\n
\tthis.oldValues = attrs;\n
\tvar attr;\n
\tfor (attr in attrs) {\n
\t\tif (attr == "#text") {this.newValues[attr] = elem.textContent;}\n
\t\telse if (attr == "#href") {this.newValues[attr] = svgedit.utilities.getHref(elem);}\n
\t\telse {this.newValues[attr] = elem.getAttribute(attr);}\n
\t}\n
};\n
svgedit.history.ChangeElementCommand.type = function() { return \'svgedit.history.ChangeElementCommand\'; };\n
svgedit.history.ChangeElementCommand.prototype.type = svgedit.history.ChangeElementCommand.type;\n
\n
// Function: svgedit.history.ChangeElementCommand.getText\n
svgedit.history.ChangeElementCommand.prototype.getText = function() {\n
\treturn this.text;\n
};\n
\n
// Function: svgedit.history.ChangeElementCommand.apply\n
// Performs the stored change action\n
svgedit.history.ChangeElementCommand.prototype.apply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_APPLY, this);\n
\t}\n
\n
\tvar bChangedTransform = false;\n
\tvar attr;\n
\tfor (attr in this.newValues ) {\n
\t\tif (this.newValues[attr]) {\n
\t\t\tif (attr == "#text") {this.elem.textContent = this.newValues[attr];}\n
\t\t\telse if (attr == "#href") {svgedit.utilities.setHref(this.elem, this.newValues[attr]);}\n
\t\t\telse {this.elem.setAttribute(attr, this.newValues[attr]);}\n
\t\t}\n
\t\telse {\n
\t\t\tif (attr == "#text") {\n
\t\t\t\tthis.elem.textContent = "";\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tthis.elem.setAttribute(attr, "");\n
\t\t\t\tthis.elem.removeAttribute(attr);\n
\t\t\t}\n
\t\t}\n
\n
\t\tif (attr == "transform") { bChangedTransform = true; }\n
\t}\n
\n
\t// relocate rotational transform, if necessary\n
\tif (!bChangedTransform) {\n
\t\tvar angle = svgedit.utilities.getRotationAngle(this.elem);\n
\t\tif (angle) {\n
\t\t\t// TODO: These instances of elem either need to be declared as global\n
\t\t\t//\t\t\t\t(which would not be good for conflicts) or declare/use this.elem\n
\t\t\tvar bbox = elem.getBBox();\n
\t\t\tvar cx = bbox.x + bbox.width/2,\n
\t\t\t\tcy = bbox.y + bbox.height/2;\n
\t\t\tvar rotate = ["rotate(", angle, " ", cx, ",", cy, ")"].join(\'\');\n
\t\t\tif (rotate != elem.getAttribute("transform")) {\n
\t\t\t\telem.setAttribute("transform", rotate);\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_APPLY, this);\n
\t}\n
\n
\treturn true;\n
};\n
\n
// Function: svgedit.history.ChangeElementCommand.unapply\n
// Reverses the stored change action\n
svgedit.history.ChangeElementCommand.prototype.unapply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_UNAPPLY, this);\n
\t}\n
\n
\tvar bChangedTransform = false;\n
\tvar attr;\n
\tfor (attr in this.oldValues ) {\n
\t\tif (this.oldValues[attr]) {\n
\t\t\tif (attr == "#text") {this.elem.textContent = this.oldValues[attr];}\n
\t\t\telse if (attr == "#href") {svgedit.utilities.setHref(this.elem, this.oldValues[attr]);}\n
\t\t\telse {\n
\t\t\t\tthis.elem.setAttribute(attr, this.oldValues[attr]);\n
\t\t\t}\n
\t\t}\n
\t\telse {\n
\t\t\tif (attr == "#text") {\n
\t\t\t\tthis.elem.textContent = "";\n
\t\t\t}\n
\t\t\telse {this.elem.removeAttribute(attr);}\n
\t\t}\n
\t\tif (attr == "transform") { bChangedTransform = true; }\n
\t}\n
\t// relocate rotational transform, if necessary\n
\tif (!bChangedTransform) {\n
\t\tvar angle = svgedit.utilities.getRotationAngle(this.elem);\n
\t\tif (angle) {\n
\t\t\tvar bbox = elem.getBBox();\n
\t\t\tvar cx = bbox.x + bbox.width/2,\n
\t\t\t\tcy = bbox.y + bbox.height/2;\n
\t\t\tvar rotate = ["rotate(", angle, " ", cx, ",", cy, ")"].join(\'\');\n
\t\t\tif (rotate != elem.getAttribute("transform")) {\n
\t\t\t\telem.setAttribute("transform", rotate);\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\t// Remove transformlist to prevent confusion that causes bugs like 575.\n
\tsvgedit.transformlist.removeElementFromListMap(this.elem);\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_UNAPPLY, this);\n
\t}\n
\n
\treturn true;\n
};\n
\n
// Function: ChangeElementCommand.elements\n
// Returns array with element associated with this command\n
svgedit.history.ChangeElementCommand.prototype.elements = function() {\n
\treturn [this.elem];\n
};\n
\n
\n
// TODO: create a \'typing\' command object that tracks changes in text\n
// if a new Typing command is created and the top command on the stack is also a Typing\n
// and they both affect the same element, then collapse the two commands into one\n
\n
\n
// Class: svgedit.history.BatchCommand\n
// implements svgedit.history.HistoryCommand\n
// History command that can contain/execute multiple other commands\n
//\n
// Parameters:\n
// text - An optional string visible to user related to this change\n
svgedit.history.BatchCommand = function(text) {\n
\tthis.text = text || "Batch Command";\n
\tthis.stack = [];\n
};\n
svgedit.history.BatchCommand.type = function() { return \'svgedit.history.BatchCommand\'; };\n
svgedit.history.BatchCommand.prototype.type = svgedit.history.BatchCommand.type;\n
\n
// Function: svgedit.history.BatchCommand.getText\n
svgedit.history.BatchCommand.prototype.getText = function() {\n
\treturn this.text;\n
};\n
\n
// Function: svgedit.history.BatchCommand.apply\n
// Runs "apply" on all subcommands\n
svgedit.history.BatchCommand.prototype.apply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_APPLY, this);\n
\t}\n
\n
\tvar i,\n
\t\tlen = this.stack.length;\n
\tfor (i = 0; i < len; ++i) {\n
\t\tthis.stack[i].apply(handler);\n
\t}\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_APPLY, this);\n
\t}\n
};\n
\n
// Function: svgedit.history.BatchCommand.unapply\n
// Runs "unapply" on all subcommands\n
svgedit.history.BatchCommand.prototype.unapply = function(handler) {\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.BEFORE_UNAPPLY, this);\n
\t}\n
\n
\tvar i;\n
\tfor (i = this.stack.length-1; i >= 0; i--) {\n
\t\tthis.stack[i].unapply(handler);\n
\t}\n
\n
\tif (handler) {\n
\t\thandler.handleHistoryEvent(svgedit.history.HistoryEventTypes.AFTER_UNAPPLY, this);\n
\t}\n
};\n
\n
// Function: svgedit.history.BatchCommand.elements\n
// Iterate through all our subcommands and returns all the elements we are changing\n
svgedit.history.BatchCommand.prototype.elements = function() {\n
\tvar elems = [];\n
\tvar cmd = this.stack.length;\n
\twhile (cmd--) {\n
\t\tvar thisElems = this.stack[cmd].elements();\n
\t\tvar elem = thisElems.length;\n
\t\twhile (elem--) {\n
\t\t\tif (elems.indexOf(thisElems[elem]) == -1) {elems.push(thisElems[elem]);}\n
\t\t}\n
\t}\n
\treturn elems;\n
};\n
\n
// Function: svgedit.history.BatchCommand.addSubCommand\n
// Adds a given command to the history stack\n
//\n
// Parameters:\n
// cmd - The undo command object to add\n
svgedit.history.BatchCommand.prototype.addSubCommand = function(cmd) {\n
\tthis.stack.push(cmd);\n
};\n
\n
// Function: svgedit.history.BatchCommand.isEmpty\n
// Returns a boolean indicating whether or not the batch command is empty\n
svgedit.history.BatchCommand.prototype.isEmpty = function() {\n
\treturn this.stack.length === 0;\n
};\n
\n
\n
// Class: svgedit.history.UndoManager\n
// Parameters:\n
// historyEventHandler - an object that conforms to the HistoryEventHandler interface\n
// (see above)\n
svgedit.history.UndoManager = function(historyEventHandler) {\n
\tthis.handler_ = historyEventHandler || null;\n
\tthis.undoStackPointer = 0;\n
\tthis.undoStack = [];\n
\n
\t// this is the stack that stores the original values, the elements and\n
\t// the attribute name for begin/finish\n
\tthis.undoChangeStackPointer = -1;\n
\tthis.undoableChangeStack = [];\n
};\n
\n
// Function: svgedit.history.UndoManager.resetUndoStack\n
// Resets the undo stack, effectively clearing the undo/redo history\n
svgedit.history.UndoManager.prototype.resetUndoStack = function() {\n
\tthis.undoStack = [];\n
\tthis.undoStackPointer = 0;\n
};\n
\n
// Function: svgedit.history.UndoManager.getUndoStackSize\n
// Returns:\n
// Integer with the current size of the undo history stack\n
svgedit.history.UndoManager.prototype.getUndoStackSize = function() {\n
\treturn this.undoStackPointer;\n
};\n
\n
// Function: svgedit.history.UndoManager.getRedoStackSize\n
// Returns:\n
// Integer with the current size of the redo history stack\n
svgedit.history.UndoManager.prototype.getRedoStackSize = function() {\n
\treturn this.undoStack.length - this.undoStackPointer;\n
};\n
\n
// Function: svgedit.history.UndoManager.getNextUndoCommandText\n
// Returns:\n
// String associated with the next undo command\n
svgedit.history.UndoManager.prototype.getNextUndoCommandText = function() {\n
\treturn this.undoStackPointer > 0 ? this.undoStack[this.undoStackPointer-1].getText() : "";\n
};\n
\n
// Function: svgedit.history.UndoManager.getNextRedoCommandText\n
// Returns:\n
// String associated with the next redo command\n
svgedit.history.UndoManager.prototype.getNextRedoCommandText = function() {\n
\treturn this.undoStackPointer < this.undoStack.length ? this.undoStack[this.undoStackPointer].getText() : "";\n
};\n
\n
// Function: svgedit.history.UndoManager.undo\n
// Performs an undo step\n
svgedit.history.UndoManager.prototype.undo = function() {\n
\tif (this.undoStackPointer > 0) {\n
\t\tvar cmd = this.undoStack[--this.undoStackPointer];\n
\t\tcmd.unapply(this.handler_);\n
\t}\n
};\n
\n
// Function: svgedit.history.UndoManager.redo\n
// Performs a redo step\n
svgedit.history.UndoManager.prototype.redo = function() {\n
\tif (this.undoStackPointer < this.undoStack.length && this.undoStack.length > 0) {\n
\t\tvar cmd = this.undoStack[this.undoStackPointer++];\n
\t\tcmd.apply(this.handler_);\n
\t}\n
};\n
\n
// Function: svgedit.history.UndoManager.addCommandToHistory\n
// Adds a command object to the undo history stack\n
//\n
// Parameters:\n
// cmd - The command object to add\n
svgedit.history.UndoManager.prototype.addCommandToHistory = function(cmd) {\n
\t// FIXME: we MUST compress consecutive text changes to the same element\n
\t// (right now each keystroke is saved as a separate command that includes the\n
\t// entire text contents of the text element)\n
\t// TODO: consider limiting the history that we store here (need to do some slicing)\n
\n
\t// if our stack pointer is not at the end, then we have to remove\n
\t// all commands after the pointer and insert the new command\n
\tif (this.undoStackPointer < this.undoStack.length && this.undoStack.length > 0) {\n
\t\tthis.undoStack = this.undoStack.splice(0, this.undoStackPointer);\n
\t}\n
\tthis.undoStack.push(cmd);\n
\tthis.undoStackPointer = this.undoStack.length;\n
};\n
\n
\n
// Function: svgedit.history.UndoManager.beginUndoableChange\n
// This function tells the canvas to remember the old values of the \n
// attrName attribute for each element sent in.  The elements and values \n
// are stored on a stack, so the next call to finishUndoableChange() will \n
// pop the elements and old values off the stack, gets the current values\n
// from the DOM and uses all of these to construct the undo-able command.\n
//\n
// Parameters:\n
// attrName - The name of the attribute being changed\n
// elems - Array of DOM elements being changed\n
svgedit.history.UndoManager.prototype.beginUndoableChange = function(attrName, elems) {\n
\tvar p = ++this.undoChangeStackPointer;\n
\tvar i = elems.length;\n
\tvar oldValues = new Array(i), elements = new Array(i);\n
\twhile (i--) {\n
\t\tvar elem = elems[i];\n
\t\tif (elem == null) {continue;}\n
\t\telements[i] = elem;\n
\t\toldValues[i] = elem.getAttribute(attrName);\n
\t}\n
\tthis.undoableChangeStack[p] = {\n
\t\t\'attrName\': attrName,\n
\t\t\'oldValues\': oldValues,\n
\t\t\'elements\': elements\n
\t};\n
};\n
\n
// Function: svgedit.history.UndoManager.finishUndoableChange\n
// This function returns a BatchCommand object which summarizes the\n
// change since beginUndoableChange was called.  The command can then\n
// be added to the command history\n
//\n
// Returns:\n
// Batch command object with resulting changes\n
svgedit.history.UndoManager.prototype.finishUndoableChange = function() {\n
\tvar p = this.undoChangeStackPointer--;\n
\tvar changeset = this.undoableChangeStack[p];\n
\tvar i = changeset.elements.length;\n
\tvar attrName = changeset.attrName;\n
\tvar batchCmd = new svgedit.history.BatchCommand("Change " + attrName);\n
\twhile (i--) {\n
\t\tvar elem = changeset.elements[i];\n
\t\tif (elem == null) {continue;}\n
\t\tvar changes = {};\n
\t\tchanges[attrName] = changeset.oldValues[i];\n
\t\tif (changes[attrName] != elem.getAttribute(attrName)) {\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, changes, attrName));\n
\t\t}\n
\t}\n
\tthis.undoableChangeStack[p] = null;\n
\treturn batchCmd;\n
};\n
\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>20432</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
