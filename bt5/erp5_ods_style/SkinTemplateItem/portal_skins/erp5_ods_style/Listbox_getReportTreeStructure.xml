<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

structure = {}\n
structure[\'line\'] = None\n
structure[\'line_list\'] = []\n
\n
if not ((is_report_tree_mode or is_domain_tree_mode) and max_section_depth):\n
  # When this is not a report tree, return the "plain structure"\n
  structure[\'line\'] = None\n
  structure[\'line_list\'] = [dict(line=x, line_list=[]) for x in listbox_line_list]\n
  return structure\n
\n
def order_line_list(line_list, current_structure, depth=0, index=0, last_dict=None):\n
  if index < len(line_list):\n
    listbox_line = line_list[index]\n
    section_depth = listbox_line.getSectionDepth()\n
    if listbox_line.isDataLine():\n
      section_depth += 1\n
    if last_dict is None or section_depth == (depth +1):\n
      last_dict = {\'line\':listbox_line, \'line_list\':[]}\n
      current_structure[\'line_list\'].append(last_dict)\n
      index += 1\n
    elif section_depth == (depth +2):\n
      new_depth = section_depth\n
      new_structure = {\'line\':listbox_line, \'line_list\':[]}\n
      last_dict[\'line_list\'].append(new_structure)\n
      index += 1\n
      index = order_line_list(line_list, new_structure, depth=new_depth, index=index, last_dict=last_dict)\n
    elif section_depth > (depth +2):\n
      raise ValueError, "A depth is missing"\n
    else:\n
      return index\n
  if index < len(line_list):\n
    # FIXME: this way of recursing is not appropriate, as we reach very easily the maximum\n
    # recursion depth from python.\n
    index = order_line_list(line_list, current_structure, depth=depth, index=index, last_dict=last_dict)\n
  return index\n
\n
order_line_list(listbox_line_list, structure, depth=-1, index=0)\n
\n
return structure\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox_line_list=None, is_report_tree_mode=False, is_domain_tree_mode=False, max_section_depth=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Listbox_getReportTreeStructure</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
